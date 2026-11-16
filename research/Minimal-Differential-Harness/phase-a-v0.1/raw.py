"""Per-arm A-raw adapter: reconstruct the facts by prior-event joins and lineage."""
import json

from provenance import actor, initial_versions, record_envelope, right
from wire import admit, permission


def reconstruct(wire_bytes):
    evidence = json.loads(wire_bytes)
    status, reason, rows = admit(evidence)
    facts = record_envelope(evidence, status, reason)
    if status != "settled":
        return facts
    prior = {row["kind"]: row for row in rows}
    binding, production = prior["bind"], prior["produce"]
    changes = {r["version"]: r for r in rows if r["kind"] in ("modify", "reset")
               and r["rank"] < binding["rank"]}
    genesis = initial_versions()

    def active(entry, rank):
        actions = [r for r in rows if r["rank"] < rank and r["kind"] in ("grant", "retract")
                   and permission(r) == entry]
        revoked = any(r["kind"] == "revoke" and r["subject"] == entry[0] and r["rank"] < rank
                      for r in rows)
        return actions[-1]["id"] if actions and actions[-1]["kind"] == "grant" and not revoked else None

    def version_details(version):
        if version in genesis:
            return genesis[version]
        edit = changes[version]
        base, field = edit["base"], edit["channel"]
        earlier = version_details(base)["fields"]
        if edit["kind"] == "reset":
            updated = {"value": 0, "origin": None}
        elif edit["value"] == earlier[field]["value"]:
            updated = earlier[field]
        else:
            updated = {"value": edit["value"], "origin": {
                **actor(edit), "grant": active((edit["key"], base[0], field), edit["rank"])}}
        return {"base": base, "event": edit["id"], "fields": {**earlier, field: updated}}

    versions = {v: version_details(v) for v in set(genesis) | set(changes)}
    entries = sorted({permission(r) for r in rows if r["kind"] == "grant"})
    facts.update(
        producer=actor(production), reviewer=actor(prior["adjudicate"]),
        score_right=active((production["key"], "x", "score"), production["rank"]),
        seal={k: prior["seal"][k] for k in ("id", "version", "policy")},
        binding={k: binding[k] for k in ("id", "root", "version", "policy")},
        commit={k: prior["adjudicate"][k] for k in ("id", "version", "policy")},
        versions=versions,
        heads={stem: max(v for v in versions if v[0] == stem) for stem in ("r", "s", "t")},
        rights=[right(*entry, eid) for entry in entries
                if (eid := active(entry, binding["rank"])) is not None],
        reads=[{k: r[k] for k in ("id", "version", "parent")} for r in rows if r["kind"] == "read"],
    )
    return facts
