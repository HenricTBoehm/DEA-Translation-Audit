"""Independent order search and backward influence derivation.

Shares the data contract, immutable-claim checks and attestation interpretation;
uses no forward replay, closure routine, or ordering test from the reference.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import product

from p01 import (CHANNELS, CLEAR, CONFLICT, INVALID, LIFECYCLE, UNKNOWN, VALID,
                 art, canonical, coordinate, initial_tokens, normalize, record_gaps,
                 target, verified_reset)


def can_complete(lifecycle, start, rows):
    """Enumerate positions for the three lifecycle slots in a finite representative grid."""
    ticks = sorted({start, *(e["time"] for e in rows if e.get("time", -1) >= start)})
    taken = {coordinate(e): e["id"] for e in rows if "time" in e and "order" in e}
    slots = [lifecycle.get(kind, {}) for kind in LIFECYCLE]

    def candidates(e):
        for time in ([e["time"]] if "time" in e else ticks):
            if time < start:
                continue
            fixed = sorted(rank for tick, rank in taken if tick == time)
            if "order" in e:
                ranks = [Fraction(e["order"])]
            else:
                bounds = [fixed[0] - 1, *fixed, fixed[-1] + 1] if fixed else [Fraction(0), Fraction(1)]
                ranks = [a + (b - a) * n / 4 for a, b in zip(bounds, bounds[1:]) for n in (1, 2, 3)]
            for rank in ranks:
                pos = time, rank
                if pos not in taken or taken[pos] == e.get("id"):
                    yield pos

    return any(x < y < z for x, y, z in product(*(tuple(candidates(e)) for e in slots)))


def backward_sets(case, trace, life, refs):
    """Prove membership per principal from a target and event prefix backwards."""
    producer = "principal", canonical(case, life["produce"]["actor"])
    judge = "principal", canonical(case, life["adjudicate"]["actor"])
    output = art(case["artifact"])
    seed_tokens = {(p, obj, ch) for p, obj, ch, _ in initial_tokens(case)}
    principals = {p for p, _, _ in seed_tokens} | {producer[1], judge[1]}
    for event in trace:
        if event["kind"] == "control" and not event.get("src_artifact"):
            principals.add(canonical(case, event["src"]))

    @lru_cache(None)
    def survives(principal, obj, channel, count):
        if count == 0:
            return (principal, obj, channel) in seed_tokens
        event = trace[count - 1]
        if (event["kind"] == "reset" and verified_reset(event)
                and target(case, event, "target") == obj and channel in event["channels"]):
            return False
        if (event["kind"] == "control" and event["persistence"] == "potential_durable"
                and event["channel"] == channel and target(case, event, "dst") == obj):
            if attributable(principal, target(case, event, "src"), count - 1):
                return True
        return survives(principal, obj, channel, count - 1)

    def attributable(principal, obj, count):
        return obj == ("principal", principal) or any(
            survives(principal, obj, channel, count) for channel in CHANNELS
        )

    production, seal = (next(i for i, event in enumerate(trace) if event["id"] == life[k]["id"])
                        for k in ("produce", "seal"))
    production_queries = [(art(ref), production) for ref in life["produce"]["inputs"]]
    production_queries.extend((obj, count) for obj, count in
                              product((producer, output), range(production + 1, seal + 1)))
    px = {p for p in principals if any(attributable(p, obj, n) for obj, n in production_queries)}
    targets = {judge, *(art(ref) for ref in refs)}
    reviewers = {obj: {p for p in principals if attributable(p, obj, len(trace))} for obj in targets}
    return px, reviewers


def evaluate(case):
    events, life, problems, missing = normalize(case)
    if problems:
        return INVALID, INVALID, set(), set(), set()
    if not can_complete(life, case["record_start"], events.values()):
        return INVALID, INVALID, set(), set(), set()
    if missing:
        return UNKNOWN, UNKNOWN, set(), set(), set()
    end = coordinate(life["adjudicate"])
    trace = sorted((e for e in events.values() if case["record_start"] <= e["time"] and coordinate(e) < end),
                   key=coordinate)
    refs = set(life["adjudicate"]["roots"].values())
    while True:
        expanded = refs | {link["to"] for link in case.get("dependencies", ())
                           if link.get("authenticated") is True and link["from"] in refs}
        if expanded == refs:
            break
        refs = expanded
    px, sets = backward_sets(case, trace, life, refs)
    shared = {(p, obj) for obj, principals in sets.items() for p in px & principals}
    verdict = CONFLICT if shared else UNKNOWN if record_gaps(case, trace) else CLEAR
    return VALID, verdict, px, set().union(*sets.values()), shared
