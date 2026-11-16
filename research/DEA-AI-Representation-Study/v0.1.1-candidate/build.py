"""Build representations, item pool, prompts and the equivalence report.

Usage: python3 build.py            (writes into build/)
Python 3.10+, standard library only. Deterministic.
"""
import hashlib
import json
import re
import sys
from collections import Counter
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor" / "pr13"))
sys.path.insert(0, str(HERE / "source"))

import spec  # noqa: E402
from cases import grant, reset, revoke, trace, wire, write  # noqa: E402
from oracle import (FIELDS, justified, ordered_completions, replay,  # noqa: E402
                    statically_possible, truth, witnesses)

OUT = HERE / "build"
CONDITIONS = ["A", "B", "C", "Cprime"]
INT_FIELDS = {"id", "time", "rank", "value"}
TOKEN = r"[A-Za-z0-9@_\-]+"
VENDOR_SHA = {
    "oracle.py": "df0a42304114a21468318a43a602ede71a05c68df33632a48b86982a5a37ce18",
    "cases.py": "5a65c4d50dceee43ea78ec3ce0a681d098c410b1f1ea32d1f4e6b899dbb26858",
    "PUBLIC_CASES.json": "3f07e797f746442ea9f4d157a15b86fbe34603afd58ed38dfd23f04c51c8ca55",
}


# ----------------------------------------------------------------- terms
def terms_for(condition):
    return spec.TERMS_CPRIME if condition == "Cprime" else spec.TERMS_C


def apply_terms(text, condition):
    table = terms_for(condition)
    return re.sub(r"\{T:([A-Za-z]+)\}", lambda m: table[m.group(1)], text)


def base_condition(condition):
    return "C" if condition == "Cprime" else condition


# ------------------------------------------------------- representations
def representation(condition):
    base = base_condition(condition)
    parts = [apply_terms(spec.PREAMBLE[base], condition), ""]
    for rid in spec.RULE_IDS:
        parts.append(f"[{rid}] " + apply_terms(spec.RULES[base][rid], condition))
        parts.append("")
    rules = "\n".join(parts).rstrip() + "\n"
    return rules, rules + "\n" + spec.COMMON_WIRE + "\n\n" + spec.ANSWER_INSTRUCTIONS + "\n"


# ------------------------------------------------------------- evidence
def encode_value(field, value):
    if value is None:
        return spec.NULL_RANK if field == "rank" else spec.NULL_PARENT
    return str(value)


def event_template(condition, kind):
    return apply_terms(spec.EVENT_TEMPLATES[base_condition(condition)][kind], condition)


def render_evidence(evidence, condition):
    base = base_condition(condition)
    yes, no = spec.BOOL_WORDS[base]
    flags = [apply_terms(t, condition).format(
        history_closed=yes if evidence["history_closed"] else no,
        dependencies_closed=yes if evidence["dependencies_closed"] else no)
        for t in spec.FLAG_TEMPLATES[base]]
    lines = [spec.EVIDENCE_HEADER[base], *flags]
    for event in sorted(evidence["events"], key=lambda e: (e["id"], json.dumps(e, sort_keys=True))):
        template = event_template(condition, event["kind"])
        lines.append(template.format(**{k: encode_value(k, v) for k, v in event.items()}))
    return "\n".join(lines) + "\n\n" + spec.USER_FOOTER + "\n"


def template_regex(template):
    pattern, pos = "", 0
    for m in re.finditer(r"\{([a-z_]+)\}", template):
        pattern += re.escape(template[pos:m.start()]) + f"(?P<{m.group(1)}>{TOKEN})"
        pos = m.end()
    return re.compile("^" + pattern + re.escape(template[pos:]) + "$")


def decode(field, raw):
    if field == "rank" and raw == spec.NULL_RANK:
        return None
    if field == "parent" and raw == spec.NULL_PARENT:
        return None
    if field in INT_FIELDS:
        return int(raw)
    return raw


def parse_evidence(text, condition):
    """Inverse of render_evidence; used only for the information-equivalence check."""
    base = base_condition(condition)
    yes, no = spec.BOOL_WORDS[base]
    lines = text.split("\n\n")[0].split("\n")[1:]
    flags = {}
    for template, line in zip(spec.FLAG_TEMPLATES[base], lines[:2]):
        m = template_regex(apply_terms(template, condition)).match(line)
        (field, raw), = m.groupdict().items()
        flags[field] = {yes: True, no: False}[raw]
    regexes = {kind: template_regex(event_template(condition, kind)) for kind in FIELDS}
    events = []
    for line in lines[2:]:
        hits = [(kind, rx.match(line)) for kind, rx in regexes.items() if rx.match(line)]
        if len(hits) != 1:
            raise ValueError(f"ambiguous or unparsable line in {condition}: {line}")
        kind, m = hits[0]
        events.append({"kind": kind, **{f: decode(f, v) for f, v in m.groupdict().items()}})
    return {**flags, "events": events}


# ---------------------------------------------------------------- items
def all_witnesses(evidence):
    if not evidence["history_closed"]:
        return []
    for order in ordered_completions(evidence["events"]):
        if not statically_possible(order):
            continue
        state = replay(order, require_root=evidence["dependencies_closed"])
        if state is not None:
            return witnesses(state)
    return []


def generated_worlds():
    """The 144 closed histories enumerated in PR #13 verify.py, unchanged."""
    for writer, channel, withdrawal, successor, selection, timing in product(
        ("ka", "kq"), ("threshold", "layout"), ("none", "revoke"),
        ("none", "layout", "threshold"), ("r@0", "r@1", "r@2"), ("before", "after")
    ):
        first, second = (3, 5) if timing == "before" else (5, 3)
        changes = [grant(1, writer, "r", channel), write(first, writer, "r@0", "r@1", channel)]
        if withdrawal == "revoke":
            changes.append(revoke(second, writer))
        if successor != "none":
            changes.append(reset(6, "r@1", "r@2", successor))
        label = f"G-{writer}-{channel}-{withdrawal}-{successor}-{selection}-{timing}"
        rows = trace(*changes, root=selection)
        yield label, {"history_closed": True, "dependencies_closed": True, "events": rows}, rows


def build_items():
    public = json.loads((HERE / "vendor" / "pr13" / "PUBLIC_CASES.json").read_text())
    pool = {}

    def add(pool_name, label, evidence, world_events):
        payload = wire(evidence)
        key = hashlib.sha256(payload).hexdigest()
        if key not in pool:
            decision = justified(json.loads(payload))
            pool[key] = {
                "item_id": f"{pool_name}-{key[:10]}", "pool": pool_name,
                "wire": json.loads(payload), "wire_sha256": key,
                "justified": decision["verdict"], "proof": decision["proof"],
                "witnesses": all_witnesses(json.loads(payload)) if decision["verdict"] == "CONFLICT" else [],
                "executions": [],
            }
        pool[key]["executions"].append({"label": label, "truth": truth({"events": world_events})})

    for case in public:
        add("P", case["label"], case["evidence"], case["world"]["events"])
    for label, evidence, rows in generated_worlds():
        add("G", label, evidence, rows)
    items = sorted(pool.values(), key=lambda i: (i["pool"], i["item_id"]))
    for item in items:
        if item["justified"] == "CONFLICT":
            assert item["witnesses"], item["item_id"]
    return items


# ------------------------------------------------------------- checks
def lint(text):
    return [w for w in spec.DEA_LEXICON if w in text]


def approx_tokens(text):
    return round(len(text) / 4)


def main():
    for name, digest in VENDOR_SHA.items():
        actual = hashlib.sha256((HERE / "vendor" / "pr13" / name).read_bytes()).hexdigest()
        assert actual == digest, f"vendored {name} does not match PR #13"
    (OUT / "representations").mkdir(parents=True, exist_ok=True)
    (OUT / "prompts").mkdir(parents=True, exist_ok=True)

    report = {"conditions": {}, "items": {}}
    systems = {}
    for cond in CONDITIONS:
        rules, system = representation(cond)
        systems[cond] = system
        (OUT / "representations" / f"{cond}.md").write_text(system, encoding="utf-8")
        tags = Counter(re.findall(r"\[(R\d+)\]", rules))
        report["conditions"][cond] = {
            "rule_tags_exactly_once": all(tags[r] == 1 for r in spec.RULE_IDS) and set(tags) == set(spec.RULE_IDS),
            "dea_lexicon_hits": lint(rules) if cond != "C" else "n/a (C is the DEA condition)",
            "rules_chars": len(rules), "rules_tokens_approx": approx_tokens(rules),
            "system_sha256": hashlib.sha256(system.encode()).hexdigest(),
        }
    suffix = spec.COMMON_WIRE + "\n\n" + spec.ANSWER_INSTRUCTIONS + "\n"
    assert all(system.endswith(suffix) for system in systems.values())
    assert set(spec.TERMS_C) == set(spec.TERMS_CPRIME)
    assert len(set(spec.TERMS_CPRIME.values())) == len(spec.TERMS_CPRIME)

    items = build_items()
    roundtrip_fail, lexicon_fail, ev_lengths = [], [], {c: [] for c in CONDITIONS}
    with open(OUT / "items.jsonl", "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, sort_keys=True) + "\n")
    for cond in CONDITIONS:
        with open(OUT / "prompts" / f"{cond}.jsonl", "w", encoding="utf-8") as f:
            for item in items:
                user = wire(item["wire"]).decode("utf-8")
                back = json.loads(user)
                if wire(back) != wire(item["wire"]):
                    roundtrip_fail.append((cond, item["item_id"]))
                if cond != "C" and lint(user):
                    lexicon_fail.append((cond, item["item_id"], lint(user)))
                ev_lengths[cond].append(len(user))
                f.write(json.dumps({"condition": cond, "item_id": item["item_id"], "pool": item["pool"],
                                    "system": systems[cond], "user": user}, sort_keys=True) + "\n")

    counts = {p: dict(Counter(i["justified"] for i in items if i["pool"] == p)) for p in ("P", "G")}
    report["items"] = {
        "distinct_views": len(items), "by_pool_and_justified_verdict": counts,
        "executions": sum(len(i["executions"]) for i in items),
        "evidence_roundtrip_failures": roundtrip_fail,
        "evidence_lexicon_failures": lexicon_fail,
        "evidence_chars_mean": {c: round(sum(v) / len(v), 1) for c, v in ev_lengths.items()},
    }
    by_condition = []
    for cond in CONDITIONS:
        with (OUT / "prompts" / f"{cond}.jsonl").open(encoding="utf-8") as entries:
            by_condition.append({r["item_id"]: r["user"] for r in map(json.loads, entries)})
    assert all(x == by_condition[0] for x in by_condition)
    rule_tokens = [report["conditions"][c]["rules_tokens_approx"] for c in CONDITIONS]
    report["rules_length_ratio_max_over_min"] = round(max(rule_tokens) / min(rule_tokens), 3)
    (OUT / "build_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    write_markdown_report(report)
    ok = (not roundtrip_fail and not lexicon_fail and
          all(v["rule_tags_exactly_once"] for v in report["conditions"].values()) and
          all(v["dea_lexicon_hits"] in ([], "n/a (C is the DEA condition)") for v in report["conditions"].values()))
    print(("PASS" if ok else "FAIL") + f": {len(items)} items x {len(CONDITIONS)} conditions; "
          f"round-trip failures {len(roundtrip_fail)}; lexicon failures {len(lexicon_fail)}; "
          f"rule length ratio {report['rules_length_ratio_max_over_min']}")
    if not ok:
        sys.exit(1)


def write_markdown_report(r):
    rows = "\n".join(
        f"| {c} | {'yes' if v['rule_tags_exactly_once'] else 'NO'} | {v['dea_lexicon_hits'] if isinstance(v['dea_lexicon_hits'], str) else (', '.join(v['dea_lexicon_hits']) or 'none')} "
        f"| {v['rules_chars']} | {v['rules_tokens_approx']} | {r['items']['evidence_chars_mean'][c]} |"
        for c, v in r["conditions"].items())
    pools = r["items"]["by_pool_and_justified_verdict"]
    text = f"""# Equivalence report (generated by build.py)

**Status:** mechanical checks only. The human derivation check (PROTOCOL §4.3, E4) is **NOT EXECUTED**.

| Condition | R1–R12 each exactly once | DEA vocabulary in rules | Rules chars | ≈ tokens | Mean evidence chars |
|---|---|---|---:|---:|---:|
{rows}

- Rule-text length ratio (max/min, ≈ tokens): **{r['rules_length_ratio_max_over_min']}** (protocol target ≤ 1.5; report as covariate either way).
- Evidence round trip (neutral JSON → parse → canonical PR #13 wire bytes): **{len(r['items']['evidence_roundtrip_failures'])} failures** over {r['items']['distinct_views']} items × 4 conditions.
- DEA vocabulary in A/B/C′ evidence renderings: **{len(r['items']['evidence_lexicon_failures'])} hits**.
- Answer instructions: byte-identical in all four system prompts (asserted).
- Item pool: {r['items']['distinct_views']} distinct evidence views ({r['items']['executions']} executions). Pool P (PR #13 public cases): {pools.get('P')}. Pool G (PR #13 generated histories): {pools.get('G')}.

All items are public. They are for calibration and pipeline testing only and carry no confirmatory weight (PROTOCOL §5).
"""
    (OUT / "EQUIVALENCE_REPORT.md").write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
