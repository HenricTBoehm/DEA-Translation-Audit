"""Assessor regression controls for this public bounded experiment."""
import json
from pathlib import Path
import sys

from acquisition import combine, e2
from observe import OVERFLOW


def compare(report):
    rows = {r["name"]: r for r in report["attempts"]}
    expected = {
        "B01": ("r@0", True, False), "B02": ("r@1", False, True),
        "B03": ("r@0", True, False), "B04": ("r@1", False, False),
        "B05": ("r@1", False, True), "B06": ("r@2", True, False),
        "B07": ("r@1", False, True), "B08": ("r@1", True, True),
        "B09": ("r@1", True, False), "B10": ("r@1", False, True),
    }
    assert set(rows) == set(expected)
    for name, row in rows.items():
        reference = row["reference"]
        assert reference["fd_full_read"] and reference["output_consistent"]
        assert (reference["version"], row["actual_output"]["accept"],
                reference["control"]["sr1_material_conflict"]) == expected[name]
        assert row["profiles"]["E2"]["observed"]["read"] == reference["read"]
        assert reference["bind_mismatch"] == (name == "B10")
        if row["profiles"]["E2"]["relations"] is not None:
            for relation in ("threshold_successor", "cosmetic_successor", "resolver_selection",
                             "material_selection_hypothesis", "surviving_material_effect", "policy_control"):
                assert row["profiles"]["E2"]["relations"][relation] == reference["control"][relation]

    assert rows["B04"]["reference"]["control"]["material_selection_hypothesis"]
    b07 = rows["B07"]["profiles"]
    assert b07["E1"]["decisions"]["D1"]["verdict"] == "UNDETERMINED"
    assert b07["E2"]["decisions"]["D1"]["verdict"] == "CONFLICT"
    b08 = rows["B08"]["profiles"]
    assert b08["E1"]["decisions"]["D1"]["verdict"] == "NO_CONFLICT_ESTABLISHED"
    assert b08["E2"]["decisions"]["D1"]["verdict"] == "CONFLICT"
    assert b08["combined"]["decisions"]["D1"]["verdict"] == "MODEL_INVALID"
    assert rows["B10"]["profiles"]["E2"]["decisions"]["D0"]["verdict"] == "MODEL_INVALID"
    assert e2([[{"mask": OVERFLOW, "name": ""}]], {}) == {}
    assert combine({"read": "a"}, {"read": "b"}) == ({}, ["read"])
    if report["opa"] == "EXECUTED":
        for name, row in rows.items():
            decisions = row["profiles"]["E2"]["decisions"]
            assert decisions["OPA"]["verdict"] == decisions["D1"]["verdict"], name
    print("PASS: B01–B10 reference, relations, missing observation, contradictory evidence and trace overflow")


if __name__ == "__main__":
    compare(json.loads(Path(sys.argv[1]).read_text()))
