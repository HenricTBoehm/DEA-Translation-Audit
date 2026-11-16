"""Bounded research fixture for event order, history closure, and control evidence."""

from dataclasses import dataclass
from enum import Enum


class HistoryBasis(Enum):
    TRUSTED_INITIAL_STATE = "TRUSTED_INITIAL_STATE"
    VERIFIED_NEUTRALIZATION = "VERIFIED_NEUTRALIZATION"


@dataclass(frozen=True)
class Scope:
    artifact_version: str
    producer: str
    adjudicator: str
    control_record_version: str


@dataclass(frozen=True)
class Transition:
    scope: Scope
    record_start: int
    execution: int | None
    seal: int | None
    adjudication: int | None


@dataclass(frozen=True)
class Edge:
    controller: str
    subject: str
    event: int
    authenticated: bool


@dataclass(frozen=True)
class Coverage:
    scope: Scope
    start: int
    through: int
    attested: bool


@dataclass(frozen=True)
class HistoryClosure:
    scope: Scope
    start: int
    basis: HistoryBasis
    independently_attested: bool


@dataclass(frozen=True)
class Evidence:
    scope: Scope
    edges: tuple[Edge, ...]
    coverage: Coverage | None = None
    history: HistoryClosure | None = None


def validate_transition(transition: Transition, evidence: Evidence) -> str:
    """Check event ranks and authenticated-model bindings supplied by the fixture."""
    if transition.scope != evidence.scope or not all(vars(transition.scope).values()):
        return "MODEL_INVALID"
    events = (transition.execution, transition.seal, transition.adjudication)
    if type(transition.record_start) is not int or transition.record_start < 0:
        return "MODEL_INVALID"
    if any(event is not None and (type(event) is not int or event < 0) for event in events):
        return "MODEL_INVALID"
    edge_ranks = tuple(edge.event for edge in evidence.edges)
    if any(type(event) is not int or event < 0 for event in edge_ranks):
        return "MODEL_INVALID"
    if len(set(edge_ranks)) != len(edge_ranks) or any(
        not edge.controller or not edge.subject for edge in evidence.edges
    ):
        return "MODEL_INVALID"
    known_ranks = (transition.record_start, *(event for event in events if event is not None))
    if known_ranks != tuple(sorted(known_ranks)):
        return "MODEL_INVALID"
    return "UNDETERMINED" if None in events else "VALID"


def coverage_status(transition: Transition, evidence: Evidence) -> tuple[bool, bool]:
    """Return separate results for in-window coverage and historical closure."""
    coverage, history = evidence.coverage, evidence.history
    in_window = (
        coverage is not None
        and coverage.attested is True
        and coverage.scope == transition.scope
        and coverage.start == transition.record_start
        and coverage.through >= transition.adjudication
        and all(edge.authenticated is True for edge in evidence.edges
                if transition.record_start <= edge.event <= transition.adjudication)
    )
    historically_closed = (
        history is not None
        and history.independently_attested is True
        and history.scope == transition.scope
        and history.start == transition.record_start
        and isinstance(history.basis, HistoryBasis)
        and not (history.basis is HistoryBasis.TRUSTED_INITIAL_STATE
                 and any(edge.authenticated is True and edge.event < history.start
                         for edge in evidence.edges))
    )
    return in_window, historically_closed


def paths_to(target: str, edges: tuple[Edge, ...], start: int, end: int):
    """Find one journey per principal by scanning the ordered edges backwards."""
    paths: dict[str, tuple[Edge, ...]] = {target: ()}
    for edge in sorted(edges, key=lambda e: e.event, reverse=True):
        if (
            edge.authenticated is True
            and start <= edge.event <= end
            and edge.subject in paths
            and edge.controller != target
        ):
            paths[edge.controller] = (edge, *paths[edge.subject])
    return paths


def evaluate(transition: Transition, evidence: Evidence) -> dict:
    admission = validate_transition(transition, evidence)
    report = {
        "version": "0.1", "scope": vars(transition.scope).copy(),
        "event_window": {"start": transition.record_start, "execution": transition.execution,
                         "seal": transition.seal, "adjudication": transition.adjudication},
        "input": admission, "in_window_coverage": None, "historical_closure": None,
        "history_basis": None, "witnesses": [],
        "outcome": admission, "passes_control_gate": False,
    }
    if admission != "VALID":
        return report
    in_window, historically_closed = coverage_status(transition, evidence)
    producer_paths = paths_to(transition.scope.producer, evidence.edges, transition.record_start, transition.seal)
    adjudicator_paths = paths_to(transition.scope.adjudicator, evidence.edges, transition.record_start,
                                transition.adjudication)
    witnesses = [
        {"principal": principal, "producer_path": [vars(edge).copy() for edge in producer_paths[principal]],
         "adjudicator_path": [vars(edge).copy() for edge in adjudicator_paths[principal]]}
        for principal in sorted(producer_paths.keys() & adjudicator_paths.keys())
    ]
    if witnesses:
        outcome = "CONFLICT"
    elif in_window and historically_closed:
        outcome = "NO_CONFLICT_ESTABLISHED"
    else:
        outcome = "UNDETERMINED"
    return report | {
        "in_window_coverage": in_window, "historical_closure": historically_closed,
        "history_basis": evidence.history.basis.value if historically_closed else None,
        "witnesses": witnesses, "outcome": outcome,
        "passes_control_gate": outcome == "NO_CONFLICT_ESTABLISHED",
    }
