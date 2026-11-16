"""Scoped P-01: only the pinpointed mandatory artifact controller expands J."""

from d0 import gate, identity_witness, negative, reply


def decide(facts):
    if result := gate(facts):
        return result
    if witness := identity_witness(facts):
        return reply("CONFLICT", "reviewer_identity", witness)
    producer = facts["producer"]
    for read in facts["reads"]:
        version = read["version"]
        origin = facts["versions"][version]["fields"]["threshold"]["origin"]
        if origin and origin["principal"] == producer["principal"]:
            witness = [producer["principal"], producer["event"], version,
                       origin["grant"], origin["event"], facts["binding"]["id"], read["id"]]
            return reply("CONFLICT", "bound_version_surviving_effect", witness)
    return negative(facts)
