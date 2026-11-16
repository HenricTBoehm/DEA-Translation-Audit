"""Scoped translation of v0.3.5.1 HC equations on the neutral wire profile."""


def gate(facts):
    check = facts["event_check"]
    if check == "contradiction":
        return reply("MODEL_INVALID", facts["event_reason"])
    if check != "settled":
        return reply("UNDETERMINED", facts["event_reason"])


def reply(verdict, reason, witness=None):
    return {"verdict": verdict, "reason": reason, "witness": witness}


def identity_witness(facts):
    producer, reviewer = facts["producer"], facts["reviewer"]
    if producer["principal"] == reviewer["principal"]:
        return [producer["principal"], producer["event"], reviewer["event"]]


def negative(facts):
    if facts["scope"]["history"] and facts["scope"]["reads"]:
        return reply("NO_CONFLICT_ESTABLISHED", "coverage_conditional")
    return reply("UNDETERMINED", "read_coverage_open")


def decide(facts):
    if result := gate(facts):
        return result
    if witness := identity_witness(facts):
        return reply("CONFLICT", "reviewer_identity", witness)
    return negative(facts)
