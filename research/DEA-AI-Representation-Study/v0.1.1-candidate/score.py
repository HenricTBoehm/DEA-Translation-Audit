"""Score model responses against the PR #13 conditional oracle.

Usage: python3 score.py RESPONSES.jsonl OUTDIR --schedule SCHEDULE.jsonl [--items CATALOG]
Each input line: {"condition", "item_id", "model", "sample", "text",
                  optional "tokens_in", "tokens_out", "latency_ms"}
Writes OUTDIR/scored_rows.csv (one row per response, long format for mixed models)
and OUTDIR/summary.json (exact numerators/denominators per condition x model).
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

from build import justified
from oracle import input_valid

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
          "false_invalid", "missed_invalid", "missing_response",
          "verified_justification", "correct_but_bad_justification"]


def read_jsonl(path):
    with Path(path).open(encoding="utf-8") as lines:
        return [json.loads(line) for line in lines]


def load_items(path=None):
    rows = read_jsonl(path or HERE / "build" / "items.jsonl")
    catalog = {row["item_id"]: row for row in rows}
    if len(catalog) != len(rows):
        raise ValueError("duplicate item ID")
    return catalog


def reject_duplicates(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate JSON fields")
    return result


def reject_constant(value):
    raise ValueError(f"invalid JSON constant: {value}")


def extract_json(text):
    if not isinstance(text, str):
        return None
    try:
        result = json.loads(text, object_pairs_hook=reject_duplicates,
                            parse_constant=reject_constant)
    except ValueError:
        return None
    return result if isinstance(result, dict) else None


def integer_set(values):
    if not isinstance(values, list) or any(type(value) is not int for value in values):
        return None
    return set(values) if len(set(values)) == len(values) else None


def required_ids(witness):
    principal, prod_grant, prod_event, version, kind = witness[:5]
    return principal, version, ROUTE[kind], {prod_grant, prod_event, *witness[5:]}


def path_extras(events, witness):
    reads = {event["version"]: event for event in events if event["kind"] == "read"}
    allowed = set()
    current = reads[witness[3]]
    while current["parent"] is not None:
        current = reads[current["parent"]]
        allowed.add(current["id"])
    return allowed


def witness_status(item, witness):
    if not isinstance(witness, dict):
        return "missing_witness"
    if set(witness) - {"principal", "criterion_version", "route", "event_ids", "extra_event_ids"}:
        return "invalid_witness_fields"
    claimed = integer_set(witness.get("event_ids"))
    extras = integer_set(witness.get("extra_event_ids", []))
    if claimed is None or extras is None or claimed & extras:
        return "invalid_or_repeated_ids"
    events = item["wire"]["events"]
    if not (claimed | extras) <= {event["id"] for event in events}:
        return "nonexistent_id"
    apparent = [required_ids(w) for w in item["witnesses"]]
    principals = [w for w in apparent if w[0] == witness.get("principal")]
    if not principals:
        return "wrong_principal"
    versions = [w for w in principals if w[1] == witness.get("criterion_version")]
    if not versions:
        return "wrong_version"
    routes = [w for w in versions if w[2] == witness.get("route")]
    if not routes:
        return "wrong_route"
    for w in item["witnesses"]:
        p, v, route, ids = required_ids(w)
        if (p, v, route, ids) == (witness.get("principal"), witness.get("criterion_version"),
                                 witness.get("route"), claimed):
            if extras <= path_extras(events, w):
                return "VERIFIED_OVERLOADED" if extras else "VERIFIED"
            return "irrelevant_extra"
    return "incomplete_path" if any(claimed < w[3] for w in routes) else "wrong_path_ids"


def verify_witness(item, witness):
    return witness_status(item, witness) in {"VERIFIED", "VERIFIED_OVERLOADED"}


def certificate_ok(item, action, certificate):
    if not isinstance(certificate, dict) or set(certificate) != {"code", "rows"}:
        return False
    rows = integer_set(certificate["rows"])
    wire = item["wire"]
    events = wire["events"]
    if rows is None or not rows <= set(range(len(events))):
        return False
    result = justified(wire)
    if action == "RELEASE":
        required = {i for i, event in enumerate(events) if event["kind"] in {"bind", "adjudicate"}}
        return (result["verdict"] == "CLEAR" and certificate["code"] == "coverage_replay"
                and len(required) == 2 and rows == required)
    if result["verdict"] != "INVALID" or certificate["code"] != result["proof"]:
        return False
    if result["proof"] == "authenticated_grammar":
        selected = [events[i] for i in sorted(rows)]
        if len(selected) == 1:
            return not input_valid(selected)
        if len(selected) == 2:
            left, right = selected
            return input_valid([left]) and input_valid([right]) and left["id"] == right["id"]
        return False
    return result["proof"] in {"no_closed_completion", "no_structural_completion"} and rows == set(range(len(events)))


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
    row["missing_response"] = int(text is None)
    if not isinstance(verdict, str) or verdict not in VERDICTS:
        row["schema_failure"] = int(text is not None)
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
        result = witness_status(item, answer.get("witness")) if j == "CONFLICT" else "wrong_verdict"
        ok = result in {"VERIFIED", "VERIFIED_OVERLOADED"}
        proof = result
        row["conflict_witness_not_verified"] = int(not ok)
        row["unsupported_conflict"] = int(not ok)
    elif action == "BLOCK_UNDETERMINED":
        claimed = answer.get("missing") or []
        claimed = (set(claimed) if isinstance(claimed, list) and
                   all(isinstance(reason, str) for reason in claimed) else {"<malformed>"})
        needed = REASON_FROM_PROOF.get(item["proof"])
        ok = j == "UNDETERMINED" and needed in claimed and claimed <= true_reasons(item)
        proof = "VERIFIED" if ok else "REJECTED"
        row["abstention_reason_wrong"] = int(j == "UNDETERMINED" and not ok)
    elif action in ("RELEASE", "INVALID"):
        proof = "VERIFIED" if certificate_ok(item, action, answer.get("certificate")) else "REJECTED"
    row["proof"] = proof
    row["verified_justification"] = int(not row["wrong_verdict"] and proof in {"VERIFIED", "VERIFIED_OVERLOADED"})
    row["correct_but_bad_justification"] = int(not row["wrong_verdict"] and not row["verified_justification"])
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
            "unjustified_release / justified non-CLEAR": frac("unjustified_release", lambda r: r["justified"] != "CLEAR"),
            "false_hold / justified CLEAR": frac("false_hold", lambda r: r["justified"] == "CLEAR"),
            "PRIMARY_wrong_verdict / all": frac("wrong_verdict", lambda r: True),
            "unsupported_conflict / all": frac("unsupported_conflict", lambda r: True),
            "verified_justification / all": frac("verified_justification", lambda r: True),
            "correct_but_bad_justification / all": frac("correct_but_bad_justification", lambda r: True),
            "missing_response / all": frac("missing_response", lambda r: True),
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


def run(responses_path, outdir, *, schedule_path, items_path=None):
    items = load_items(items_path)
    scheduled = read_jsonl(schedule_path)
    def key(row):
        return (row["condition"], row["model"], row["item_id"], row["sample"])

    planned = {key(row) for row in scheduled}
    if len(planned) != len(scheduled):
        raise ValueError("duplicate scheduled response")
    responses = {}
    for rec in read_jsonl(responses_path):
        tag = key(rec)
        if tag not in planned or tag in responses:
            raise ValueError("unexpected or duplicate response")
        responses[tag] = rec
    rows = []
    for planned_row in scheduled:
        rec = {**planned_row, **responses.get(key(planned_row), {})}
        item = items[rec["item_id"]]
        row = score(item, rec.get("text"))
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("responses")
    parser.add_argument("outdir")
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--items", help="assessor-owned catalog; default is public build")
    args = parser.parse_args()
    run(args.responses, args.outdir, schedule_path=args.schedule, items_path=args.items)
