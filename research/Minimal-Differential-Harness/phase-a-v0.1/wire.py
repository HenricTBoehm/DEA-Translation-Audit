"""Finite input admission per PR #13's event protocol; no policy verdicts."""
from itertools import permutations

OWNERS = {"ka": "p", "kq": "q", "kj": "j", "ki": "issuer"}
ACTORS = {"ka", "kq"}
STEMS = ("r", "s", "t")
FIELDS = ("threshold", "layout")
SLOTS = range(16)
VERSIONS = {f"{s}@{v}" for s in STEMS for v in range(3)}
STAGES = ("produce", "seal", "bind", "adjudicate")
POLICY = "sum-thresholds@1"
PAYLOAD = {
    "grant": "subject target channel", "retract": "subject target channel", "revoke": "subject",
    "modify": "base version channel value", "reset": "base version channel",
    "produce": "version value", "seal": "version policy", "bind": "version root policy",
    "read": "version parent", "adjudicate": "version policy",
}


def shape(row):
    kind = row.get("kind")
    if kind not in PAYLOAD or set(row) != {"id", "kind", "time", "rank", "key", *PAYLOAD[kind].split()}:
        return False
    if any(type(row[f]) is not int or row[f] not in SLOTS for f in ("id", "time")):
        return False
    if row["rank"] is not None and (type(row["rank"]) is not int or row["rank"] not in SLOTS):
        return False
    key = row["key"]
    if key not in OWNERS:
        return False
    if kind in ("grant", "retract"):
        return key == "ki" and row["subject"] in ACTORS and (
            (row["target"] == "x" and row["channel"] == "score")
            or (row["target"] in STEMS and row["channel"] in FIELDS))
    if kind == "revoke":
        return key == "ki" and row["subject"] in ACTORS
    if kind in ("modify", "reset"):
        base, version = row["base"], row["version"]
        return (base in VERSIONS and version in VERSIONS and base[0] == version[0]
                and int(version[-1]) == int(base[-1]) + 1 and row["channel"] in FIELDS
                and ((key == "ki") if kind == "reset" else
                     (type(row["value"]) is int and row["value"] in (0, 1))))
    if kind == "read":
        return key == "kj" and row["version"] in VERSIONS and (
            row["parent"] is None or row["parent"] in VERSIONS)
    if row["version"] != "x@1":
        return False
    if kind == "produce":
        return key != "ki" and type(row["value"]) is int and row["value"] in range(4)
    return key == "kj" and row["policy"] == POLICY and (kind != "bind" or row["root"] in VERSIONS)


def coordinates(rows):
    fixed = {r["rank"]: r for r in rows if r["rank"] is not None}
    pending = [r for r in rows if r["rank"] is None]
    if len(fixed) + len(pending) != len(rows):
        return
    for assignment in permutations([n for n in SLOTS if n not in fixed], len(pending)):
        ordered = sorted([*fixed.values(), *({**r, "rank": n} for r, n in zip(pending, assignment))],
                         key=lambda row: row["rank"])
        if all(left["time"] <= right["time"] for left, right in zip(ordered, ordered[1:])):
            yield ordered


def permission(row):
    return row["subject"], row["target"], row["channel"]


def permitted_history(rows, history_closed, dependencies_closed):
    """Existence check for closed histories; sound contradiction subset when open."""
    stages, revocations, permissions, reads = [], set(), set(), {}
    writes, heads = set(), {s: f"{s}@0" for s in STEMS}
    bound = {}
    lifecycle = {r["kind"] for r in rows if r["kind"] in STAGES}
    for row in rows:
        kind, key = row["kind"], row["key"]
        if key in revocations or "adjudicate" in stages:
            return False
        if kind in STAGES:
            stages.append(kind)
            if stages != [s for s in STAGES if s in lifecycle][:len(stages)]:
                return False
        if kind == "revoke":
            if row["subject"] in revocations:
                return False
            revocations.add(row["subject"])
        if kind in ("modify", "reset"):
            if row["version"] in writes:
                return False
            writes.add(row["version"])
        if kind == "read" and "bind" in lifecycle and "bind" not in stages:
            return False
        if not history_closed:
            continue
        if kind in ("grant", "retract"):
            right = permission(row)
            if kind == "grant" and right not in permissions and right[0] not in revocations:
                permissions.add(right)
            elif kind == "retract" and right in permissions:
                permissions.remove(right)
            else:
                return False
        if kind in ("modify", "reset"):
            stem = row["base"][0]
            if (row["base"] != heads[stem] or
                kind == "modify" and (key, stem, row["channel"]) not in permissions):
                return False
            heads[stem] = row["version"]
        if kind == "produce" and row["value"] != 0 and (key, "x", "score") not in permissions:
            return False
        if kind == "bind":
            bound = dict(heads)
            if row["root"] > bound[row["root"][0]]:
                return False
        if kind == "read":
            version, parent = row["version"], row["parent"]
            if stages != list(STAGES[:3]) or version[0] in reads or version > bound[version[0]]:
                return False
            root = next(r["root"] for r in rows if r["kind"] == "bind")
            if (not reads and (version != root or parent is not None)) or (
                reads and parent not in reads.values()):
                return False
            reads[version[0]] = version
    if not history_closed:
        return True
    if stages != list(STAGES):
        return False
    if reads:
        return True
    ranks = {r["rank"] for r in rows}
    bind_rank = next(r["rank"] for r in rows if r["kind"] == "bind")
    return not dependencies_closed and any(i not in ranks for i in range(bind_rank + 1, rows[-1]["rank"]))


def admit(evidence):
    events = evidence["events"]
    closed = evidence["history_closed"]
    deps = evidence["dependencies_closed"]
    if not all(map(shape, events)) or len({r["id"] for r in events}) != len(events):
        return "contradiction", "authenticated_grammar", []
    candidates = (rows for rows in coordinates(events) if permitted_history(rows, closed, deps))
    ordered = next(candidates, None)
    if ordered is None:
        return "contradiction", "no_ordered_completion", []
    if not closed:
        return "incomplete", "history_open", []
    if any(r["rank"] is None for r in events):
        return "incomplete", "unverified_rank", []
    return "settled", "ordered_scoped_history", ordered
