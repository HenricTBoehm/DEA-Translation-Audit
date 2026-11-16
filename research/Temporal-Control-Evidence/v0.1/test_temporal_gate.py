import unittest
from dataclasses import replace
from itertools import product

from temporal_gate import Coverage, Edge, Evidence, HistoryBasis, HistoryClosure, Scope, Transition, evaluate, paths_to


SCOPE = Scope("execution-output@1", "a", "j", "control-record@1")
TRANSITION = Transition(SCOPE, record_start=1, execution=2, seal=2, adjudication=4)
COVERAGE = Coverage(SCOPE, start=1, through=4, attested=True)
GENESIS = HistoryClosure(SCOPE, 1, HistoryBasis.TRUSTED_INITIAL_STATE, independently_attested=True)
RESET = HistoryClosure(SCOPE, 1, HistoryBasis.VERIFIED_NEUTRALIZATION, independently_attested=True)
EARLY_EDGE = Edge("p", "j", 0, authenticated=True)
EXECUTION_EDGE = Edge("p", "a", 1, authenticated=True)
EARLY_INFLUENCE = (EARLY_EDGE, EXECUTION_EDGE)


class TemporalEvidenceTests(unittest.TestCase):
    def test_pre_history_counterexample_and_two_closure_routes(self):
        truncated = evaluate(TRANSITION, Evidence(SCOPE, EARLY_INFLUENCE, COVERAGE))
        self.assertEqual(truncated["outcome"], "UNDETERMINED")
        self.assertTrue(truncated["in_window_coverage"])
        self.assertFalse(truncated["historical_closure"])
        extended = evaluate(replace(TRANSITION, record_start=0), Evidence(SCOPE, EARLY_INFLUENCE))
        self.assertEqual(extended["outcome"], "CONFLICT")
        self.assertEqual(extended["witnesses"][0]["adjudicator_path"][0]["event"], 0)
        contradictory = evaluate(TRANSITION, Evidence(SCOPE, EARLY_INFLUENCE, COVERAGE, GENESIS))
        self.assertEqual(contradictory["outcome"], "UNDETERMINED")
        neutralized = evaluate(TRANSITION, Evidence(SCOPE, EARLY_INFLUENCE, COVERAGE, RESET))
        self.assertEqual(neutralized["outcome"], "NO_CONFLICT_ESTABLISHED")
        genesis = evaluate(TRANSITION, Evidence(SCOPE, (EXECUTION_EDGE,), COVERAGE, GENESIS))
        self.assertEqual(genesis["outcome"], "NO_CONFLICT_ESTABLISHED")

    def test_missing_seal_and_invalid_chronology(self):
        evidence = Evidence(SCOPE, (EXECUTION_EDGE, Edge("p", "j", 3, authenticated=True)), COVERAGE, GENESIS)
        for transition, expected in (
            (replace(TRANSITION, seal=None), "UNDETERMINED"),
            (replace(TRANSITION, seal=5), "MODEL_INVALID"),
            (replace(TRANSITION, execution=0), "MODEL_INVALID"),
            (replace(TRANSITION, execution=5, seal=None), "MODEL_INVALID"),
        ):
            with self.subTest(transition=transition):
                result = evaluate(transition, evidence)
                self.assertEqual(result["outcome"], expected)
                self.assertEqual(result["witnesses"], [])
                self.assertFalse(result["passes_control_gate"])

    def test_competing_control_events_need_order(self):
        ambiguous = Evidence(SCOPE, (EXECUTION_EDGE, Edge("p", "j", 1, authenticated=True)), COVERAGE, GENESIS)
        self.assertEqual(evaluate(TRANSITION, ambiguous)["input"], "MODEL_INVALID")

    def test_incomplete_or_mismatched_attestations(self):
        wrong_scope = replace(SCOPE, artifact_version="report@1")
        for coverage, history in (
            (None, GENESIS), (COVERAGE, None),
            (replace(COVERAGE, through=3), GENESIS),
            (replace(COVERAGE, scope=wrong_scope), GENESIS),
            (COVERAGE, replace(RESET, scope=wrong_scope)),
            (COVERAGE, replace(RESET, independently_attested=False)),
            (COVERAGE, replace(GENESIS, start=0)),
        ):
            with self.subTest(coverage=coverage, history=history):
                result = evaluate(TRANSITION, Evidence(SCOPE, (EXECUTION_EDGE,), coverage, history))
                self.assertEqual(result["outcome"], "UNDETERMINED")
                self.assertFalse(result["passes_control_gate"])

    def test_positive_witness_is_local_and_requires_authentication(self):
        forward = (EXECUTION_EDGE, Edge("p", "o", 2, authenticated=True), Edge("o", "j", 3, authenticated=True))
        reverse = (EXECUTION_EDGE, Edge("o", "j", 2, authenticated=True), Edge("p", "o", 3, authenticated=True))
        self.assertEqual(evaluate(TRANSITION, Evidence(SCOPE, forward))["outcome"], "CONFLICT")
        self.assertEqual(evaluate(TRANSITION, Evidence(SCOPE, reverse))["outcome"], "UNDETERMINED")
        unauthenticated = forward[:2] + (replace(forward[2], authenticated=False),)
        result = evaluate(TRANSITION, Evidence(SCOPE, unauthenticated, COVERAGE, GENESIS))
        self.assertFalse(result["in_window_coverage"])
        self.assertEqual(result["outcome"], "UNDETERMINED")

    def test_late_edges_and_reflexive_conflict(self):
        for edges in ((Edge("p", "a", 3, authenticated=True), Edge("p", "j", 4, authenticated=True)),
                      (EXECUTION_EDGE, Edge("p", "j", 5, authenticated=True))):
            self.assertEqual(evaluate(TRANSITION, Evidence(SCOPE, edges, COVERAGE, GENESIS))["outcome"],
                             "NO_CONFLICT_ESTABLISHED")
        scope = replace(SCOPE, adjudicator="a")
        result = evaluate(replace(TRANSITION, scope=scope), Evidence(scope, ()))
        self.assertEqual(result["witnesses"], [{"principal": "a", "producer_path": [], "adjudicator_path": []}])

    def test_journey_scan_matches_forward_replay_in_small_ordered_traces(self):
        vertices = ("p", "a", "j")
        arcs = tuple((left, right) for left in vertices for right in vertices if left != right)
        for trace in product((None, *arcs), repeat=3):
            edges = tuple(Edge(*arc, rank, authenticated=True) for rank, arc in enumerate(trace) if arc)
            for target in vertices:
                backward = paths_to(target, edges, 0, 2)
                for source in vertices:
                    reached = {source}
                    for edge in edges:
                        if edge.controller in reached:
                            reached.add(edge.subject)
                    self.assertEqual(source in backward, target in reached, (trace, source, target))
                    if source in backward:
                        cursor = source
                        previous = -1
                        for edge in backward[source]:
                            self.assertEqual(edge.controller, cursor)
                            self.assertGreater(edge.event, previous)
                            cursor, previous = edge.subject, edge.event
                        self.assertEqual(cursor, target)


if __name__ == "__main__":
    unittest.main()
