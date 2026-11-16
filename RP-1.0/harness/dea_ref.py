"""DEA v0.3.4.3 reference evaluator (baseline: Architecture Closure Candidate, 15 Nov 2026).

Printed-page references:
  Ctrl_theta  p.8-9  (reflexive-transitive closure of direct-control edges 'during the stage';
                      historical versions bound to the record; TCB not exempt; shared weights,
                      read-only access, independent pre-stage manifest are not edges)
  Eq.(11)-(13) p.9; Eq.(16) p.10 (guard for EVERY s in Sigma_adj); Eqs.(31)-(33) p.14
  Ledger p.12-13; NAP Eqs.(46)-(47) p.17-18; diagnostic classes p.19.
The closure timing of Ctrl_theta is NOT fixed by p.8; both readings are implemented:
  'A' per-instant closure, 'B' closure of the union of edges active in the window.
"""
from collections import deque

# ---------------------------------------------------------------- H_EJ / Eq.16 (identity control)
def ej_effective(m, ctrl=None):
    """m: n, exec[k], adj[k], disp[k], grants[(u,k,s)]. ctrl: optional {identity: set(principals)}.
    Effective iff AuthorizedForDisposition and not ExecConflict (all dispositions)."""
    g = {tuple(x) for x in m["grants"]}
    c = ctrl or {}
    out = set()
    for k in range(m["n"]):
        j, a, s = m["adj"][k], m["exec"][k], m["disp"][k]
        conflict = bool(c.get(j, {j}) & c.get(a, {a}))
        if (j, k, s) in g and not conflict:
            out.add(k)
    return frozenset(out)


# ---------------------------------------------------------------- T3 / H_DE^ext
def t3_permitted(m):
    """permitted acceptances k (T3 only, Eq.31): not (scope == exec_k == acc_k)."""
    return frozenset(k for k in range(len(m["exec"]))
                     if not (m["scope"] == m["exec"][k] == m["acc"][k]))


def de_permitted(m):
    """Eq.33 / p.14: external effect permitted iff scope != ext, or an independent gate (not the
    scoping authority, not self-conferred) took effect before e."""
    ok = m["scope"] != m["ext"] or (m["gate"] not in ("nu", None) and m["gate"] != m["scope"])
    return frozenset(["ext"]) if ok else frozenset()


# ---------------------------------------------------------------- Ctrl_theta
def _closure(nodes, edges):
    c = {n: {n} for n in nodes}
    changed = True
    while changed:
        changed = False
        for (s, t) in edges:
            for n in nodes:
                if s in c[n] and t not in c[n]:
                    c[n].add(t)
                    changed = True
    return c


def ctrl_window(nodes, edges_at, window, semantics):
    if semantics == "A":
        out = {n: set() for n in nodes}
        for t in window:
            cl = _closure(nodes, edges_at(t))
            for n in nodes:
                out[n] |= cl[n]
        return out
    union = set()
    for t in window:
        union |= set(edges_at(t))
    return _closure(nodes, union)


def exec_conflict(nodes, edges_at, wE, wJ, a, j, semantics):
    cE = ctrl_window(nodes, edges_at, wE, semantics)
    cJ = ctrl_window(nodes, edges_at, wJ, semantics)
    return any(j in cJ[p] and a in cE[p] for p in nodes)


# ---------------------------------------------------------------- Ledger (p.12-13)
def ledger(events, B):
    """events: ('cont', wf, case, blocker) | ('term', wf, case, blocker) |
    ('reopen', wf, case, blocker, independent).  Returns indices of granted continuations."""
    bal, closed, out = {}, set(), set()
    for i, e in enumerate(events):
        k = (e[2], e[3])
        if e[0] == "cont":
            if e[3] is None:                 # next stage addressing no recorded blocker (L4)
                out.add(i)
                continue
            bal.setdefault(k, B)
            if k not in closed and bal[k] > 0:
                bal[k] -= 1
                out.add(i)
        elif e[0] == "term":
            closed.add(k)
        elif e[0] == "reopen":
            if k in closed and e[4]:
                closed.discard(k)
                bal[k] = B
    return frozenset(out)


def case_of(objs):
    """Case(x) (p.12): classes under recorded DerivedFrom, identical content, same bound locator.
    objs: list of dicts oid, content, locator, derived_from. Returns {oid: case id}."""
    parent = {o["oid"]: o["oid"] for o in objs}

    def f(a):
        while parent[a] != a:
            a = parent[a]
        return a
    for o in objs:
        if o.get("derived_from") in parent:
            parent[f(o["oid"])] = f(o["derived_from"])
    for i, x in enumerate(objs):
        for y in objs[i + 1:]:
            if x["content"] == y["content"] or x["locator"] == y["locator"]:
                parent[f(x["oid"])] = f(y["oid"])
    return {o["oid"]: f(o["oid"]) for o in objs}


# ---------------------------------------------------------------- NAP (Eqs. 46-47)
def nap(m):
    seen, dq = {m["start"]}, deque([m["start"]])
    while dq:
        s = dq.popleft()
        for (_, a, b, ok) in m["edges"]:
            if a == s and ok and b not in seen:
                seen.add(b)
                dq.append(b)
    return frozenset(["NAP"]) if not (seen & set(m["goals"])) else frozenset()


def nap_diagnostic(m, depth):
    """p.19 classes: 'witness', 'verified_nap', 'undetermined' under a depth bound."""
    frontier, seen = [m["start"]], {m["start"]}
    for _ in range(depth + 1):
        if any(s in m["goals"] for s in frontier):
            return "witness"
        nxt = [b for s in frontier for (_, a, b, ok) in m["edges"] if a == s and ok and b not in seen]
        if not nxt:
            return "verified_nap"
        seen |= set(nxt)
        frontier = nxt
    return "undetermined"
