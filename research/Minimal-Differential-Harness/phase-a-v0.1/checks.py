"""Evidence verification only. Participant modules do not import archived oracles."""
from itertools import product
import json
import sys

from adapters import decide
from provenance import bundle, encode, export
from raw import reconstruct
from run import REFERENCE, project

# Isolate archived modules with overlapping base names from participant imports.
import importlib.util
spec = importlib.util.spec_from_file_location("archived_oracle", REFERENCE / "oracle.py")
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)
sys.modules["oracle"] = reference
sys.path.append(str(REFERENCE))
from cases import altered, grant, reset, revoke, trace, write
from crosscheck import evaluate


def evidence(rows):
    return {"events": rows, "history_closed": True, "dependencies_closed": True}


def main():
    verified = 0
    for case in json.loads((REFERENCE / "PUBLIC_CASES.json").read_text()):
        wire = project(case["evidence"])
        facts = export(wire)
        assert facts == reconstruct(wire)
        assert not {"case", "label", "truth", "expected", "witness", "verdict"} & set(facts)
        observed = reference.justified(case["evidence"])
        assert observed["verdict"] == case["expected"]
        if observed.get("witness"):
            principal, score_grant, producer_id, version, mode, *path = observed["witness"]
            assert (facts["producer"]["principal"], facts["score_right"], facts["producer"]["event"]) == (
                principal, score_grant, producer_id)
            assert any(read["version"] == version and read["id"] == path[-1] for read in facts["reads"])
            assert facts["binding"]["id"] == path[-2]
            if mode == "surviving":
                origin = facts["versions"][version]["fields"]["threshold"]["origin"]
                assert (origin["principal"], origin["grant"], origin["event"]) == (principal, *path[:2])
            else:
                assert any(r["event"] == path[0] and r["channel"] == "threshold"
                           and r["principal"] == principal and facts["heads"][r["target"]] == version
                           for r in facts["rights"])
            verified += 1

    generated = 0
    for writer, channel, withdrawn, successor, selected, timing in product(
        ("ka", "kq"), ("threshold", "layout"), (False, True),
        (None, "layout", "threshold"), ("r@0", "r@1", "r@2"), (True, False)
    ):
        first, second = (3, 5) if timing else (5, 3)
        changes = [grant(1, writer, "r", channel), write(first, writer, "r@0", "r@1", channel)]
        if withdrawn:
            changes.append(revoke(second, writer))
        if successor:
            changes.append(reset(6, "r@1", "r@2", successor))
        rows = trace(*changes, root=selected)
        wire = project(evidence(rows))
        facts = export(wire)
        assert facts == reconstruct(wire)
        actual, _ = evaluate(rows)
        assert (facts["event_check"] == "contradiction") == (actual == "MODEL_INVALID")
        generated += 1

    # D0 and D1 preserve reflexive identity even when SR-1's production-right
    # premise is missing. This exercises a source rule, outside the 38 cases.
    identity = project(evidence(trace(signer="kj")))
    for arm in ("D0", "D1"):
        assert decide(arm, "raw", identity)["reason"] == "reviewer_identity"
    other = project(evidence(altered(trace(), 4, key="kj")))
    try:
        decide("D0", "derived", other, encode(bundle(project(evidence(trace())))))
    except ValueError:
        pass
    else:
        raise AssertionError("cross-wire provenance accepted")
    print(f"PASS: 38 fact comparisons; {verified} external witness paths; "
          f"{generated} temporal fact comparisons and source/adapter checks")


if __name__ == "__main__":
    main()
