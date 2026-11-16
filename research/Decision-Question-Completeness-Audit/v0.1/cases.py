"""Examiner-owned hidden reference states. Only the observed branch enters a comparator."""

from copy import deepcopy
from fixtures import fixture, control

CLEAR = "NO_CONFLICT_ESTABLISHED"
HOLD = "UNDETERMINED"
STABLE = "CERTIFIED_STABLE"
UNKNOWN = "STABILITY_UNDETERMINED"


def world(output, **values):
    return {"values": values, "decision": output}


def model(domains=None, weights=None, *, offset=1, threshold=1, historic=False):
    state = fixture()
    state.pop("oracle")
    state["scientific"].update(domains=domains or {}, weights=weights or {}, offset=offset,
                               threshold=threshold, observed={})
    if historic:
        state["remainder"].update(kind="U", attested=False)
    return state


def xy(name):
    return [world("REJECT", **{name: 0}), world("ACCEPT", **{name: 1})]


def review_source(observed, *, variables=(), bindings=None, effects=(), outside_world=None):
    return {
        "scope": deepcopy(observed["scientific"]["scope"]),
        "variable_requirements": list(variables),
        "binding_requirements": bindings or {},
        "effect_requirements": list(effects),
        "missing_world": outside_world,
    }


def suites():
    result = {}
    active = "calibration"

    def add(name, cause, observed, worlds, witness, limitation, expected, findings=(), external=None,
            needed=(), true_conflict=False):
        result[name] = {
            "cause": cause, "observed": observed, "truth": {"worlds": worlds, "control_conflict": true_conflict,
                                                           "needed_governance_bindings": list(needed)},
            "withheld": witness, "detectable_only_with": limitation,
            "source": external, "expected": {"C": expected[0], "science": expected[1],
                                            "query": expected[2], "audit_findings": list(findings)},
        }

    state = model({active: [0, 1]}, {active: 1}, offset=0, historic=True)
    add("Q-A", "Q1", state, xy(active), "one unobserved answer to a known calibration question",
        "attest which calibration applied", (HOLD, "UNSTABLE", [active]),
        external=review_source(state, variables=[active], effects=[active]))

    state = model()
    twin = deepcopy(state)
    add("Q-B", "Q2", state, xy(active), "calibration field entirely absent from modeled input",
        "independent procedure specification identifies calibration", (CLEAR, STABLE, []),
        ["MISSING_VARIABLE:calibration"], review_source(state, variables=[active], effects=[active]))
    add("Q-B0", "indistinguishable control", twin, [world("ACCEPT")], "none",
        "same observed bytes as Q-B", (CLEAR, STABLE, []), external=review_source(twin))

    state = model()
    state["model"]["events"].extend([
        control("p-executor", "p", "a", 1, channel="capability"),
        control("p-standard", "p", "standard@1", 4, bundle=True),
    ])
    add("Q-C", "Q3 governance", state, [world("ACCEPT")],
        "the mandatory standard is absent from the trusted dependency claim despite its recorded controller",
        "independent rubric/standard manifest with mandatory role", (CLEAR, STABLE, []),
        ["MISSING_BINDING:standard"], review_source(state, bindings={"standard": "standard@1"}),
        needed=["standard"], true_conflict=True)

    state = model({"resolver": [0, 1]})
    # The true version-bound procedure resolves one of two explicit standards at runtime.
    route = {0: "low@1", 1: "high@1"}
    standards = {"low@1": "REJECT", "high@1": "ACCEPT"}
    dynamic_worlds = [world(standards[route[v]], resolver=v) for v in (0, 1)]
    add("Q-D", "Q3 dynamic", state, dynamic_worlds, "runtime resolver is unconnected in the claimed policy",
        "instrument or independently audit the authorized resolver", (CLEAR, STABLE, []),
        ["MISSING_EFFECT:resolver"], review_source(state, variables=["resolver"], effects=["resolver"]))

    state = model({active: [0, 1]}, {active: 1}, offset=0)
    state["scientific"]["allowed"] = [[1]]
    add("Q-E", "Q4", state, xy(active), "same protected scope allows calibration=0, excluded by false world closure",
        "independently verify admissibility of omitted world", (CLEAR, STABLE, []),
        ["OMITTED_ADMISSIBLE_WORLD"], review_source(state, variables=[active], effects=[active],
                                                    outside_world={active: 0}))

    state = model({"archive_note": [0, 1]}, historic=True)
    add("Q-F", "irrelevant open answer", state, [world("ACCEPT", archive_note=v) for v in (0, 1)],
        "archive note remains unknown; no outcome dependence", "verified fixed rule and exhaustive domain",
        (HOLD, STABLE, []), external=review_source(state, variables=["archive_note"]))

    state = model()
    state["model"]["events"].extend([
        control("p-executor", "p", "a", 1, channel="capability"),
        control("p-rubric", "p", "rubric@1", 4, bundle=True),
    ])
    add("Q-G", "governance/ongoing state", state, [world("ACCEPT")], "both governed roles share controller p",
        "no scientific question can change this control witness", ("CONFLICT", STABLE, []),
        external=review_source(state, bindings={"rubric": "rubric@1"}), true_conflict=True)

    state = model({"display_theme": [0, 1]})
    add("Q-H", "irrelevant proposed question", state, [world("ACCEPT", display_theme=v) for v in (0, 1)],
        "irrelevant candidate query display_theme supplied before science evaluation",
        "joint outcome comparison across both values", (CLEAR, STABLE, []),
        external=review_source(state, variables=["display_theme"]))

    state = model({active: [0, 1]}, {active: 1}, offset=0, historic=True)
    state["scientific"].update(covered=False, samples=[[1]])
    add("Q-I", "Q4 acknowledged", state, xy(active), "only one admissible world sampled",
        "missing opposite-outcome case or certified coverage", (HOLD, "SAMPLED_STABLE", None),
        external=review_source(state, variables=[active], effects=[active]))

    state = model({"u": [0, 1], "v": [0, 1]}, {"u": 1, "v": 1}, offset=0, threshold=2)
    add("Q-J", "interaction", state, [world("ACCEPT" if u and v else "REJECT", u=u, v=v)
                                       for u, v in [(0, 0), (0, 1), (1, 0), (1, 1)]],
        "one-at-a-time perturbations from (0,0) cannot flip either result",
        "joint variation", (CLEAR, "UNSTABLE", ["u", "v"]),
        external=review_source(state, variables=["u", "v"], effects=["u", "v"]))

    state = model({"resolver": [0, 1]}, historic=True)
    state["model"]["bound_complete"] = False
    mismatched = review_source(state, variables=["resolver"], effects=["resolver"])
    mismatched["scope"]["policy"] = "stale@2"
    add("Q-K", "Q4 flagged; stale provenance", state, xy("resolver"),
        "trace coverage explicitly absent; review receipt from another scope",
        "version-matched independent dependency evidence", (HOLD, UNKNOWN, None),
        ["SOURCE_SCOPE_UNVERIFIED"], mismatched)
    return result


def public_cases(reports):
    for name, report in reports.items():
        switch = report["parameter"]
        worlds = [world(report["runs"][label]["decision"], **{switch: value})
                  for value, label in ((0, "term_omitted"), (1, "published_terms"))]
        # Validation is against the documented reference fit in both execution variants.
        for listed in (True, False):
            observed = model({switch: [0, 1]} if listed else {}, {switch: 1} if listed else {},
                             offset=0 if listed else 1, historic=True)
            for key in ("scope", "world_scope"):
                observed["scientific"][key].update(attempt=f"NIST-{name}@1", policy=f"coefficient-tolerance-{name}@1")
            observed["model"].update(attempt=f"NIST-{name}@1", policy=f"coefficient-tolerance-{name}@1")
            # Reading the NIST formula supplies independent information about the required term.
            source = review_source(observed, variables=[switch], effects=[switch])
            source["public_fixture"] = name
            yield name + ("-known-option" if listed else "-omitted-option"), {
                "cause": "Q1" if listed else "Q2",
                "truth": {"worlds": worlds, "control_conflict": None, "needed_governance_bindings": []},
                "observed": observed, "source": source,
                "withheld": "synthetic unknown execution setting" if listed else "synthetic removal of whole execution setting",
                "detectable_only_with": "consult original NIST formula and independently compare implementation options",
                "expected": {"C": HOLD, "science": "UNSTABLE" if listed else STABLE,
                             "query": [switch] if listed else [],
                             "audit_findings": [] if listed else ["MISSING_VARIABLE:" + switch]},
            }
