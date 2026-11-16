"""Wang & Li ESORICS 2007 R2BAC -- independent target engine (Defs 1-5, preprint pp.6-7).

NOT the 2010 TISSEC article (unavailable; all 2010 comparisons are SOURCE-UNVERIFIED).

Configuration <U, UR, B>: B maps relation names to sets of user pairs; '=' and '!=' are predefined;
'~name' denotes the complement of 'name' (Def 1).
Workflow <S, order, SA, C>; constraint forms (Def 2):
  ('pair', rho, s1, s2)  ('ex_l', rho, X, s)  ('ex_r', rho, s, X)  ('all_l', rho, X, s)  ('all_r', rho, s, X)
Def 4: valid plan / satisfiability.  Def 5 + p.7 runtime rule: a constraint containing a universal
quantifier is checked whenever a step restricted by it is executed; any other constraint is checked
before the LAST step restricted by it is executed.
"""
import itertools


class Config:
    def __init__(self, users, UR, B):
        self.users = list(users)
        self.UR = set(UR)
        self.B = {k: set(v) for k, v in B.items()}

    def rel(self, name, u, v):
        if name == "=":
            return u == v
        if name == "!=":
            return u != v
        if name.startswith("~"):
            return not self.rel(name[1:], u, v)
        return (u, v) in self.B.get(name, set())


class Workflow:
    def __init__(self, steps, order, SA, C):
        self.steps, self.order, self.SA, self.C = list(steps), set(order), set(SA), list(C)

    def authorized(self, cfg, u, s):
        return any((u, r) in cfg.UR and (r, s) in self.SA for r in {r for (_, r) in cfg.UR})


def steps_of(c):
    f = c[0]
    if f == "pair":
        return {c[2], c[3]}
    if f in ("ex_l", "all_l"):
        return set(c[2]) | {c[3]}
    return {c[2]} | set(c[3])


def holds(cfg, c, P, partial=False):
    """Evaluate constraint c on (partial) plan P: dict step->user. In partial mode, pairs with an
    unassigned step are ignored for universal forms; existential forms need at least one witness among
    assigned steps."""
    f, rho = c[0], c[1]
    g = P.get
    if f == "pair":
        a, b = g(c[2]), g(c[3])
        return True if (a is None or b is None) else cfg.rel(rho, a, b)
    if f == "all_l":
        t = g(c[3])
        return True if t is None else all(cfg.rel(rho, g(x), t) for x in c[2] if g(x) is not None)
    if f == "all_r":
        t = g(c[2])
        return True if t is None else all(cfg.rel(rho, t, g(x)) for x in c[3] if g(x) is not None)
    if f == "ex_l":
        t = g(c[3])
        return True if t is None else any(cfg.rel(rho, g(x), t) for x in c[2] if g(x) is not None)
    if f == "ex_r":
        t = g(c[2])
        return True if t is None else any(cfg.rel(rho, t, g(x)) for x in c[3] if g(x) is not None)
    raise ValueError(f)


def valid_plan(cfg, W, P):
    if set(P) != set(W.steps):
        return False
    if not all(W.authorized(cfg, u, s) for s, u in P.items()):
        return False
    return all(holds(cfg, c, P) for c in W.C)


def satisfiable(cfg, W):
    cands = [[u for u in cfg.users if W.authorized(cfg, u, s)] for s in W.steps]
    for combo in itertools.product(*cands):
        if valid_plan(cfg, W, dict(zip(W.steps, combo))):
            return True
    return False


def runtime(cfg, W, sequence):
    """sequence: list of (user, step) in execution order. Returns list of permitted flags; a refused
    step is not added to the partial plan (Def 5 / p.7 runtime checking)."""
    P, out = {}, []
    order_steps = [s for _, s in sequence]
    for i, (u, s) in enumerate(sequence):
        ok = W.authorized(cfg, u, s)
        if ok:
            P2 = dict(P)
            P2[s] = u
            for c in W.C:
                st = steps_of(c)
                if s not in st:
                    continue
                universal = c[0] in ("all_l", "all_r")
                later = [x for x in order_steps[i + 1:] if x in st and x not in P2]
                if universal or not later:
                    if not holds(cfg, c, P2, partial=True):
                        ok = False
                        break
        out.append(ok)
        if ok:
            P[s] = u
    return out
