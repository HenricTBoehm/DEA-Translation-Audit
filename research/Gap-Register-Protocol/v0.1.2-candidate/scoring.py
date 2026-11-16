"""Assessor-only scoring of validated responses, not a comparison implementation."""

ACTIONS = {
    "CLEAR": "RELEASE", "CONFLICT": "BLOCK_CONFLICT",
    "UNDETERMINED": "BLOCK_UNDETERMINED", "INVALID": "INVALID",
}
STATUSES = set(ACTIONS.values()) | {"NO_DECISION"}
PROOFS = {"VERIFIED", "REJECTED", "UNVERIFIED", "NONE"}


def metrics(rows):
    """Each row has an assessor-checked proof tag and fidelity/premise outcomes."""
    def rate(eligible, hit):
        matching = [row for row in rows if eligible(row)]
        return [sum(hit(row) for row in matching), len(matching)]

    def expect(status):
        return lambda row: row["justified"] == status

    def acts(status):
        return lambda row: row["action"] == status

    def verified_correct(row):
        return row["action"] == ACTIONS[row["justified"]] and row["proof"] == "VERIFIED"

    of_all = lambda row: True
    release = acts("RELEASE")
    conflict = acts("BLOCK_CONFLICT")
    invalid = acts("INVALID")
    for row in rows:
        if (row["action"] not in STATUSES or row["proof"] not in PROOFS
                or row["action"] == "NO_DECISION" and row["proof"] != "NONE"):
            raise ValueError("invalid assessed response")
    result = {
        "justified_release": rate(expect("CLEAR"), release),
        "false_hold_justified": rate(expect("CLEAR"), lambda row: not release(row)),
        "false_release_justified": rate(lambda row: not expect("CLEAR")(row), release),
        "false_release_truth": rate(lambda row: row["truth"] == "CONFLICT", release),
        "release_invalid_truth": rate(lambda row: row["truth"] == "MODEL_INVALID", release),
        "holds_on_actual_no_conflict": rate(lambda row: row["truth"] == "NO_CONFLICT",
                                           lambda row: not release(row)),
        "verdict_exact": rate(of_all, lambda row: row["action"] == ACTIONS[row["justified"]]),
        "verdict_verified": rate(of_all, verified_correct),
        "verified_release": rate(expect("CLEAR"), verified_correct),
        "verified_conflict": rate(expect("CONFLICT"), verified_correct),
        "correct_abstention": rate(expect("UNDETERMINED"), verified_correct),
        "invalid_with_unverified_proof": rate(
            lambda row: expect("INVALID")(row) and invalid(row), lambda row: row["proof"] != "VERIFIED"),
        "proofless_correct_conflict_label": rate(
            expect("CONFLICT"), lambda row: conflict(row) and row["proof"] != "VERIFIED"),
        "miss_invalid": rate(expect("INVALID"), lambda row: not invalid(row)),
        "miss_actual_invalid": rate(lambda row: row["truth"] == "MODEL_INVALID",
                                    lambda row: not invalid(row)),
        "false_invalid": rate(lambda row: not expect("INVALID")(row), invalid),
        "unjustified_conflict": rate(lambda row: not expect("CONFLICT")(row), conflict),
        "unverified_conflict": rate(conflict, lambda row: row["proof"] != "VERIFIED"),
        "no_decision": rate(of_all, acts("NO_DECISION")),
    }
    for verdict in ("CONFLICT", "UNDETERMINED", "INVALID"):
        result[f"release_on_justified_{verdict.lower()}"] = rate(expect(verdict), release)
    for axis, statuses in (("fidelity", ("PASS", "FAIL", "UNDETERMINED", "NOT EXECUTED")),
                           ("premise", ("SUPPORTED", "OPEN", "CONTRADICTED", "NOT EXECUTED"))):
        for status in statuses:
            result[f"{axis}_{status}"] = rate(of_all, lambda row: row[axis] == status)
    return result
