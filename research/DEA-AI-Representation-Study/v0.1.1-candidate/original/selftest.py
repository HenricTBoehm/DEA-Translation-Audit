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
    if j == "UNDETERMINED":
        ans["missing"] = sorted(score.true_reasons(item))
    return ans


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
                    text = "I cannot decide." if fn is None else "Answer:\n" + json.dumps(fn(item))
                    f.write(json.dumps({"condition": "SELFTEST", "item_id": item["item_id"],
                                        "model": name, "sample": 0, "text": text}) + "\n")
        _, s = score.run(path, HERE / "build" / "selftest")
    n = len(items)
    count = lambda v: sum(i["justified"] == v for i in items.values())
    clear, conflict, invalid, undet = (count(v) for v in ("CLEAR", "CONFLICT", "INVALID", "UNDETERMINED"))
    g = lambda m, k: s[f"SELFTEST|{m}"][k]
    P = "PRIMARY_unjustified_release / justified non-CLEAR"
    assert g("ideal", "wrong_verdict / all") == [0, n]
    assert g("ideal", P) == [0, n - clear]
    assert g("ideal", "witness_not_verified / reported BLOCK_CONFLICT") == [0, conflict]
    assert g("ideal", "abstention_reason_wrong / justified UNDETERMINED") == [0, undet]
    assert g("always_release", P) == [n - clear, n - clear]
    assert g("always_hold", "false_hold / justified CLEAR") == [clear, clear]
    assert g("always_hold", "abstention_reason_wrong / justified UNDETERMINED") == [undet, undet]
    assert g("always_invalid", "false_invalid / justified non-INVALID") == [n - invalid, n - invalid]
    assert g("proofless_conflict", "witness_not_verified / reported BLOCK_CONFLICT") == [n, n]
    assert g("proofless_conflict", "unsupported_conflict / justified non-CONFLICT") == [n - conflict, n - conflict]
    assert g("wrong_route", "witness_not_verified / reported BLOCK_CONFLICT") == [conflict, conflict]
    assert g("wrong_route", "wrong_verdict / all") == [0, n]
    assert g("garbage", "schema_failure / all") == [n, n]
    assert g("garbage", "false_hold / justified CLEAR") == [clear, clear]
    print(f"PASS: scoring self-test, {len(RESPONDERS)} synthetic responders x {n} items "
          f"(CLEAR {clear}, CONFLICT {conflict}, UNDETERMINED {undet}, INVALID {invalid})")


if __name__ == "__main__":
    main()
