"""Pipeline self-test with synthetic responders (no language model involved).

Checks that score.py rewards the oracle-ideal responder and penalises the
mandatory negative controls exactly as specified in PROTOCOL §6.
Usage: python3 selftest.py   (after build.py)
"""
import json
import tempfile
from pathlib import Path

import score

HERE = Path(__file__).resolve().parent
ROUTE = {"surviving": "recorded_author", "potential": "bind_time_right"}


def ideal(item):
    j = item["justified"]
    ans = {"verdict": score.EXPECTED_ACTION[j], "witness": None, "missing": [], "justification": "oracle"}
    if j == "CONFLICT":
        principal, version, route, ids = score.required_ids(item["witnesses"][0])
        ans["witness"] = {"principal": principal, "criterion_version": version,
                          "route": route, "event_ids": sorted(ids)}
    if j in {"CLEAR", "INVALID"}:
        ans["certificate"] = ideal_certificate(item)
    if j == "UNDETERMINED":
        ans["missing"] = sorted(score.true_reasons(item))
    return ans


def ideal_certificate(item):
    events = item["wire"]["events"]
    if item["justified"] == "CLEAR":
        return {"code": "coverage_replay", "rows": [i for i, event in enumerate(events)
                                                    if event["kind"] in {"bind", "adjudicate"}]}
    code = item["proof"]
    if code == "authenticated_grammar":
        for i, event in enumerate(events):
            if not score.input_valid([event]):
                return {"code": code, "rows": [i]}
        for i, left in enumerate(events):
            for j, right in enumerate(events[i+1:], i+1):
                if left["id"] == right["id"]:
                    return {"code": code, "rows": [i, j]}
        raise AssertionError("missing grammar counterexample")
    return {"code": code, "rows": list(range(len(events)))}


def wrong_route(item):
    ans = ideal(item)
    if ans["witness"]:
        ans["witness"]["route"] = {"recorded_author": "bind_time_right",
                                   "bind_time_right": "recorded_author"}[ans["witness"]["route"]]
    return ans


RESPONDERS = {
    "ideal": ideal,
    "always_release": lambda i: {"verdict": "RELEASE", "witness": None, "missing": []},
    "always_hold": lambda i: {"verdict": "BLOCK_UNDETERMINED", "witness": None, "missing": []},
    "always_invalid": lambda i: {"verdict": "INVALID", "witness": None, "missing": []},
    "proofless_conflict": lambda i: {"verdict": "BLOCK_CONFLICT", "witness": None, "missing": []},
    "wrong_route": wrong_route,
    "garbage": None,
}


def main():
    items = score.load_items()
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "responses.jsonl"
        with open(path, "w") as f:
            for name, fn in RESPONDERS.items():
                for item in items.values():
                    text = "I cannot decide." if fn is None else json.dumps(fn(item))
                    f.write(json.dumps({"condition": "SELFTEST", "item_id": item["item_id"],
                                        "model": name, "sample": 0, "text": text}) + "\n")
        schedule = Path(tmp) / "schedule.jsonl"
        expected = score.read_jsonl(path)
        expected.append({**expected[0], "model": "missing"})
        schedule.write_text("".join(json.dumps({k: r[k] for k in ("condition", "model", "item_id", "sample")})
                                    + "\n" for r in expected), encoding="utf-8")
        _, s = score.run(path, HERE / "build" / "selftest", schedule_path=schedule)
    n = len(items)
    count = lambda v: sum(i["justified"] == v for i in items.values())
    clear, conflict, invalid, undet = (count(v) for v in ("CLEAR", "CONFLICT", "INVALID", "UNDETERMINED"))
    g = lambda m, k: s[f"SELFTEST|{m}"][k]
    P = "unjustified_release / justified non-CLEAR"
    assert g("ideal", "PRIMARY_wrong_verdict / all") == [0, n]
    assert g("ideal", P) == [0, n - clear]
    assert g("ideal", "witness_not_verified / reported BLOCK_CONFLICT") == [0, conflict]
    assert g("ideal", "abstention_reason_wrong / justified UNDETERMINED") == [0, undet]
    assert g("always_release", P) == [n - clear, n - clear]
    assert g("always_hold", "false_hold / justified CLEAR") == [clear, clear]
    assert g("always_hold", "abstention_reason_wrong / justified UNDETERMINED") == [undet, undet]
    assert g("always_invalid", "false_invalid / justified non-INVALID") == [n - invalid, n - invalid]
    assert g("proofless_conflict", "witness_not_verified / reported BLOCK_CONFLICT") == [n, n]
    assert g("proofless_conflict", "unsupported_conflict / all") == [n, n]
    assert g("wrong_route", "witness_not_verified / reported BLOCK_CONFLICT") == [conflict, conflict]
    assert g("wrong_route", "PRIMARY_wrong_verdict / all") == [0, n]
    assert g("garbage", "schema_failure / all") == [n, n]
    assert g("garbage", "false_hold / justified CLEAR") == [clear, clear]
    assert g("ideal", "verified_justification / all") == [n, n]
    assert g("missing", "missing_response / all") == [1, 1]
    assert g("missing", "PRIMARY_wrong_verdict / all") == [1, 1]
    for item in items.values():
        ans = ideal(item)
        if item["justified"] in {"CLEAR", "INVALID"}:
            ans["certificate"]["rows"].append(999)
            result = score.score(item, json.dumps(ans))
            assert not result["wrong_verdict"] and result["correct_but_bad_justification"]
        if item["justified"] == "CONFLICT":
            ans["witness"]["event_ids"].append(999)
            assert score.score(item, json.dumps(ans))["proof"] == "nonexistent_id"
            ans = ideal(item)
            ans["witness"]["event_ids"].pop()
            assert score.score(item, json.dumps(ans))["proof"] == "incomplete_path"
    print(f"PASS: scoring self-test, {len(RESPONDERS)} synthetic responders x {n} items "
          f"(CLEAR {clear}, CONFLICT {conflict}, UNDETERMINED {undet}, INVALID {invalid})")


if __name__ == "__main__":
    main()
