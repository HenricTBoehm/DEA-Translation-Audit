"""Generic bottom-up stratified Datalog with negation, comparisons and count/max aggregates.

Independent target engine (does not import the DEA reference evaluator).
Terms: variables are str starting with an uppercase letter and containing no '_' (e.g. U, K2, Bd), or
exactly '_'; everything else (e.g. 'T_adj', 'R_c', 'a') is a constant.
Literals:
  ('+', pred, args)                 positive atom
  ('-', pred, args)                 negated atom (safe: variables bound earlier)
  ('cmp', op, t1, t2)               op in < <= > >= == !=
  ('count', [literals], N)          N := number of distinct answers of the conjunction
                                    (outer-bound variables act as group-by)
  ('max', V, [literals], M)         M := max value of V over answers; literal fails if no answer
Rules: (head_pred, head_args, [literals]).  Facts: set of (pred, tuple).
"""
import operator

OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
       "==": operator.eq, "!=": operator.ne}


def is_var(t):
    return isinstance(t, str) and (t == "_" or (t[:1].isupper() and "_" not in t))


def subst(t, b):
    return b.get(t, t) if is_var(t) else t


def unify(args, tup, b):
    if len(args) != len(tup):
        return None
    nb = dict(b)
    for a, v in zip(args, tup):
        if is_var(a):
            if a == "_":
                continue
            if a in nb:
                if nb[a] != v:
                    return None
            else:
                nb[a] = v
        elif a != v:
            return None
    return nb


def body_preds(lits, neg=False):
    out = []
    for l in lits:
        if l[0] == "+":
            out.append((l[1], neg))
        elif l[0] == "-":
            out.append((l[1], True))
        elif l[0] == "count":
            out += [(p, True) for p, _ in body_preds(l[1])]
        elif l[0] == "max":
            out += [(p, True) for p, _ in body_preds(l[2])]
    return out


def solve(lits, db, b):
    """Yield bindings satisfying the conjunction (literals evaluated in given order)."""
    if not lits:
        yield b
        return
    l, rest = lits[0], lits[1:]
    k = l[0]
    if k == "+":
        args = l[2]
        for tup in db.get(l[1], ()):
            nb = unify(args, tup, b)
            if nb is not None:
                yield from solve(rest, db, nb)
    elif k == "-":
        if any(is_var(a) and a not in b for a in l[2]):
            raise ValueError(f"unsafe negation {l}")
        tup = tuple(subst(a, b) for a in l[2])
        if False:
            raise ValueError(f"unsafe negation {l}")
        if tup not in db.get(l[1], ()):
            yield from solve(rest, db, b)
    elif k == "cmp":
        if any(is_var(t) and t not in b for t in (l[2], l[3])):
            raise ValueError(f"unbound comparison {l}")
        x, y = subst(l[2], b), subst(l[3], b)
        if False:
            raise ValueError(f"unbound comparison {l}")
        if OPS[l[1]](x, y):
            yield from solve(rest, db, b)
    elif k == "count":
        answers = set()
        for nb in solve(l[1], db, b):
            answers.add(tuple(sorted((v, nb[v]) for v in nb if v not in b)))
        n = len(answers)
        var = l[2]
        if is_var(var) and var not in b:
            yield from solve(rest, db, {**b, var: n})
        elif (b[var] if is_var(var) else var) == n:
            yield from solve(rest, db, b)
    elif k == "max":
        vals = [nb[l[1]] for nb in solve(l[2], db, b)]
        if vals:
            yield from solve(rest, db, {**b, l[3]: max(vals)})
    else:
        raise ValueError(k)


def stratify(rules):
    preds = {r[0] for r in rules}
    stratum = {p: 0 for p in preds}
    changed, it = True, 0
    while changed:
        changed, it = False, it + 1
        if it > len(preds) + 2:
            raise ValueError("program not stratifiable")
        for h, _, body in rules:
            for p, neg in body_preds(body):
                if p not in stratum:
                    continue
                need = stratum[p] + (1 if neg else 0)
                if stratum[h] < need:
                    stratum[h] = need
                    changed = True
    return stratum


def evaluate(facts, rules):
    db = {}
    for p, t in facts:
        db.setdefault(p, set()).add(tuple(t))
    st = stratify(rules)
    for level in sorted(set(st.values())):
        layer = [r for r in rules if st[r[0]] == level]
        changed = True
        while changed:
            changed = False
            for h, hargs, body in layer:
                new = set()
                for b in solve(body, db, {}):
                    if any(is_var(a) and a not in b for a in hargs):
                        raise ValueError(f"unsafe head {h}{hargs}")
                    tup = tuple(subst(a, b) for a in hargs)
                    if False:
                        raise ValueError(f"unsafe head {h}{hargs}")
                    if tup not in db.get(h, set()):
                        new.add(tup)
                if new:
                    db.setdefault(h, set()).update(new)
                    changed = True
    return db
