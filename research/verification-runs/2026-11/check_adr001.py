"""Independently replay ADR-001's JSON fixtures and probe adversarial boundaries."""
import itertools
import json
import sys
from pathlib import Path

ADR = Path(__file__).resolve().parents[2] / "ADR-001"
sys.path.insert(0, str(ADR))
import adr001_ctrl as archived


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def journeys(edges, times, source, target, semantics):
    """Enumerate simple vertex paths and choose one timestamp per edge."""
    if source == target:
        return True
    intermediate = sorted({v for edge in edges for v in edge} - {source, target})
    for length in range(len(intermediate) + 1):
        for middle in itertools.permutations(intermediate, length):
            route = (source, *middle, target)
            choices = [edges.get(edge, set()) & times for edge in zip(route, route[1:])]
            for schedule in itertools.product(*choices):
                if semantics == "A" and len(set(schedule)) == 1:
                    return True
                if semantics == "B":
                    return True
                if semantics == "C" and tuple(sorted(schedule)) == schedule:
                    return True
    return False


def reset_journey(edges, times, source, target, resets, *, reset_first=True):
    """Search a time-expanded graph with control arcs and persistence arcs."""
    clock = sorted(times)
    if not clock:
        return source == target
    pending = [(source, index) for index in range(len(clock))]
    visited = set()
    while pending:
        node, index = pending.pop()
        if (node, index) in visited:
            continue
        visited.add((node, index))
        tick = clock[index]
        if node == target and index == len(clock) - 1:
            if reset_first or node == source or tick not in resets.get(node, ()):
                return True
        for (origin, destination), active in edges.items():
            if origin == node and tick in active:
                pending.append((destination, index))
        if index + 1 < len(clock):
            cut = clock[index + int(reset_first)]
            if node == source or cut not in resets.get(node, ()):
                pending.append((node, index + 1))
    return False


def comparison_cases():
    fixture = json.loads((ADR / "adr001-regression-cases.json").read_bytes())
    reference = json.loads((ADR / "results/adr001-results.json").read_bytes())
    actual = archived.run_cms()
    check(actual == reference["countermodels"], "archived named results differ")
    check(archived.relay_properties() == reference["relay_properties"], "relay matrix differs")
    check(archived.nontransitivity_witness() == reference["nontransitivity_C"], "nontransitivity differs")
    check({case["id"] for case in fixture["cases"]} == set(actual) and len(actual) == 11, "fixture coverage")
    comparisons = 0
    for case in fixture["cases"]:
        name = case["id"]
        stage_e, stage_j = set(case["theta_E"]), set(case["theta_J"])
        execute, seal, assign = (case[key] for key in ("t_exec", "seal", "t_adj"))
        check(execute in stage_e and assign in stage_j and execute <= seal <= assign, name)
        edges = {tuple(edge.split("->")): set(times) for edge, times in case["edges"].items()}
        resets = case["recorded_resets"]
        windows = {
            "stage": (stage_e, stage_j),
            "act": ({t for t in stage_e if t <= execute}, {t for t in stage_j if t <= assign}),
            "causal": (set(range(min(stage_e), seal + 1)), set(range(min(stage_e), assign + 1))),
        }
        nodes = sorted({v for edge in edges for v in edge} | {"p", "o", "a", "j"})
        configurations = [(s, a) for s in ("A", "B", "C") for a in windows]
        if resets:
            configurations.append(("CR", "causal"))
        for sem, anchor in configurations:
            def reaches(src, dst, times):
                if sem == "CR":
                    return reset_journey(edges, times, src, dst, resets)
                return journeys(edges, times, src, dst, sem)

            production, decision = windows[anchor]
            witnesses = [
                node for node in nodes
                if reaches(node, case["executor"], production)
                and reaches(node, case["adjudicator"], decision)
            ]
            row = {"ExecConflict": bool(witnesses), "j_may_adjudicate": not witnesses,
                   "common_controllers": witnesses}
            check(row == actual[name][f"{sem}/{anchor}"], (name, sem, anchor, row))
            comparisons += 1
        selected = actual[name]["CR/causal" if resets else "C/causal"]
        check(selected["ExecConflict"] == case["expected_ExecConflict"], name)
        check(selected["j_may_adjudicate"] == case["expected_j_may_adjudicate_on_control_grounds"], name)
    return comparisons


def adversarial_cases():
    # Invalid chronology is accepted. The producer can be attributed after the decision.
    late = archived.M({"p->a": {3}, "p->j": {2}}, tE=1, sigma=3, tJ=2)
    check(archived.conflict(late, "C", "causal") == (True, ["p"]), "post-decision producer edge")
    early = archived.M({"p->j": {2}}, tE=1, sigma=3, tJ=2)
    check(archived.conflict(early, "C", "causal") == (False, []), "edge deletion isolates late edge")
    invalid = sum(m["sigma"] > m["tJ"] for m in archived.mc_random(20000))
    check(invalid > 0, "expected invalid chronology in archived random generator")

    times = {2, 3}
    relay = {("p", "o"): {2}, ("o", "j"): {3}}
    check(not reset_journey(relay, times, "p", "j", {"o": {3}}), "CM8 reset-first")
    check(reset_journey(relay, times, "p", "j", {"o": {3}}, reset_first=False), "CM8 reset-last")
    check(reset_journey({**relay, ("p", "o"): {2, 3}}, times, "p", "j", {"o": {3}}),
          "same-instant reacquisition defeats reset")
    check(reset_journey({("p", "o"): {2}, ("o", "j"): {2}}, times, "p", "j", {"o": {3}}),
          "intermediate reset does not retract downstream effects")
    # A terminal reset clears the terminal row although the ADR text names intermediates.
    terminal = reset_journey({("p", "j"): {2}}, times, "p", "j", {"j": {3}})
    check(terminal is False and archived.ctrl_set(
        archived.M({"p->j": {2}}), "p", times, "CR", {"j": {3}}
    ) == {"p"}, "reset of destination")
    # A temporal cycle need not give its members equal reachability rows.
    cycle = {("p", "j"): {2}, ("p", "o"): {2}, ("o", "p"): {3}}
    check(journeys(cycle, times, "p", "o", "C") and journeys(cycle, times, "o", "p", "C")
          and journeys(cycle, times, "p", "j", "C") and not journeys(cycle, times, "o", "j", "C"),
          "mutual temporal reachability does not imply equal rows")
    return invalid


if __name__ == "__main__":
    rows = comparison_cases()
    invalid_chronology = adversarial_cases()
    print(f"PASS: 11 independent fixtures, {rows} decisions and witness sets")
    print(f"CONFIRMED: {invalid_chronology}/20000 archived random models seal after adjudication")
