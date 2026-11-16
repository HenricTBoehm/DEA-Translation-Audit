"""Ahn & Sandhu (1999) RSL99 -- independent target engine for RFOPL sentences (pp.48-51).

RFOPL (p.48-51): a (possibly empty) prefix of universal quantifiers over sets, followed by a
predicate over RSL99 terms; no free variables, no existential quantifiers.  Structures are single
snapshots (p.47: 'We consider one snapshot in a system at a time and SOD properties are applied only
to that snapshot'; UA, PA, RH do not change).
Size bounds |X| <= k are in the grammar (Fig. 3: size ::= phi | 1 | ... | N).

AST:
  ('forall', var, setterm, body)  ('leq', setterm, k)  ('and', a, b)  ('implies', a, b)
  set terms: ('set', NAME) | ('var', v) | ('app', fn, setterm) | ('inter', t1, t2)
  functions on elements are lifted to sets by union (p.48 convention).
"""


class Snapshot:
    def __init__(self, sets, UA, PA=(), RH=()):
        self.sets = {k: [frozenset(x) if isinstance(x, (set, frozenset, list, tuple)) else x for x in v]
                     for k, v in sets.items()}
        self.UA, self.PA = set(UA), set(PA)          # PA subset of P x R (Fig. 1)
        rel = set(RH)                                 # (senior, junior); RH is a partial order (p.47)
        changed = True
        while changed:
            changed = False
            for (a, b) in list(rel):
                for (c, d) in list(rel):
                    if b == c and (a, d) not in rel:
                        rel.add((a, d)); changed = True
        self.RHstar = rel

    def fn(self, name, x):
        if name == "roles":       # roles(u) = {r | (u,r) in UA}   (Fig. 1, no hierarchy here)
            return {r for (u, r) in self.UA if u == x}
        if name == "roles*":      # roles*(u) = {r | exists r' >= r, (u,r') in UA}  (Fig. 1)
            direct = {r for (u, r) in self.UA if u == x}
            return direct | {j for (s_, j) in self.RHstar if s_ in direct}
        if name == "user":        # user(r) = {u | (u,r) in UA}
            return {u for (u, r) in self.UA if r == x}
        if name == "permissions":
            return {p for (p, r) in self.PA if r == x}
        raise ValueError(name)


def term(S, t, env):
    k = t[0]
    if k == "set":
        return set(S.sets[t[1]])
    if k == "var":
        v = env[t[1]]
        return set(v) if isinstance(v, frozenset) else {v}
    if k == "app":
        out = set()
        for x in term(S, t[2], env):
            out |= S.fn(t[1], x)
        return out
    if k == "inter":
        return term(S, t[1], env) & term(S, t[2], env)
    raise ValueError(k)


def sat(S, f, env=None):
    env = env or {}
    k = f[0]
    if k == "forall":
        return all(sat(S, f[3], {**env, f[1]: x}) for x in term_elems(S, f[2], env))
    if k == "leq":
        return len(term(S, f[1], env)) <= f[2]
    if k == "and":
        return sat(S, f[1], env) and sat(S, f[2], env)
    if k == "implies":
        return (not sat(S, f[1], env)) or sat(S, f[2], env)
    raise ValueError(k)


def term_elems(S, t, env):
    if t[0] == "set":
        return list(S.sets[t[1]])
    if t[0] == "var":
        v = env[t[1]]
        return list(v) if isinstance(v, frozenset) else [v]
    return list(term(S, t, env))


# Table 1, property 1 (SSOD-CR) after Reduction (p.48): for all u in U, cr in CR: |roles(u) & cr| <= 1
def SSOD_CR(k=1):
    return ("forall", "u", ("set", "U"), ("forall", "cr", ("set", "CR"),
            ("leq", ("inter", ("app", "roles", ("var", "u")), ("var", "cr")), k)))


# Table 1, property 5 component (SSOD-CU): for all cr in CR, cu in CU: |user(cr) & cu| <= 1
def SSOD_CU():
    return ("forall", "cr", ("set", "CR"), ("forall", "cu", ("set", "CU"),
            ("leq", ("inter", ("app", "user", ("var", "cr")), ("var", "cu")), 1)))


# Table 1, property 2 (MOD-CP) after Reduction: for all u in U, cp in CP: |permissions(roles*(u)) & cp| <= 1
def MOD_CP():
    return ("forall", "u", ("set", "U"), ("forall", "cp", ("set", "CP"),
            ("leq", ("inter", ("app", "permissions", ("app", "roles*", ("var", "u"))), ("var", "cp")), 1)))
