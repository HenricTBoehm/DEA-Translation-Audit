"""Li, Tripunitara & Bizri (2007) -- independent target engine.

RBAC state <UA, PA, RH> (Notation 2, p.10); auth_perms with RH* (p.10);
k-n SSoD policy ssod<P,k> (Notation 1, p.9); safety (Def 3, p.10):
  safe_e(gamma)  iff  no k-1 users together hold all permissions in P.
Enforcement reading used for event observables: an assignment/activation is permitted iff the
resulting state is safe (the policy is an objective on states; Li p.6 separates policy from mechanism).
"""
import itertools


def closure(RH):
    rel = set(RH)
    changed = True
    while changed:
        changed = False
        for (a, b) in list(rel):
            for (c, d) in list(rel):
                if b == c and (a, d) not in rel:
                    rel.add((a, d))
                    changed = True
    return rel


def auth_perms(UA, PA, RH, u):
    star = closure(RH) | {(r, r) for (_, r) in UA} | {(r, r) for (r, _) in PA}
    out = set()
    for (u2, r1) in UA:
        if u2 != u:
            continue
        for (a, r2) in star:
            if a == r1:
                out |= {p for (r, p) in PA if r == r2}
    return out


def safe(UA, PA, RH, policies):
    users = sorted({u for (u, _) in UA})
    for (P, k) in policies:
        for grp in itertools.combinations(users, min(k - 1, len(users))):
            have = set()
            for u in grp:
                have |= auth_perms(UA, PA, RH, u)
            if set(P) <= have:
                return False
    return True
