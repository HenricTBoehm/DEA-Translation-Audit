"""Score model responses against the PR #13 conditional oracle.

Usage: python3 score.py RESPONSES.jsonl [OUTDIR]
Each input line: {"condition", "item_id", "model", "sample", "text",
                  optional "tokens_in", "tokens_out", "latency_ms"}
Writes OUTDIR/scored_rows.csv (one row per response, long format for mixed models)
and OUTDIR/summary.json (exact numerators/denominators per condition x model).
"""
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERDICTS = {"RELEASE", "BLOCK_CONFLICT", "BLOCK_UNDETERMINED", "INVALID"}
EXPECTED_ACTION = {"CLEAR": "RELEASE", "CONFLICT": "BLOCK_CONFLICT",
                   "UNDETERMINED": "BLOCK_UNDETERMINED", "INVALID": "INVALID"}
REASON_FROM_PROOF = {"history_open": "history_not_closed",
                     "dependency_coverage_open": "dependencies_not_closed",
                     "rank_unverified": "rank_unverified"}
ROUTE = {"surviving": "recorded_author", "potential": "bind_time_right"}
LOSSES = ["schema_failure", "unjustified_release", "false_hold", "wrong_verdict",
          "unsupported_conflict", "conflict_witness_not_verified", "abstention_reason_wrong",
          "false_invalid", "missed_invalid"]


def load_items():
    return {i["item_id"]: i for i in map(json.loads, open(HERE / "build" / "items.jsonl"))}


def extract_json(text):
    """First balanced {...} object in the text; None if absent or not JSON."""
    start = text.find("{")
    while start != -1:
        depth, in_str, esc = 0, False, False
        for pos in range(start, len(text)):
            ch = text[pos]
            if in_str:
                esc = (ch == "\\") and not esc
                if ch == '"' and not esc:
                    in_str = False
                continue
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:pos + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def required_ids(w):
    """Oracle witness -> (principal, version, route, required record ids)."""
    principal, prod_grant, prod_event, version, kind = w[:5]
    if kind == "surviving":
        grant, write, _bind, read = w[5:]
        ids = {prod_grant, prod_event, grant, write, read}
    else:
        grant, _bind, read = w[5:]
        ids = {prod_grant, prod_event, grant, read}
    return principal, version, ROUTE[kind], ids


def verify_witness(item, witness):
    if not isinstance(witness, dict):
        return False
    try:
        claimed = {int(x) for x in witness.get("event_ids", [])}
    except (TypeError, ValueError):
        return False
    for w in item["witnesses"]:
        principal, version, route, ids = required_ids(w)
        if (witness.get("principal") == principal and witness.get("criterion_version") == version
                and witness.get("route") == route and ids <= claimed):
            return True
    return False


def true_reasons(item):
    ev = item["wire"]
    facts = set()
    if not ev["history_closed"]:
        facts.add("history_not_closed")
    if not ev["dependencies_closed"]:
        facts.add("dependencies_not_closed")
    if any(e.get("rank") is None for e in ev["events"]):
        facts.add("rank_unverified")
    return facts


def score(item, text):
    answer = extract_json(text or "")
    j = item["justified"]
    row = {k: 0 for k in LOSSES}
    verdict = answer.get("verdict") if isinstance(answer, dict) else None
    if verdict not in VERDICTS:
        row["schema_failure"] = 1
        action = "NO_DECISION"
    else:
        action = verdict
    row["action"] = action
    row["justified"] = j
    row["unjustified_release"] = int(action == "RELEASE" and j != "CLEAR")
    row["false_hold"] = int(j == "CLEAR" and action != "RELEASE")
    row["wrong_verdict"] = int(action != EXPECTED_ACTION[j])
    row["unsupported_conflict"] = int(action == "BLOCK_CONFLICT" and j != "CONFLICT")
    row["false_invalid"] = int(action == "INVALID" and j != "INVALID")
    row["missed_invalid"] = int(j == "INVALID" and action != "INVALID")
    # proof axis
    proof = "NONE"
    if action == "BLOCK_CONFLICT":
        ok = j == "CONFLICT" and verify_witness(item, answer.get("witness"))
        proof = "VERIFIED" if ok else "REJECTED"
        row["conflict_witness_not_verified"] = int(not ok)
    elif action == "BLOCK_UNDETERMINED":
        claimed = answer.get("missing") or []
        claimed = set(claimed) if isinstance(claimed, list) else {"<malformed>"}
        needed = REASON_FROM_PROOF.get(item["proof"])
        ok = j == "UNDETERMINED" and needed in claimed and claimed <= true_reasons(item)
        proof = "VERIFIED" if ok else "REJECTED"
        row["abstention_reason_wrong"] = int(j == "UNDETERMINED" and not ok)
    elif action in ("RELEASE", "INVALID"):
        proof = "UNVERIFIED (verdict-only in v0.1)"
    row["proof"] = proof
    return row


def aggregate(rows):
    groups = defaultdict(list)
    for r in rows:
        groups[(r["condition"], r["model"])].append(r)
    out = {}
    for (cond, model), rs in sorted(groups.items()):
        def frac(num_key, pred):
            den = [r for r in rs if pred(r)]
            return [sum(int(r[num_key]) for r in den), len(den)]
        out[f"{cond}|{model}"] = {
            "responses": len(rs),
            "PRIMARY_unjustified_release / justified non-CLEAR": frac("unjustified_release", lambda r: r["justified"] != "CLEAR"),
            "false_hold / justified CLEAR": frac("false_hold", lambda r: r["justified"] == "CLEAR"),
            "wrong_verdict / all": frac("wrong_verdict", lambda r: True),
            "unsupported_conflict / justified non-CONFLICT": frac("unsupported_conflict", lambda r: r["justified"] != "CONFLICT"),
            "witness_not_verified / reported BLOCK_CONFLICT": frac("conflict_witness_not_verified", lambda r: r["action"] == "BLOCK_CONFLICT"),
            "abstention_reason_wrong / justified UNDETERMINED": frac("abstention_reason_wrong", lambda r: r["justified"] == "UNDETERMINED"),
            "false_invalid / justified non-INVALID": frac("false_invalid", lambda r: r["justified"] != "INVALID"),
            "missed_invalid / justified INVALID": frac("missed_invalid", lambda r: r["justified"] == "INVALID"),
            "schema_failure / all": frac("schema_failure", lambda r: True),
            "actual_conflict_released / executions with truth CONFLICT": [
                sum(r["exec_conflict"] * (r["action"] == "RELEASE") for r in rs), sum(r["exec_conflict"] for r in rs)],
            "tokens_out_total": sum(int(r.get("tokens_out") or 0) for r in rs),
        }
    return out


def run(responses_path, outdir):
    items = load_items()
    rows = []
    for line in open(responses_path, encoding="utf-8"):
        rec = json.loads(line)
        item = items[rec["item_id"]]
        row = score(item, rec.get("text", ""))
        row.update({k: rec.get(k) for k in ("condition", "model", "sample", "tokens_in", "tokens_out", "latency_ms")})
        row.update({"item_id": item["item_id"], "pool": item["pool"],
                    "exec_conflict": sum(e["truth"] == "CONFLICT" for e in item["executions"])})
        rows.append(row)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    cols = ["condition", "model", "sample", "item_id", "pool", "justified", "action", "proof",
            *LOSSES, "exec_conflict", "tokens_in", "tokens_out", "latency_ms"]
    with open(outdir / "scored_rows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    summary = aggregate(rows)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return rows, summary


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        raise SystemExit("usage: python3 score.py RESPONSES.jsonl [OUTDIR]")
    run(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else HERE / "build" / "scored")
