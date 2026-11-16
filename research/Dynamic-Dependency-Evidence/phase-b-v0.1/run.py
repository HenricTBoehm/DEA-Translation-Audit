"""Execute public scenarios, collect independent observations, and assess separately."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import select
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import perf_counter_ns

from acquisition import candidate, combine, e1, e2
from observe import Watch, descriptor
from scenarios import SCENARIOS, fixture, pack

HERE = Path(__file__).resolve().parent
PHASE_A = HERE.parents[1] / "Minimal-Differential-Harness/phase-a-v0.1"
sys.path.insert(0, str(PHASE_A))
from adapters import decide, verified_opa
from provenance import bundle, encode


def snapshots(directory, registry):
    values = {}
    for name, entry in registry.items():
        path = directory / name
        stat = path.stat()
        content = path.read_bytes()
        assert hashlib.sha256(content).hexdigest() == entry["sha256"]
        assert json.loads(content) == entry["value"] and stat.st_mode & 0o222 == 0
        values[name] = (stat.st_dev, stat.st_ino, stat.st_size)
    return values


def measured(label, function, marks):
    start = perf_counter_ns()
    value = function()
    marks[label] = (perf_counter_ns() - start) / 1e6
    return value


def execute(directory, configs, registry, replacement, marks):
    sealed = snapshots(directory, registry)
    watch = Watch(directory)
    before = after = None
    epochs = []
    start = perf_counter_ns()
    try:
        with subprocess.Popen([sys.executable, "-I", "-B", HERE / "evaluate.py",
                               directory, json.dumps(configs)], stdin=subprocess.PIPE,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                              bufsize=0) as process:
            try:
                for checkpoint in ("planned", "threshold_open", "consumed"):
                    if not select.select([process.stderr], [], [], 5)[0]:
                        raise TimeoutError(f"checkpoint {checkpoint}")
                    received = process.stderr.readline().decode().strip()
                    if received != checkpoint:
                        raise ValueError(f"unexpected checkpoint: {received}")
                    epochs.append(watch.drain())
                    if checkpoint == "planned" and replacement is not None:
                        staged = directory / "binding.tmp"
                        staged.write_bytes(replacement)
                        staged.replace(directory / "binding.json")
                    if checkpoint in ("threshold_open", "consumed"):
                        try:
                            sample = descriptor(process.pid, directory)
                        except (OSError, ValueError):
                            sample = None
                        if checkpoint == "threshold_open":
                            before = sample
                        else:
                            after = sample
                    process.stdin.write(b"continue\n")
                output, claims = process.communicate(timeout=5)
                if process.returncode:
                    raise RuntimeError(claims.decode())
                epochs.append(watch.drain())
            except BaseException:
                process.kill()
                raise
    finally:
        watch.close()
    marks["evaluator_and_capture"] = (perf_counter_ns() - start) / 1e6
    assert sealed == snapshots(directory, registry)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    marks["child_process_cumulative_peak_kib"] = usage.ru_maxrss
    stdout = json.loads(output)
    # Assessor uses the actual child FD, retained immutable manifests and a separate arithmetic test.
    confirmed = before is not None and after is not None and before["file"] == after["file"]
    if confirmed:
        name = after["file"]
        confirmed = (before["offset"] == 0 and after["offset"] == after["size"]
                     and (after["dev"], after["inode"], after["size"]) == sealed[name]
                     and (before["dev"], before["inode"], before["size"]) == sealed[name])
    if confirmed:
        threshold = registry[after["file"]]["value"]["threshold"]
        score = registry[configs["score"]]["value"]["score"]
        # Independent finite truth table for the permitted domains.
        independently_predicted = threshold == 0 or score in (1, 2, 3)
        reference = {"fd_full_read": True, "read": after["file"],
                     "fd_offsets": [before["offset"], after["offset"]],
                     "output_consistent": stdout["accept"] == independently_predicted}
        assert reference["output_consistent"]
    else:
        reference = {"fd_full_read": False, "status": "NOT VERIFIED"}
    return stdout, json.loads(claims), epochs, reference


def phase_a(projection, opa):
    wire = projection["wire"]
    if wire is None:
        # Explicit experimental evidence-level contradiction, not an invented lifecycle event.
        wire_bytes = b"{}"
        derived = {"wire_sha256": hashlib.sha256(wire_bytes).hexdigest(),
                   "provenance": {"event_check": "contradiction", "event_reason": projection["reason"]}}
    else:
        order = sorted(wire["events"], key=encode)
        wire_bytes = encode({**wire, "events": order})
        derived = bundle(wire_bytes)
    results = {arm: decide(arm, "derived", wire_bytes, encode(derived), opa) for arm in ("D0", "D1", "OPA")}
    return derived["provenance"], results, hashlib.sha256(wire_bytes).hexdigest()


def relation(observed, registry, control, facts):
    """Explicit research extension: role/rights separate from observed binding."""
    if facts["event_check"] != "settled" or "read" not in observed:
        return None
    version = registry[observed["read"]]["value"]["version"]
    producer = facts["producer"]["principal"]
    rights = [r["channel"] for r in facts["rights"] if r["principal"] == producer and r["target"] == "r"]
    values = {entry["value"]["threshold"] for entry in registry.values()
              if entry["role"] in control["allowed_thresholds"]}
    prior = facts["versions"][version]["fields"]["threshold"]["origin"]
    return {"threshold_successor": "threshold" in rights,
            "cosmetic_successor": "layout" in rights,
            "resolver_selection": producer in control["selector_owners"],
            "material_selection_hypothesis": len(values) > 1 and producer in control["selector_owners"],
            "observed_bound_version": version,
            "surviving_material_effect": bool(prior and prior["principal"] == producer),
            "policy_control": producer in control["policy_owners"]}


def ground_control(control, used, registry):
    """Independent backward query on controller history, not a policy or provenance export."""
    state = "r@0"
    active = False
    cosmetic = False
    threshold_source = False
    history = control["history"]
    version = registry[used]["value"]["version"]
    for row in reversed(history):
        if row["kind"] in ("reset", "modify") and row["version"] == version:
            if row["channel"] == "threshold":
                threshold_source = row["kind"] == "modify" and row["key"] == "ka"
                break
            version = row["base"]
    if not any(r["kind"] == "revoke" and r["subject"] == "ka" for r in history):
        active = any(r["kind"] == "grant" and r["subject"] == "ka" and r["target"] == "r"
                     and r["channel"] == "threshold" for r in history)
        cosmetic = any(r["kind"] == "grant" and r["subject"] == "ka" and r["target"] == "r"
                       and r["channel"] == "layout" for r in history)
    for row in history:
        if row["kind"] in ("modify", "reset"):
            state = row["version"]
    selector = "p" in control["selector_owners"]
    values = {d["value"]["threshold"] for d in registry.values() if d["role"] in control["allowed_thresholds"]}
    return {"threshold_successor": active, "cosmetic_successor": cosmetic, "resolver_selection": selector,
            "surviving_material_effect": threshold_source, "policy_control": "p" in control["policy_owners"],
            "material_selection_hypothesis": selector and len(values) > 1,
            "sr1_material_conflict": threshold_source or (active and state == registry[used]["value"]["version"]
                                                           and not state.endswith("@2"))}


def run(opa):
    reports, costs = [], {}
    for name in SCENARIOS:
        marks = {}
        with TemporaryDirectory(prefix="phase-b-") as tmp:
            directory = Path(tmp).resolve()
            registry, configs, control, plan, replacement = fixture(directory, name)
            stdout, claims, epochs, reference = execute(directory, configs, registry, replacement, marks)
            first = measured("e1_normalization", lambda: e1(claims, registry), marks)
            second = measured("e2_normalization", lambda: e2(epochs, registry), marks)
            fusion, conflicts = combine(first, second)
            profiles = {}
            if reference["fd_full_read"]:
                used = reference["read"]
                reference["version"] = registry[used]["value"]["version"]
                reference["control"] = ground_control(control, used, registry)
                reference["bind_mismatch"] = plan["binding_before"] != reference["version"]
            for label, observed in (("E1", first), ("E2", second), ("combined", fusion)):
                projection = ({"state": "contradiction", "wire": None,
                               "reason": "inconsistent_runtime_attestations"}
                              if label == "combined" and conflicts else candidate(observed, registry, control))
                facts, judgments, wire_fingerprint = measured(
                    f"{label}_mapping_and_decision", lambda: phase_a(projection, opa), marks)
                profiles[label] = {"observed": observed, "projection": projection["state"],
                                   "phase_a_event_check": facts["event_check"],
                                   "reason": facts["event_reason"], "wire_sha256": wire_fingerprint,
                                   "decisions": judgments, "relations": relation(observed, registry, control, facts)}
            reports.append({"name": name, "intervention": plan, "controller": control,
                            "artifact_manifest": registry, "actual_output": stdout, "reference": reference,
                            "app_claims": claims, "kernel_events": epochs, "cross_source_conflicts": conflicts,
                            "profiles": profiles})
            costs[name] = marks
    return reports, costs


def summary(rows):
    result = {}
    for p in ("E1", "E2", "combined"):
        c = Counter()
        releases = Counter()
        for row in rows:
            ref, profile = row["reference"], row["profiles"][p]
            if not ref["fd_full_read"]:
                continue
            c["fd_verified_attempts"] += 1
            observed = profile["observed"].get("read")
            c["threshold_reports"] += observed is not None
            c["correct_threshold_reports"] += observed == ref["read"]
            c["wrong_threshold_reports"] += observed is not None and observed != ref["read"]
            c["omitted_threshold_reports"] += observed is None
            c["score_policy_resolver_read_reported"] += len(profile["observed"]) == 5
            c["incomplete_runtime"] += profile["projection"] == "incomplete"
            c["integrity_contradictions"] += profile["phase_a_event_check"] == "contradiction"
            status = profile["decisions"]["OPA"].get("verdict")
            c["unknown_on_incomplete"] += profile["projection"] == "incomplete" and status == "UNDETERMINED"
            c["coverage_claims"] += profile["projection"] == "projected"
            c["coverage_with_wrong_read"] += profile["projection"] == "projected" and observed != ref["read"]
            truth = ref["control"]
            rel = profile["relations"]
            for relation_name in ("threshold_successor", "resolver_selection", "surviving_material_effect"):
                c[f"{relation_name}_reference_positive"] += truth[relation_name]
                if rel is None:
                    c[f"{relation_name}_unknown"] += 1
                else:
                    category = ("true_positive" if truth[relation_name] else "false_positive") if rel[relation_name] else (
                        "false_negative" if truth[relation_name] else "true_negative")
                    c[f"{relation_name}_{category}"] += 1
            valid = not ref["bind_mismatch"]
            c["actual_sr1_conflict_valid"] += valid and truth["sr1_material_conflict"]
            for arm, decision in profile["decisions"].items():
                if decision.get("verdict") == "NO_CONFLICT_ESTABLISHED":
                    releases[f"{arm}_releases"] += 1
                    releases[f"{arm}_actual_conflict_release"] += valid and truth["sr1_material_conflict"]
                    if status is not None:
                        releases[f"{arm}_release_against_accepted_sr1_conflict"] += status == "CONFLICT"
        result[p] = {"counts": dict(c), "release_counts": dict(releases)}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--opa")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    opa = verified_opa(args.opa)[0] if args.opa else None
    args.out.mkdir(parents=True, exist_ok=True)
    rows, costs = run(opa)
    report = {"status": "EXPLORATORY – NOT SCORED – NOT FREEZE VALIDATION",
              "opa": "EXECUTED" if opa else "NOT EXECUTED", "attempts": rows, "counts": summary(rows)}
    # Compact each attempt individually so the public report remains diffable.
    rendered = json.dumps({k: v for k, v in report.items() if k != "attempts"}, sort_keys=True, indent=2)
    attempts = ",\n".join("    " + json.dumps(row, sort_keys=True) for row in rows)
    (args.out / "RESULTS.json").write_text(
        rendered[:-2] + ',\n  "attempts": [\n' + attempts + "\n  ]\n}\n", encoding="utf-8")
    (args.out / "MEASUREMENTS.json").write_bytes(pack(costs))
    print(f"PASS: {len(rows)} real evaluations; {sum(r['reference']['fd_full_read'] for r in rows)} independent FD confirmations; OPA {report['opa']}")


if __name__ == "__main__":
    main()
