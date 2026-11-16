"""Independent relational checker: use prior-event queries and backward lineage.

No replay state or imports from the transition oracle. Expected labels are not inputs.
Schema validation and missing-rank search are outside this complete-history check.
"""
from itertools import product


def evaluate(events, root_required=True):
    trace = sorted(events, key=lambda row: row["rank"])
    ranks = [row["rank"] for row in trace]
    if (len(set(ranks)) != len(trace) or
            any(a["time"] > b["time"] for a, b in zip(trace, trace[1:]))):
        return "MODEL_INVALID", None
    positions = {row["kind"]: i for i, row in enumerate(trace)}
    for name in ("produce", "seal", "bind", "adjudicate"):
        if sum(row["kind"] == name for row in trace) != 1:
            return "MODEL_INVALID", None
    produce, seal, bind, end = (positions[name] for name in ("produce", "seal", "bind", "adjudicate"))
    if not produce < seal < bind < end == len(trace) - 1:
        return "MODEL_INVALID", None

    def revoked(key, stop):
        return any(row["kind"] == "revoke" and row["subject"] == key for row in trace[:stop])

    def permit(key, artifact, field, stop):
        relevant = [row["kind"] for row in trace[:stop]
                    if row["kind"] in ("grant", "retract")
                    and (row["subject"], row["target"], row["channel"]) == (key, artifact, field)]
        return relevant[-1:] == ["grant"] and not revoked(key, stop)

    def changes(artifact, stop):
        return [row for row in trace[:stop] if row["kind"] in ("modify", "reset")
                and row["base"][0] == artifact]

    def field_source(version, channel):
        if version.endswith("@0"):
            return 0, None
        write = next(row for row in trace if row.get("base") and row["version"] == version)
        old_value, old_source = field_source(write["base"], channel)
        if channel != write["channel"]:
            return old_value, old_source
        if write["kind"] == "reset":
            return 0, None
        value = write["value"]
        return value, write["key"] if value != old_value else old_source

    selected = []
    for i, row in enumerate(trace):
        kind, key = row["kind"], row["key"]
        if revoked(key, i):
            return "MODEL_INVALID", None
        if kind == "revoke" and revoked(row["subject"], i):
            return "MODEL_INVALID", None
        if kind in ("grant", "retract"):
            earlier = [old["kind"] for old in trace[:i] if old["kind"] in ("grant", "retract")
                       and all(old[f] == row[f] for f in ("subject", "target", "channel"))]
            if earlier[-1:] == ["grant"]:
                if kind == "grant":
                    return "MODEL_INVALID", None
            elif kind == "retract" or revoked(row["subject"], i):
                return "MODEL_INVALID", None
        if kind in ("modify", "reset"):
            base, version = row["base"], row["version"]
            history = changes(base[0], i)
            if version in [old["version"] for old in history]:
                return "MODEL_INVALID", None
            tip = history[-1]["version"] if history else f"{base[0]}@0"
            if base != tip or kind == "modify" and not permit(key, base[0], row["channel"], i):
                return "MODEL_INVALID", None
        if kind in ("read", "bind"):
            version = row["root"] if kind == "bind" else row["version"]
            known = version.endswith("@0") or any(old["version"] == version
                                                    for old in changes(version[0], bind))
            if not known:
                return "MODEL_INVALID", None
        if kind == "read":
            parent, version = row["parent"], row["version"]
            if not bind < i < end or any(v[0] == version[0] for v in selected):
                return "MODEL_INVALID", None
            if not selected and (parent is not None or version != trace[bind]["root"]):
                return "MODEL_INVALID", None
            if selected and parent not in selected:
                return "MODEL_INVALID", None
            selected.append(version)
    if not selected and (root_required or set(range(ranks[bind] + 1, ranks[end])) <= set(ranks)):
        return "MODEL_INVALID", None

    producer = trace[produce]["key"]
    if not permit(producer, "x", "score", produce):
        return ("NO_CONFLICT", None) if trace[produce]["value"] == 0 else ("MODEL_INVALID", None)

    # Counterfactual outcome proof in the actual finite rating procedure.
    values = [field_source(version, "threshold")[0] for version in selected]
    causal_versions = set()
    for i, version in enumerate(selected):
        replacements = list(values)
        replacements[i] = 1 - values[i]
        changes_outcome = any((score >= sum(values)) != (score >= sum(replacements))
                              for score in range(4))
        history = changes(version[0], bind)
        tip = history[-1]["version"] if history else f"{version[0]}@0"
        current = (tip == version and not version.endswith("@2")
                   and permit(producer, version[0], "threshold", bind))
        historical = field_source(version, "threshold")[1] == producer
        if changes_outcome and (current or historical):
            causal_versions.add(version)
    return ("CONFLICT", causal_versions) if causal_versions else ("NO_CONFLICT", None)


def rank_realizations(events):
    """Independent finite slot assignment for test probes with <= 2 omissions."""
    open_ids = [row["id"] for row in events if row["rank"] is None]
    assert len(open_ids) <= 2
    for values in product(range(16), repeat=len(open_ids)):
        assigned = dict(zip(open_ids, values))
        yield [{**row, "rank": assigned.get(row["id"], row["rank"])} for row in events]
