"""Reproducible outcome assessment and separately instrumented corpus trials."""
import argparse
from collections import Counter
import hashlib
import json
from itertools import combinations
import os
from pathlib import Path
import platform
import resource
import statistics
import subprocess
import sys
from time import perf_counter_ns

from adapters import HERE, decide, verified_opa
from provenance import bundle, encode
from raw import reconstruct

REFERENCE = HERE.parents[1] / "Gap-Register-Protocol/v0.1.2-candidate"
ARMS = ("D0", "D1", "OPA")
LAYERS = ("raw", "derived")
LABELS = {"CLEAR": "NO_CONFLICT_ESTABLISHED", "INVALID": "MODEL_INVALID"}


def project(evidence):
    # PR #13's canonical wire, recreated independently of its cases/oracle module.
    order = sorted(evidence["events"], key=encode)
    return encode({"events": order, "history_closed": evidence["history_closed"],
                   "dependencies_closed": evidence["dependencies_closed"]})


def output(path, obj, compact_rows=False):
    if compact_rows:
        data = "[\n" + ",\n".join(json.dumps(row, sort_keys=True) for row in obj) + "\n]\n"
    else:
        data = json.dumps(obj, sort_keys=True, indent=2) + "\n"
    path.write_text(data, encoding="utf-8")


def outcomes(directory, opa):
    cases = json.loads((REFERENCE / "PUBLIC_CASES.json").read_text())
    assessor = {row["label"]: row for row in json.loads((REFERENCE / "RESULTS.json").read_text())["public_results"]}
    rows, equal_views, payloads = [], {}, []
    for case in cases:
        wire_bytes = project(case["evidence"])
        digest = hashlib.sha256(wire_bytes).hexdigest()
        expected = assessor[case["label"]]
        assert digest == expected["wire_sha256"]
        assert case["expected"] == expected["justified"] and case["expected_truth"] == expected["truth"]
        derived_bytes = encode(bundle(wire_bytes))
        assert reconstruct(wire_bytes) == json.loads(derived_bytes)["provenance"]
        payloads.append({"wire": wire_bytes.decode(), "derived": derived_bytes.decode()})
        replies = {}
        for arm in ARMS:
            for layer in LAYERS:
                got = decide(arm, layer, wire_bytes, derived_bytes if layer == "derived" else None, opa)
                previous = equal_views.setdefault((digest, arm, layer), got)
                assert previous == got, (arm, layer, "byte-identical view divergence")
                replies[f"{arm}/{layer}"] = got
            assert replies[f"{arm}/raw"] == replies[f"{arm}/derived"]
        if opa:
            observed = replies["OPA/derived"]
            assert observed["verdict"] == LABELS.get(case["expected"], case["expected"]), case["label"]
            assert observed["witness"] == expected["witness"], case["label"]
        rows.append({"case": case["label"], "evidence_sha256": digest,
                     "derived_sha256": hashlib.sha256(derived_bytes).hexdigest(),
                     "assessor": {k: expected[k] for k in ("justified", "truth", "premise")},
                     "responses": replies})
    counts, comparisons = {}, {}
    for arm in ARMS:
        for layer in LAYERS:
            route = f"{arm}/{layer}"
            def response(row):
                result = row["responses"][route]
                return result.get("verdict", result.get("status"))
            counts[route] = {
                "verdicts": dict(Counter(map(response, rows))),
                "matches_sr1_conditional": [sum(response(row) == LABELS.get(row["assessor"]["justified"],
                                                                         row["assessor"]["justified"])
                                                for row in rows), len(rows)] if opa or arm != "OPA" else None,
                "releases_against_justified_conflict": [row["case"] for row in rows
                    if row["assessor"]["justified"] == "CONFLICT" and response(row) == "NO_CONFLICT_ESTABLISHED"],
                "releases_against_actual_conflict": [row["case"] for row in rows
                    if row["assessor"]["truth"] == "CONFLICT" and response(row) == "NO_CONFLICT_ESTABLISHED"],
            }
    for layer in LAYERS:
        for first, second in combinations(ARMS, 2):
            comparisons[f"{layer}/{first}-{second}"] = (
                [r["case"] for r in rows if r["responses"][f"{first}/{layer}"]["verdict"] !=
                 r["responses"][f"{second}/{layer}"]["verdict"]]
                if opa or second != "OPA" else None)
    summary = {"status": "EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION",
               "public_executions": len(rows), "distinct_wire_views": len({r["evidence_sha256"] for r in rows}),
               "counts": counts, "verdict_disagreements": comparisons}
    output(directory / "RESULTS.json", rows, compact_rows=True)
    output(directory / "SUMMARY.json", summary)
    return payloads


def sample():
    """Worker measures one full corpus after decoding its transport."""
    request = json.load(sys.stdin)
    who = (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)
    cpu_before = sum(r.ru_utime + r.ru_stime for r in map(resource.getrusage, who))
    start = perf_counter_ns()
    if request["arm"] == "producer":
        for record in request["payloads"]:
            encode(bundle(record["wire"].encode()))
    else:
        for record in request["payloads"]:
            decide(request["arm"], request["layer"], record["wire"].encode(),
                   record["derived"].encode() if request["layer"] == "derived" else None,
                   request["opa"])
    elapsed = perf_counter_ns() - start
    own, child = map(resource.getrusage, who)
    print(json.dumps({"wall_ms": elapsed / 1e6, "cpu_ms": (own.ru_utime + own.ru_stime
                     + child.ru_utime + child.ru_stime - cpu_before) * 1e3, "worker_peak_kib": own.ru_maxrss,
                     "child_peak_kib": child.ru_maxrss}))


def bench(directory, payloads, opa, descriptor):
    evidence = {"environment": {"python": platform.python_version(), "platform": platform.platform(),
                                "machine": platform.machine(), "opa_version_output": descriptor,
                                "cpu_affinity": sorted(os.sched_getaffinity(0))},
                "sample": "one full corpus per fresh worker; OPA CLI startup per request included",
                "rows": {}}
    routes = [(arm, layer) for arm in ARMS for layer in LAYERS] + [("producer", "derived")]
    for arm, layer in routes:
        if arm == "OPA" and opa is None:
            evidence["rows"][f"{arm}/{layer}"] = "NOT EXECUTED"
            continue
        observations = []
        inputs = payloads if layer == "derived" and arm != "producer" else [
            {"wire": record["wire"]} for record in payloads]
        for index in range(11):
            measured = subprocess.run(
                [sys.executable, "-B", HERE / "run.py", "--worker"], check=True, capture_output=True,
                input=encode({"arm": arm, "layer": layer, "opa": str(opa) if opa else None,
                              "payloads": inputs}), timeout=180,
            )
            if index:
                observations.append(json.loads(measured.stdout))
        evidence["rows"][f"{arm}/{layer}"] = {
            field: {"median": statistics.median(values), "min": min(values), "max": max(values)}
            for field in observations[0] for values in ([row[field] for row in observations],)}
    output(directory / "MEASUREMENTS.json", evidence)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opa")
    parser.add_argument("--output", type=Path, default=HERE)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        sample()
        return
    if not __debug__:
        parser.error("run with assertions enabled")
    binary, descriptor = verified_opa(args.opa) if args.opa else (None, None)
    args.output.mkdir(parents=True, exist_ok=True)
    payloads = outcomes(args.output, binary)
    if args.benchmark:
        bench(args.output, payloads, binary, descriptor)
    print(f"PASS: {len(payloads)} public cases; OPA {'EXECUTED' if binary else 'NOT EXECUTED'}")


if __name__ == "__main__":
    main()
