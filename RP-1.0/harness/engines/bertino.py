"""Bertino, Ferrari & Atluri (1999) constraint-base semantics -- independent target engine.

Native vocabulary (TISSEC 2(1)): Table I role/2, belong/2 (glb/lub/order unused here);
Table II executeu/3, executer/3, abort/2, success/2; Table III cannot_dou/2, cannot_dor/2,
must_executeu/2, must_executer/2, panic/0; Table IV aggregates (count, max); comparison literals.
Rule classes Defs 4.1-4.4: explicit (facts), assignment (heads cannot_*/must_*), integrity (panic).
Prop. 4.1: a CB is a stratified normal program (evaluated with engines.datalog).

Runtime semantics used here (Sections 2 and 5, simplified to the observables of this audit):
  * user u is authorized for task T iff exists R: role(R,T) and belong(u,R) (Def 2.1, no role order);
  * a requested activation of T by u is PREVENTED iff cannot_dou(u,T), or cannot_dor(R,T) with
    belong(u,R), is derivable from CB + specification facts + execution history (+ request facts);
  * if not prevented, executeu(u,T,k) and success(T,k) are added (k = next activation of T);
  * DETECTION: panic is evaluated after each execution and reported separately (never as enforcement).
"""
from . import datalog

NATIVE_SPEC = {"role", "belong", "glb", "lub"}
NATIVE_EXEC = {"executeu", "executer", "abort", "success"}
NATIVE_HEADS = {"cannot_dou", "cannot_dor", "must_executeu", "must_executer", "panic"}


class RegimeViolation(Exception):
    pass


def _preds(lits):
    for l in lits:
        if l[0] in "+-":
            yield l[1]
        elif l[0] == "count":
            yield from _preds(l[1])
        elif l[0] == "max":
            yield from _preds(l[2])


def validate(rules, facts, regime, aux=()):
    aux = set(aux)
    body_ok = NATIVE_SPEC | NATIVE_EXEC | (aux if regime == "B" else set())
    head_ok = NATIVE_HEADS | (aux if regime == "B" else set())
    for h, _, body in rules:
        if h not in head_ok:
            raise RegimeViolation(f"head {h} not admissible in regime {regime}")
        for p in _preds(body):
            if p not in body_ok:
                raise RegimeViolation(f"body predicate {p} not admissible in regime {regime}")
    for p, _ in facts:
        if p not in NATIVE_SPEC | NATIVE_EXEC | (aux if regime == "B" else set()):
            raise RegimeViolation(f"fact predicate {p} not admissible in regime {regime}")
    if regime == "A":
        heads = {h for h, _, _ in rules}
        for _, _, body in rules:
            if heads & set(_preds(body)):
                raise RegimeViolation("regime A: native heads may not occur in bodies")


class Instance:
    """One Bertino workflow instance with its constraint base CB(W) (Def 4.7)."""

    def __init__(self, spec_facts, rules, regime, aux=()):
        validate(rules, spec_facts, regime, aux)
        self.spec = set((p, tuple(a)) for p, a in spec_facts)
        self.rules = rules
        self.regime, self.aux = regime, set(aux)
        self.hist = set()
        self.nact = {}

    def authorized(self, u, T):
        roles = {a[0] for p, a in self.spec if p == "role" and a[1] == T}
        return any(("belong", (u, R)) in self.spec for R in roles)

    def request(self, u, T, request_facts=(), post_facts=()):
        """Returns dict(permitted, prevented_by, panic_after)."""
        ok = NATIVE_SPEC | NATIVE_EXEC | (self.aux if self.regime == "B" else set())
        for p, _ in request_facts:
            if p not in ok:
                raise RegimeViolation(f"request fact {p} not admissible in regime {self.regime}")
        db = datalog.evaluate(self.spec | self.hist | set(request_facts), self.rules)
        if not self.authorized(u, T):
            return {"permitted": False, "reason": "not_authorized", "panic_after": None}
        blocked = (u, T) in db.get("cannot_dou", set())
        for (R, T2) in db.get("cannot_dor", set()):
            if T2 == T and ("belong", (u, R)) in self.spec:
                blocked = True
        if blocked:
            return {"permitted": False, "reason": "cannot_do", "panic_after": None}
        k = self.nact.get(T, 0) + 1
        self.nact[T] = k
        self.hist |= {("executeu", (u, T, k)), ("success", (T, k))}
        pf = set(post_facts(k) if callable(post_facts) else post_facts)
        for p, _ in pf:
            if p not in ok:
                raise RegimeViolation(f"post fact {p} not admissible in regime {self.regime}")
        self.hist |= pf
        db2 = datalog.evaluate(self.spec | self.hist, self.rules)
        return {"permitted": True, "reason": "ok", "panic_after": bool(db2.get("panic"))}
