"""Shared A-derived producer: forward snapshots from neutral records only."""
import hashlib
import json

from wire import FIELDS, OWNERS, STEMS, admit, permission


def encode(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode()


def right(key, target, channel, event_id):
    return {"key": key, "principal": OWNERS[key], "target": target, "channel": channel, "event": event_id}


def actor(row):
    return {"principal": OWNERS[row["key"]], "key": row["key"], "event": row["id"]}


def initial_versions():
    return {f"{s}@0": {"base": None, "event": None,
                        "fields": {f: {"value": 0, "origin": None} for f in FIELDS}}
            for s in STEMS}


def record_envelope(evidence, state, reason):
    return {"event_check": state, "event_reason": reason,
            "scope": {"history": evidence["history_closed"], "reads": evidence["dependencies_closed"]}}


def export(wire_bytes):
    evidence = json.loads(wire_bytes)
    state, reason, rows = admit(evidence)
    facts = record_envelope(evidence, state, reason)
    if state != "settled":
        return facts
    rights, revoked, reads = {}, set(), []
    versions = initial_versions()
    heads = {s: f"{s}@0" for s in STEMS}
    for row in rows:
        kind = row["kind"]
        if kind == "grant":
            rights[permission(row)] = row["id"]
        elif kind == "retract":
            del rights[permission(row)]
        elif kind == "revoke":
            revoked.add(row["subject"])
        elif kind in ("reset", "modify"):
            base, field = row["base"], row["channel"]
            old = versions[base]["fields"][field]
            if kind == "reset":
                new = {"value": 0, "origin": None}
            elif row["value"] == old["value"]:
                new = old
            else:
                key = row["key"]
                new = {"value": row["value"], "origin": {**actor(row),
                       "grant": rights[key, base[0], field]}}
            versions[row["version"]] = {
                "base": base, "event": row["id"],
                "fields": {**versions[base]["fields"], field: new}}
            heads[base[0]] = row["version"]
        elif kind == "produce":
            facts["producer"] = actor(row)
            facts["score_right"] = rights.get((row["key"], "x", "score"))
        elif kind == "seal":
            facts["seal"] = {k: row[k] for k in ("id", "version", "policy")}
        elif kind == "bind":
            facts["binding"] = {k: row[k] for k in ("id", "root", "version", "policy")}
            facts["versions"] = dict(versions)
            facts["heads"] = dict(heads)
            facts["rights"] = [right(*entry, eid) for entry, eid in sorted(rights.items())
                               if entry[0] not in revoked]
        elif kind == "read":
            reads.append({k: row[k] for k in ("id", "version", "parent")})
        elif kind == "adjudicate":
            facts["reviewer"] = actor(row)
            facts["commit"] = {k: row[k] for k in ("id", "version", "policy")}
    facts["reads"] = reads
    return facts


def bundle(wire_bytes):
    return {"wire_sha256": hashlib.sha256(wire_bytes).hexdigest(), "provenance": export(wire_bytes)}
