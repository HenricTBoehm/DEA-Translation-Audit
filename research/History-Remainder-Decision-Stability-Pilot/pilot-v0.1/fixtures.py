"""Shared input data; oracle truth fields are separated by the runner."""

from copy import deepcopy
from itertools import product

SCOPE = {"attempt": "adjudication@1", "seal": "x@1", "rubric": "rubric@1",
         "policy": "threshold@1", "commit": "bundle@1"}


def row(event_id, kind, t, order=0, **kw):
    return {"id": event_id, "kind": kind, "time": t, "order": order,
            "authenticated": True, **kw}


def control(event_id, src, dst, t, order=0, bundle=False, channel="criteria"):
    return row(event_id, "control", t, order, src=src, dst=dst, dst_artifact=bundle,
               channel=channel, persistence="potential_durable")


def reset(channel):
    return row("reset", "reset", 4, target="rubric@1", target_artifact=True, channels=[channel],
               independent=True, scope_proved=True, neutralized=True)


def token(target, *, artifact=True, channel="criteria", source="p"):
    return {"id": f"historical:{source}:{target}:{channel}", "principal": source, "target": target,
            "target_artifact": artifact, "channel": channel, "authenticated": True}


def fixture():
    return {
        "model": {"attempt": "adjudication@1", "policy": "threshold@1", "artifact": "x@1", "record_start": 1, "binding_verified": True,
                  "snapshot_attested": True, "snapshot_version": "bundle@1", "commit_version": "bundle@1",
                  "bound_complete": True, "graph_attested": True, "record_complete": True, "authorized": True,
                  "events": [
                      row("produce", "produce", 2, artifact="x@1", actor="a", inputs=[]),
                      row("seal", "seal", 3, artifact="x@1", pins={"rubric": "rubric@1"}),
                      row("commit", "adjudicate", 5, artifact="x@1", actor="j", roots={"rubric": "rubric@1"}),
                  ]},
        "remainder": {"kind": "Z", "issuer": "i", "attested": True, "actual_attested": True,
                      "witnesses": [], "upper": [], "uncovered": []},
        "scientific": {"scope": dict(SCOPE), "world_scope": dict(SCOPE), "policy_defined": True,
                       "domains": {"calibration": [0, 1], "archive_context": [0, 1]},
                       "observed": {}, "weights": {}, "offset": 1, "threshold": 1,
                       "covered": True, "samples": []},
        "oracle": {"prestate": [], "valid": True, "authorized": True},
    }


def named():
    cases = {f"S{i:02d}": fixture() for i in range(1, 13)}

    def controls(key, *events):
        cases[key]["model"]["events"].extend(events)

    producer = control("producer-control", "p", "a", 1, channel="capability")
    rubric = control("rubric-control", "p", "rubric@1", 1, 1, bundle=True)
    controls("S02", producer, rubric)
    for name in ("S03", "S04", "S09"):
        cases[name]["remainder"].update(kind="U", attested=False)
    cases["S04"]["scientific"].update(offset=0, weights={"calibration": 1})
    s05 = cases["S05"]
    s05["model"]["events"][2]["roots"] = {"rubric": "rubric@2"}
    s05["scientific"]["world_scope"]["rubric"] = "rubric@2"
    s05["oracle"]["valid"] = False
    controls("S06", producer, control("rubric-control-late", "p", "rubric@1", 4, bundle=True))
    controls("S07", producer, row("read", "read", 4, actor="p", artifact="rubric@1"))
    for name in ("S08", "S10", "S11"):
        cases[name]["remainder"].update(kind="B", upper=[token("rubric@1")])
        controls(name, producer)
    s09 = cases["S09"]
    s09["remainder"]["uncovered"] = [["relay", "credential"]]
    s09["oracle"]["prestate"] = [token("relay", artifact=False, channel="credential")]
    controls("S09", producer, control("relay", "relay", "j", 4))
    s09["scientific"].update(offset=0, weights={"archive_context": 1})
    for name, channel in (("S10", "credential"), ("S11", "criteria")):
        cases[name]["oracle"]["prestate"] = [token("rubric@1")]
        cases[name]["remainder"]["witnesses"] = [token("rubric@1")]
        controls(name, reset(channel))
    s12 = cases["S12"]
    s12["model"]["bound_complete"] = False
    s12["scientific"]["policy_defined"] = False
    s12["oracle"]["hidden_dependencies"] = [{"from": "rubric@1", "to": "resolver@1", "role": "resolver",
                                              "authenticated": True}]
    return cases


def generated(bits):
    actual, witnessed, include_upper, certified, reset_code, sensitive = bits
    case = fixture()
    case["model"]["events"].append(control("producer-control", "p", "a", 1, channel="capability"))
    present = [token("rubric@1")] if actual else []
    case["oracle"]["prestate"] = present
    case["remainder"].update(kind="B" if certified else "U", attested=bool(certified),
                             witnesses=present if witnessed else [], upper=[token("rubric@1")] if include_upper else [])
    # The issuer can only attest to this finite scenario's declared envelope.
    # Generator admits incomplete bounds as U. Counterexample audit separately tests lying certificates.
    if actual and not (witnessed or include_upper):
        case["remainder"].update(kind="U", attested=False, uncovered=[["rubric@1", "criteria"]])
    if reset_code:
        case["model"]["events"].append(reset(("credential", "criteria")[reset_code - 1]))
    case["scientific"].update(offset=0 if sensitive else 1, weights={"calibration": int(bool(sensitive))})
    return case


def parameters():
    return product(range(2), range(2), range(2), range(2), range(3), range(2))


def stability_probes():
    basic = fixture()["scientific"]
    constant_sample = deepcopy(basic) | {"covered": False, "samples": [[0, 0]]}
    return {
        "empty": (deepcopy(basic) | {"allowed": []}, "STABILITY_UNDETERMINED"),
        "matching_sample": (constant_sample, "SAMPLED_STABLE"),
        "disagreement_in_sample": (constant_sample | {"offset": 0, "weights": {"calibration": 1},
                                                       "samples": [[0, 0], [0, 1]]}, "UNSTABLE"),
        "different_rubric": (deepcopy(basic) | {"world_scope": SCOPE | {"rubric": "rubric@2"}},
                             "STABILITY_UNDETERMINED"),
        "correlated_worlds": (deepcopy(basic) | {"allowed": [[0, 0], [1, 1]], "offset": 0,
                                                 "weights": {"calibration": 1, "archive_context": 1}},
                              "UNSTABLE"),
    }
