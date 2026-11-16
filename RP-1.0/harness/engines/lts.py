"""Basin, Burri & Karjoth (obstruction-free authorization enforcement, extended version) --
independent trace-semantics engine (labelled transition system view of a CSP process).

Workflow process: LTS (states, init, transitions (src, event, dst)); authorization: event -> users.
An event occurrence is authorised iff some user is authorised for it.
  * Native (Def 7 analogue, manuscript p.14): OBSTRUCTED iff some authorised trace leads to a state
    in which an enabled event has no authorised user.
  * Regime B (declared extension): termination event TICK is enabled exactly in goal states;
    goal-relative non-admissibility := no authorised trace ends with TICK.
Implementation enumerates WORDS over the event alphabet up to a length bound and replays them;
it does not perform state-graph search (independent of the DEA evaluator's BFS).
"""
import itertools

TICK = "TICK"


def replay(lts, word):
    s = lts["init"]
    for ev in word:
        nxt = [d for (a, e, d) in lts["trans"] if a == s and e == ev]
        if not nxt:
            return None
        s = nxt[0]          # deterministic in this audit's model classes (<=1 edge per ordered pair+label)
    return s


def authorised_words(lts, maxlen):
    alphabet = sorted({e for (_, e, _) in lts["trans"]})
    for n in range(maxlen + 1):
        for w in itertools.product(alphabet, repeat=n):
            if all(lts["auth"].get(e) for e in w) and replay(lts, w) is not None:
                yield w


def tick_reachable(lts, maxlen):
    for w in authorised_words(lts, maxlen):
        if replay(lts, w) in lts["goals"]:
            return True
    return False


def obstructed(lts, maxlen):
    for w in authorised_words(lts, maxlen):
        s = replay(lts, w)
        if any(a == s and not lts["auth"].get(e) for (a, e, _) in lts["trans"]):
            return True
    return False
