"""Non-normative PB-3/PB-3v fixture with artifact-specific stages and control evidence."""
import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from adr001_ctrl import ctrl_set
from poblete_adr001_check import READINGS

CLOCK = frozenset(range(4))
HUMAN = "human"  # Two workflow roles mapped to one principal in this hypothetical fixture.
AGENT = "engineering-agent"


@dataclass(frozen=True)
class Transition:
    artifact: str
    producer: str
    production_stage: frozenset[int]
    produced_at: int
    sealed_at: int
    adjudicator: str
    adjudication_stage: frozenset[int]
    adjudicated_at: int
    record_start: int
    input_artifact: "Transition | None" = None

    def __post_init__(self):
        if not (
            self.production_stage <= CLOCK
            and self.adjudication_stage <= CLOCK
            and self.produced_at in self.production_stage
            and self.adjudicated_at in self.adjudication_stage
            and self.record_start in CLOCK
            and self.sealed_at in CLOCK
            and self.record_start <= min(self.production_stage)
            and self.produced_at <= self.sealed_at <= self.adjudicated_at
        ):
            raise ValueError(f"{self.artifact}: invalid stage or event order")
        if self.input_artifact is not None and (
            self.input_artifact.artifact == self.artifact
            or self.input_artifact.sealed_at >= self.produced_at
        ):
            raise ValueError(f"{self.artifact}: expected a distinct previously sealed input")


@dataclass(frozen=True)
class ControlRecord:
    edges: dict[str, frozenset[int]]
    complete: bool  # Attests completeness of relevant authenticated edges and transition events.


def classify(transition: Transition, record: ControlRecord):
    principals = {transition.producer, transition.adjudicator}
    for edge, times in record.edges.items():
        source, target = edge.split("->")
        if not source or not target or not times <= CLOCK:
            raise ValueError(f"invalid control evidence: {edge}")
        principals.update((source, target))
    production = range(transition.record_start, transition.sealed_at + 1)
    decision = range(transition.record_start, transition.adjudicated_at + 1)
    model = {"edges": record.edges}
    witnesses = [
        p for p in sorted(principals)
        if transition.producer in ctrl_set(model, p, production, "C")
        and transition.adjudicator in ctrl_set(model, p, decision, "C")
    ]
    if witnesses:
        outcome = "CONFLICT"
    elif record.complete:
        outcome = "NO_CONFLICT_ESTABLISHED"
    else:
        outcome = "UNDETERMINED"
    return {"outcome": outcome, "witness_principals": witnesses, "record_complete": record.complete,
            "passes_control_gate": outcome == "NO_CONFLICT_ESTABLISHED"}


def verify(actual, expected):
    if actual != expected:
        raise AssertionError(f"expected {expected!r}, got {actual!r}")


def reject(factory):
    try:
        factory()
    except ValueError:
        return
    raise AssertionError("invalid transition accepted")


def run():
    execution = Transition("execution-output", AGENT, frozenset({0, 1}), 1, 1,
                           HUMAN, frozenset({3}), 3, 0)
    report = Transition("verification-report", AGENT, frozenset({2}), 2, 2,
                        HUMAN, frozenset({3}), 3, 0, execution)
    old, _ = READINGS["PB-3v_same_reading_object_is_verification_report"]
    reject(lambda: Transition(report.artifact, AGENT, execution.production_stage, old["tE"],
                              old["sigma"], HUMAN, frozenset({3}), old["tJ"], 0, execution))
    reject(lambda: Transition(report.artifact, AGENT, frozenset({2}), 2, 3,
                              HUMAN, frozenset({2}), 2, 0, execution))
    reject(lambda: Transition(report.artifact, AGENT, frozenset({1, 2}), 1, 2,
                              HUMAN, frozenset({3}), 3, 0, execution))

    edge = {f"{HUMAN}->{AGENT}": frozenset({2})}
    results = {}
    for artifact in (execution, report):
        results[artifact.artifact] = {}
        for label, record in {
            "publication_evidence_only": ControlRecord({}, False),
            "hypothetical_complete_with_edge": ControlRecord(edge, True),
            "hypothetical_incomplete_with_authenticated_witness": ControlRecord(edge, False),
            "hypothetical_complete_without_edge": ControlRecord({}, True),
        }.items():
            value = classify(artifact, record)
            if record.edges and artifact is report:
                expected = "CONFLICT", [HUMAN], False
            elif record.complete:
                expected = "NO_CONFLICT_ESTABLISHED", [], True
            else:
                expected = "UNDETERMINED", [], False
            verify((value["outcome"], value["witness_principals"], value["passes_control_gate"]), expected)
            results[artifact.artifact][label] = value
    return {"variant": "PB-3v-v1.0.1", "archived_PB-3v": "MODEL_INVALID",
            "execution_output": {"production_stage": [0, 1], "produced": 1, "sealed": 1, "adjudicated": 3},
            "verification_report": {"production_stage": [2], "produced": 2, "sealed": 2, "adjudicated": 3,
                                    "input": "execution-output"},
            "record_start": 0, "hypothetical_edge": {k: sorted(v) for k, v in edge.items()}, "results": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = run()
    if args.out:
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS: 3 invalid transitions rejected, 8 typed control decisions verified")
