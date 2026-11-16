"""Construct public assessor records and project their evidence-only wire views."""
import json

from oracle import FIELDS

POLICY = "sum-thresholds@1"


def event(at, kind, key, **attrs):
    return {"id": at, "kind": kind, "key": key, "time": at, "rank": at, **attrs}


def grant(at, subject, target, channel="threshold"):
    return event(at, "grant", "ki", subject=subject, target=target, channel=channel)


def write(at, key, base, version, channel="threshold", value=1):
    return event(at, "modify", key, base=base, version=version, channel=channel, value=value)


def reset(at, base, version, channel="threshold"):
    return event(at, "reset", "ki", base=base, version=version, channel=channel)


def revoke(at, key):
    return event(at, "revoke", "ki", subject=key)


def trace(*changes, root="r@0", extras=(), signer="ka", root_read=None):
    production = event(4, "produce", signer, version="x@1", value=0)
    seal = event(7, "seal", "kj", version="x@1", policy=POLICY)
    bind = event(8, "bind", "kj", version="x@1", policy=POLICY, root=root)
    primary = event(10, "read", "kj", version=root_read or root, parent=None)
    reads = [event(rank, "read", "kj", version=version, parent=parent)
             for rank, (version, parent) in enumerate(extras, 11)]
    end = event(14, "adjudicate", "kj", version="x@1", policy=POLICY)
    rows = [grant(0, "ka", "x", "score"), *changes, production, seal, bind, primary, *reads, end]
    return sorted(rows, key=lambda row: row["id"])


def altered(rows, eid, **changes):
    return [{**row, **changes} if row["id"] == eid else row for row in rows]


def fixture(name, rows, expected_truth, expected, *, omit=(), patch=None,
            history_closed=True, dependencies_closed=True, premise="SUPPORTED",
            synthetic_truth=None):
    visible = rows if patch is None else patch
    return {
        "label": name, "world": {"events": synthetic_truth if synthetic_truth is not None else rows},
        "expected_truth": expected_truth, "expected": expected, "premise": premise,
        "evidence": {"history_closed": history_closed, "dependencies_closed": dependencies_closed,
                     "events": [row for row in visible if row["id"] not in omit]},
    }


def wire(evidence):
    # The evidence object comes from the authenticated assertion boundary.
    if set(evidence) != {"history_closed", "dependencies_closed", "events"} or any(
        type(evidence[field]) is not bool for field in ("history_closed", "dependencies_closed")
    ) or not isinstance(evidence["events"], list):
        raise ValueError("out-of-profile evidence envelope")
    common = {"id", "kind", "key", "time", "rank"}
    for row in evidence["events"]:
        if not isinstance(row, dict) or not isinstance(row.get("kind"), str) or row["kind"] not in FIELDS:
            raise ValueError("out-of-profile event shape")
        if set(row) != common | FIELDS[row["kind"]] or any(
            value is not None and type(value) not in (str, int) for value in row.values()
        ):
            raise ValueError("out-of-profile event fields")
    def encode(obj):
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return encode({**evidence, "events": sorted(evidence["events"], key=encode)}).encode()


def cases():
    k1_clean = trace(grant(1, "ka", "s"))
    k1_used = trace(grant(1, "ka", "s"), extras=(("s@0", "r@0"),))
    k2_p = trace(grant(1, "ka", "r"))
    k2_q = trace(grant(1, "kq", "r"))
    k3_p = trace(grant(1, "ka", "r"), grant(2, "kq", "r"),
                 write(3, "ka", "r@0", "r@1"), revoke(5, "ka"), root="r@1")
    k3_q = trace(grant(1, "ka", "r"), grant(2, "kq", "r"),
                 write(3, "kq", "r@0", "r@1"), revoke(5, "ka"), root="r@1")
    C, N, U, I = "CONFLICT", "NO_CONFLICT", "UNDETERMINED", "MODEL_INVALID"
    common = [
        fixture("K1-F", k1_used, C, C), fixture("K1-C", k1_clean, N, "CLEAR"),
        fixture("K2-F", k2_p, C, C), fixture("K2-C", k2_q, N, "CLEAR"),
        fixture("K3-F", k3_p, C, C), fixture("K3-C", k3_q, N, "CLEAR"),
    ]
    for n, true, false, omitted in [(1, k1_used, k1_clean, 11), (2, k2_p, k2_q, 1), (3, k3_p, k3_q, 3)]:
        for suffix, world, actual in [("a", true, C), ("b", false, N)]:
            common.append(fixture(f"K{n}-I-{suffix}", world, actual, U, omit=(omitted,),
                                  history_closed=n == 1, dependencies_closed=False, premise="OPEN"))
    wrong_order = altered(k1_used, 7, rank=3, time=3)
    common += [fixture("X-ORDER", wrong_order, I, "INVALID"),
               fixture("X-TRUST", k1_used, C, "CLEAR", omit=(11,), premise="CONTRADICTED")]
    model = [
        fixture("M1-material", trace(grant(1, "ka", "r"), write(2, "ka", "r@0", "r@1"),
                                    root="r@1"), C, C),
        fixture("M2-cosmetic", trace(grant(1, "ka", "r", "layout"),
                                    write(2, "ka", "r@0", "r@1", channel="layout"), root="r@1"), N, "CLEAR"),
        fixture("M3-dynamic-hidden", k1_used, C, U, omit=(11,), dependencies_closed=False, premise="OPEN"),
        fixture("M3-indirect", trace(grant(1, "ka", "t"),
                                    extras=(("s@0", "r@0"), ("t@0", "s@0"))), C, C),
        fixture("M4-signature-only", trace(grant(1, "ka", "r"))[1:], N, "CLEAR"),
        fixture("M5-retract-effect", trace(grant(1, "ka", "r"), write(3, "ka", "r@0", "r@1"),
                                         event(5, "retract", "ki", subject="ka", target="r",
                                               channel="threshold"), root="r@1"), C, C),
        fixture("revoked-write", trace(grant(1, "ka", "r"), revoke(5, "ka"),
                                       write(6, "ka", "r@0", "r@1"), root="r@1"), I, "INVALID"),
        fixture("missing-rank", k3_p, C, U, patch=altered(k3_p, 7, rank=None)),
        fixture("contradictory-rank", k3_p, C, "INVALID", patch=altered(k3_p, 7, rank=2)),
        fixture("outside-rank", k3_p, C, "INVALID", patch=altered(k3_p, 14, rank=16)),
        fixture("unverified-rank-ignored", k3_p, C, U, patch=altered(k3_p, 7, rank=None)),
        fixture("missing-history-record", k3_p, C, U, omit=(7,), history_closed=False, premise="OPEN"),
        fixture("open-history-but-contradiction", wrong_order, I, "INVALID",
                history_closed=False, dependencies_closed=False, premise="OPEN"),
        fixture("same-time-resolved", altered(k3_p, 5, time=4), C, C),
        fixture("post-binding-other-version", trace(grant(1, "ka", "r"),
                                                   write(9, "ka", "r@0", "r@1"),
                                                   root_read="r@1"), I, "INVALID"),
        fixture("frozen-read-original", trace(grant(1, "ka", "r"),
                                             write(9, "ka", "r@0", "r@1")), C, C),
        fixture("partial-reset", trace(grant(1, "ka", "r"), write(3, "ka", "r@0", "r@1"),
                                      revoke(5, "ka"), reset(6, "r@1", "r@2", "layout"),
                                      root="r@2"), C, C),
        fixture("complete-reset", trace(grant(1, "ka", "r"), write(3, "ka", "r@0", "r@1"),
                                       revoke(5, "ka"), reset(6, "r@1", "r@2"), root="r@2"), N, "CLEAR"),
        fixture("reset-unbound", trace(grant(1, "ka", "r"), write(3, "ka", "r@0", "r@1"),
                                      revoke(5, "ka"), reset(6, "r@1", "r@2"), root="r@1"), C, C),
        fixture("open-global-proved-positive", k2_p, C, C, dependencies_closed=False, premise="OPEN"),
        fixture("open-no-positive", k2_p, C, U, omit=(1,), history_closed=False,
                dependencies_closed=False, premise="OPEN"),
        fixture("open-root-no-free-rank", k1_clean, N, "INVALID", omit=(10,),
                patch=altered(k1_clean, 14, rank=9), dependencies_closed=False),
        fixture("two-witness-versions", trace(grant(1, "ka", "t"), grant(2, "ka", "s"),
                                               root="t@0", extras=(("s@0", "t@0"),)), C, C),
        fixture("duplicate-id", k1_clean, N, "INVALID", patch=altered(k1_clean, 7, id=4)),
    ]
    return common + model
