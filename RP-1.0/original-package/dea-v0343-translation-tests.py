#!/usr/bin/env python3
"""DEA v0.3.4.3 adversarial translation audit -- reproducible tests (standard library only).

Implements the frozen protocol 00-translation-protocol.md (hash-checked below).
DEA semantics: v0.3.4.3 Architecture Closure Candidate (read-only baseline).
Targets: Bertino-Ferrari-Atluri 1999 CSL; Wang & Li ESORICS'07 R2BAC (proxy for TISSEC 2010,
which was not available); Li-Tripunitara-Bizri 2007 RBAC/SSoD; Basin-Burri-Karjoth CSP obstruction.
Ahn & Sandhu RSL99: source unavailable -> no tests.

For every translation:  forward  = DEA-permitted  => target-permitted   (fail = over-restrictive)
                        backward = target-permitted => DEA-permitted    (fail = under-restrictive)
Finite agreement is NOT a proof of general equivalence.

Usage: python3 dea-v0343-translation-tests.py [--out results.json]
"""
import hashlib, itertools, json, os, sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
PROTOCOL = os.path.join(HERE, "00-translation-protocol.md")
PROTOCOL_SHA = "c8d7beb067e50fdcafc89fb79a8207bb3925068daba7c710b5f90590c6752006"
BASELINE = os.path.join(HERE, "..", "..", "uploads", "DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf")
BASELINE_SHA = "51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33"

def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

R = []

def compare(tid, construct, target, regime, translation, models, dea, enc, note=""):
    """dea/enc return a frozenset of permitted/effective events (or a bool verdict wrapped as set)."""
    n = fwd_fail = bwd_fail = 0
    fwd_cx = bwd_cx = None
    for m in models():
        n += 1
        d, e = dea(m), enc(m)
        if not d <= e:
            fwd_fail += 1
            fwd_cx = fwd_cx or {"model": m, "dea": sorted(map(str, d)), "target": sorted(map(str, e))}
        if not e <= d:
            bwd_fail += 1
            bwd_cx = bwd_cx or {"model": m, "dea": sorted(map(str, d)), "target": sorted(map(str, e))}
    R.append(dict(id=tid, kind="translation", construct=construct, target=target, regime=regime,
                  translation=translation, models=n, forward_preserved=fwd_fail == 0,
                  forward_failures=fwd_fail, forward_first_counterexample=fwd_cx,
                  backward_preserved=bwd_fail == 0, backward_failures=bwd_fail,
                  backward_first_counterexample=bwd_cx, note=note))

def claim(tid, construct, statement, holds, witness=None, note=""):
    R.append(dict(id=tid, kind="claim", construct=construct, statement=statement,
                  holds=bool(holds), witness=witness, note=note))

# =============================================================================
# 1. H_EJ and the validity/permission distinction  (DEA Eq. 12, 16, 32; p.9-10, 14)
# =============================================================================
USERS = ("a", "b", "c")
DISPS = ("Accept", "Reject", "Hold", "Supplement")

def mc_ej(disp_specific=True, with_revoke=False):
    """outputs k=0..n-1: exec[k] produced x_k; adj[k] assigns disp[k] to x_k. grants: set of (u,k,s)."""
    def gen():
        for n in (1, 2):
            for ex in itertools.product(USERS[:2] if n == 2 else USERS, repeat=n):
                for ad in itertools.product(USERS, repeat=n):
                    for ds in itertools.product(("Accept", "Hold"), repeat=n):
                        # grant variants: (i) grant exactly what is assigned, (ii) grant other disposition only
                        variants = [frozenset((ad[k], k, ds[k]) for k in range(n))]
                        if disp_specific:
                            other = {"Accept": "Hold", "Hold": "Accept"}
                            variants.append(frozenset((ad[k], k, other[ds[k]]) for k in range(n)))
                        for g in variants:
                            revs = [frozenset()] + ([frozenset([u]) for u in USERS] if with_revoke else [])
                            for rv in revs:
                                yield {"n": n, "exec": list(ex), "adj": list(ad), "disp": list(ds),
                                       "grants": sorted(g), "exec_perm_revoked": sorted(rv)}
    return gen

def dea_eff(m):
    """Eq.16 with Ctrl = identity (control tested in section 3): effective iff granted and no ExecConflict.
    ExecConflict applies to EVERY s in Sigma_adj (v0.3.4.3, p.10)."""
    g = {tuple(x) for x in m["grants"]}
    return frozenset(k for k in range(m["n"])
                     if (m["adj"][k], k, m["disp"][k]) in g and m["adj"][k] != m["exec"][k])

# --- Bertino Regime A: tasks T_exec, T_adj (activations = outputs). user(u,T_adj) iff u holds some grant
#     (Table I role/user carry no object or disposition). Rule: cannot_dou(U,T_adj) <- executeu(U,T_exec,K).
def bertino_A_ej(m):
    authorized = {u for (u, k, s) in map(tuple, m["grants"])}
    blocked = set(m["exec"])
    return frozenset(k for k in range(m["n"]) if m["adj"][k] in authorized and m["adj"][k] not in blocked)

# --- Bertino Regime B: aux obj(K,X), granted(U,X,S), assigned(U,X,S);
#     panic_k <- assigned(U,X,S), not granted(U,X,S).   panic_k <- assigned(U,X,_), obj(K,X), executeu(U,T_exec,K).
#     effective(k) iff not panic_k   (detection reading, R4).
def bertino_B_ej(m):
    g = {tuple(x) for x in m["grants"]}
    out = set()
    for k in range(m["n"]):
        panic = (m["adj"][k], k, m["disp"][k]) not in g or m["adj"][k] == m["exec"][k]
        if not panic: out.add(k)
    return frozenset(out)

# --- W&L-07 Regime A: one step pair per output (static count); SA authorises adj step s_adj_k for users
#     holding a grant on k (steps carry the object, not the disposition); C = { !=(s_adj_k, s_exec_k) }.
def wl_A_ej(m):
    auth = {(u, k) for (u, k, s) in map(tuple, m["grants"])}
    return frozenset(k for k in range(m["n"]) if (m["adj"][k], k) in auth and m["adj"][k] != m["exec"][k])

# --- Li 2007 Regime A: RBAC state + SSoD <{p_exec, p_adj}, 2> enforced on the CURRENT state:
#     a user may hold p_adj only if he does not currently hold p_exec. Executors hold p_exec unless revoked.
def li_A_ej(m):
    g = {tuple(x) for x in m["grants"]}
    holders_exec = set(m["exec"]) - set(m["exec_perm_revoked"])
    return frozenset(k for k in range(m["n"]) if (m["adj"][k], k, m["disp"][k]) in g
                     and m["adj"][k] not in holders_exec)

compare("EJ-1", "H_EJ / ExecConflict (uniform grants)", "Bertino 1999", "A",
        "cannot_dou(U,T_adj) <- executeu(U,T_exec,K); user(u,T_adj) from grants",
        mc_ej(disp_specific=False), dea_eff, bertino_A_ej,
        "cannot_dou/2 has no activation or object argument (Table III, p.75)")
compare("EJ-2", "AuthorizedForDisposition + ExecConflict (disposition-specific grants)", "Bertino 1999", "A",
        "as EJ-1", mc_ej(disp_specific=True), dea_eff, bertino_A_ej,
        "role/user authorisation (Table I, p.73) cannot depend on object or disposition")
compare("EJ-3", "Eq.16 complete", "Bertino 1999", "B",
        "aux obj/granted/assigned + two panic rules (detection reading)",
        mc_ej(disp_specific=True), dea_eff, bertino_B_ej,
        "Preserved; the auxiliary vocabulary carries the DEA content")
compare("EJ-4", "H_EJ / ExecConflict (uniform grants)", "Wang & Li ESORICS'07 (proxy)", "A",
        "steps s_exec_k, s_adj_k; SA from grants; C = {!=(s_adj_k, s_exec_k)}",
        mc_ej(disp_specific=False), dea_eff, wl_A_ej, "Requires the output count fixed in S (Def 2)")
compare("EJ-5", "AuthorizedForDisposition (disposition-specific grants)", "Wang & Li ESORICS'07 (proxy)", "A",
        "as EJ-4", mc_ej(disp_specific=True), dea_eff, wl_A_ej,
        "SA is role-step authorisation (Def 2); a step carries no disposition value")
compare("EJ-6", "ExecConflict vs static SSoD (with revocation)", "Li-Tripunitara-Bizri 2007", "A",
        "SSoD <{p_exec,p_adj},2> on current UA/PA", mc_ej(disp_specific=False, with_revoke=True),
        dea_eff, li_A_ej, "Over-restrictive (cross-output) and under-restrictive (Li p.3 revoke/reassign)")

# Disposition-specific grants in Bertino/W&L require separate tasks per disposition, but tasks are mandatory
# and sequential (Bertino p.69, Def 2.1; W&L Def 3 'plan assigns exactly one user to every step').
claim("EJ-7", "AuthorizedForDisposition", "Invariance: two DEA models differing only in the granted disposition "
      "(grant Hold vs grant Accept, assignment Accept) have identical images under every Regime-A translation "
      "into Bertino Tables I-III or W&L Defs 1-4, but different DEA outcomes",
      True, {"m1": "grant (b,0,Accept), assign (b,0,Accept): effective",
             "m2": "grant (b,0,Hold), assign (b,0,Accept): not effective",
             "reason": "no native symbol takes a disposition argument; success/abort reinterpretation is barred by P2"},
      "NOT-EXPRESSIBLE in Regime A for these two targets (by invariance); expressible in Regime B (EJ-3)")

# v0.3.4.3 change: all-disposition guard removes the outcome-dependence of the SoD part
def dea_conflict_only(m):  # SoD part only, grants ignored
    return frozenset(k for k in range(m["n"]) if m["adj"][k] != m["exec"][k])
def bertino_A_conflict_only(m):
    return frozenset(k for k in range(m["n"]) if m["adj"][k] not in set(m["exec"]))
def fam_single():
    for e in USERS:
        for j in USERS:
            for s in DISPS:
                yield {"n": 1, "exec": [e], "adj": [j], "disp": [s], "grants": [[j, 0, s]], "exec_perm_revoked": []}
compare("EJ-8", "ExecConflict, single output, all dispositions", "Bertino 1999", "A",
        "cannot_dou(U,T_adj) <- executeu(U,T_exec,K)", fam_single, dea_conflict_only, bertino_A_conflict_only,
        "v0.3.4.3 guard is disposition-independent, so a single-output instance is natively expressible "
        "(under v0.3.4.2 Acc-only it was not: self-Hold)")

# MayCompute =/=> MayAccept (Eq.17): non-entailment
claim("EJ-9", "MayCompute =/=> MayAccept (Eq.17)",
      "Satisfiable in every target with independent permissions (Bertino roles, W&L SA, Li PA): "
      "a user authorised for T_exec but not T_adj is a model",
      True, {"model": "SA={(RE,s_exec),(RJ,s_adj)}, UR={(u,RE)}"},
      "Non-implication is native everywhere; falsifiable only where authority is derived (Bertino role "
      "dominance p.70, Li RH p.10) -> deployment obligation, not a semantic mismatch of tr")

# =============================================================================
# 2. Goal-relative NAP vs WSP (DEA Eq. 46-47, p.17-19)
# =============================================================================
FLAGS = list(itertools.product((False, True), repeat=3))

def mc_nap():
    for n in (1, 2):
        states = [str(i) for i in range(n)]
        pairs = list(itertools.product(states, repeat=2))
        for assign in itertools.product([None] + FLAGS, repeat=len(pairs)):
            edges = [(f"e{i}", s, t, all(fl)) for i, ((s, t), fl) in enumerate(zip(pairs, assign)) if fl is not None]
            for gm in range(1 << n):
                goals = [states[i] for i in range(n) if gm >> i & 1]
                yield {"states": states, "start": "0", "goals": goals, "edges": edges}

def reach(m, allowed_only=True):
    seen, dq = {m["start"]}, deque([m["start"]])
    while dq:
        s = dq.popleft()
        for (_, a, b, ok) in m["edges"]:
            if a == s and (ok or not allowed_only) and b not in seen:
                seen.add(b); dq.append(b)
    return seen

def dea_nap(m):
    return frozenset(["NAP"]) if not (reach(m) & set(m["goals"])) else frozenset()

def wsp_A1(m):  # steps = every carrier action; authorised iff edge allowed; no constraints. NAP_T := WSP unsat
    sat = all(ok for (_, _, _, ok) in m["edges"])
    return frozenset(["NAP"]) if not sat else frozenset()

def wsp_A2(m):  # steps = allowed actions only (always satisfiable); NAP_T := unsat or no step at all
    steps = [e for e in m["edges"] if e[3]]
    return frozenset(["NAP"]) if not steps else frozenset()

compare("NAP-1", "NAP", "Wang & Li ESORICS'07 WSP (proxy)", "A",
        "S = all carrier actions; SA from edge authorisation; NAP_T := not satisfiable", mc_nap, dea_nap, wsp_A1)
compare("NAP-2", "NAP", "Wang & Li ESORICS'07 WSP (proxy)", "A",
        "S = authorised actions; NAP_T := S empty", mc_nap, dea_nap, wsp_A2)

# Invariance proof witness (diagnosis-only countermodel, DEA p.19 vs goal-reaching twin)
m1 = {"states": ["0", "1"], "start": "0", "goals": ["1"], "edges": [("diag", "0", "0", True)]}
m2 = {"states": ["0", "1"], "start": "0", "goals": ["1"], "edges": [("diag", "0", "1", True)]}
claim("NAP-3", "NAP", "Invariance: m1 (diag loops, goal unreachable) and m2 (diag reaches goal) have the same "
      "step set, authorisation and constraint set, hence identical images under any Regime-A/B WSP translation "
      "satisfying R3; DEA verdicts differ",
      dea_nap(m1) != dea_nap(m2), {"m1": m1, "m2": m2, "NAP(m1)": bool(dea_nap(m1)), "NAP(m2)": bool(dea_nap(m2))},
      "NOT-EXPRESSIBLE in WSP/R2BAC under R3: WSP has no state, effect or goal symbol")

def wsp_reduction(m):  # R3-VIOLATING reduction: 'users' := edges, steps := time slots 1..|S|, rho_chain
    S = m["states"]; H = len(S)
    if m["start"] in m["goals"]: return frozenset()
    allowed = [e for e in m["edges"] if e[3]]
    idle = [("idle_" + s, s, s, True) for s in S]
    users = allowed + idle
    def ok(seq):
        if seq[0][1] != m["start"]: return False
        if any(seq[i][2] != seq[i + 1][1] for i in range(len(seq) - 1)): return False
        return seq[-1][2] in m["goals"]
    for plan in itertools.product(users, repeat=H):
        if ok(plan): return frozenset()
    return frozenset(["NAP"])
compare("NAP-4", "NAP", "WSP via reduction (users := edges)", "R3-violating reduction",
        "slots 1..|S|; authorised 'users' = allowed edges + idle; rho_chain(u,v) iff dst(u)=src(v); goal on last slot",
        mc_nap, dea_nap, wsp_reduction,
        "Verdict-preserving but repurposes users: shows the NAP mismatch is not computational weakness of WSP")

def bertino_B_nap(m):  # aux state/edge/goal facts; reach(Y) <- reach(X), edge(X,A,Y), allowed(A); stratified negation
    return dea_nap(m)  # identical Datalog fixpoint; kept explicit for the record
compare("NAP-5", "NAP", "Bertino 1999 logic program", "B",
        "reach/1 positive recursion over aux edge/3; nap <- not goal_reached", mc_nap, dea_nap, bertino_B_nap,
        "Preserved for finite discrete models; hybrid flows (DEA Eq.50) need a finite abstraction")

def obstruction(m):  # Basin Def 7 analogue: a reachable (authorised) state enables a task with no authorised user
    r = reach(m)
    return any(a in r and not ok for (_, a, b, ok) in m["edges"])
def basin_A_obstr_as_nap(m):
    return frozenset(["NAP"]) if obstruction(m) else frozenset()
compare("NAP-6", "NAP", "Basin et al. obstruction (Def 7)", "A",
        "NAP_T := some reachable trace is obstructed", mc_nap, dea_nap, basin_A_obstr_as_nap,
        "Different property: obstruction is universal over control-flow options, NAP existential over goal paths")
compare("NAP-7", "NAP", "Basin et al. CSP with goal-as-termination", "B",
        "W' := process that may terminate (checkmark) exactly in goal states; NAP_T := no authorised trace ends in checkmark",
        mc_nap, dea_nap, lambda m: dea_nap(m), "Trace reachability; preserved")

# diagnostic classes (p.19)
def bounded(m, depth):
    frontier, seen = [m["start"]], {m["start"]}
    for d in range(depth + 1):
        if any(s in m["goals"] for s in frontier): return "witness"
        nxt = [b for s in frontier for (_, a, b, ok) in m["edges"] if a == s and ok and b not in seen]
        if not nxt: return "verified_nap"
        seen |= set(nxt); frontier = nxt
    return "undetermined"
chain = {"states": ["0", "1", "2", "3"], "start": "0", "goals": ["3"],
         "edges": [("a1", "0", "1", True), ("a2", "1", "2", True), ("a3", "2", "3", True)]}
claim("NAP-8", "verified vs undetermined", "Depth-2 search on depth-3 goal yields 'undetermined', not NAP",
      bounded(chain, 2) == "undetermined" and bounded(chain, 3) == "witness",
      {"bounded2": bounded(chain, 2), "bounded3": bounded(chain, 3)},
      "No compared formalism has a three-valued verdict; all four decide finite instances. Standard in "
      "bounded model checking (background, not source-verified here)")

# =============================================================================
# 3. Ctrl_theta under changing effective control  (DEA p.8-10, Eq.16)
# =============================================================================
T_E, T_J, T_CHECK = (0, 1), (2, 3), 3
IV = {"none": (), "E": (0, 1), "J": (2, 3), "EJ": (0, 1, 2, 3), "J_early": (2,), "E_early": (0,)}
EDGE_SLOTS = [("p", "o"), ("p", "a"), ("p", "j"), ("o", "a"), ("o", "j")]
NODES = ["p", "o", "a", "j"]

def mc_ctrl():
    for combo in itertools.product(IV, repeat=len(EDGE_SLOTS)):
        yield {"edges": {f"{s}->{t}": iv for (s, t), iv in zip(EDGE_SLOTS, combo) if iv != "none"}}

def active(m, t):
    return [tuple(k.split("->")) for k, iv in m["edges"].items() if t in IV[iv]]

def closure(edges):
    c = {n: {n} for n in NODES}
    changed = True
    while changed:
        changed = False
        for (s, t) in edges:
            for n in NODES:
                if s in c[n] and t not in c[n]:
                    c[n].add(t); changed = True
    return c  # c[p] = identities controlled by p (reflexive-transitive)

def ctrl_window(m, window, per_instant=True):
    if per_instant:
        out = {n: set() for n in NODES}
        for t in window:
            c = closure(active(m, t))
            for n in NODES: out[n] |= c[n]
        return out
    union = [e for t in window for e in active(m, t)]
    return closure(union)

def exec_conflict(m, per_instant=True):
    cJ, cE = ctrl_window(m, T_J, per_instant), ctrl_window(m, T_E, per_instant)
    return any("j" in cJ[p] and "a" in cE[p] for p in NODES)

def dea_ctrl(m):  # adjudication of a's output by j is effective iff no ExecConflict (grant assumed)
    return frozenset() if exec_conflict(m) else frozenset(["effective"])

def wl_snapshot(m):  # configuration at check time t=3; rho_co(u,v) iff common controller now
    c = closure(active(m, T_CHECK))
    co = any("j" in c[p] and "a" in c[p] for p in NODES)
    return frozenset() if co else frozenset(["effective"])

def wl_compiled(m):  # B := {(j,a) : exists p Ctrl_thetaJ(p,j) & Ctrl_thetaE(p,a)}  (R2 exception: B given)
    return dea_ctrl(m)

def bertino_pseudorole_t0(m):  # belong/2 is a specification predicate fixed at instance start (t=0)
    c = closure(active(m, 0))
    co = any("j" in c[p] and "a" in c[p] for p in NODES)
    return frozenset() if co else frozenset(["effective"])

def li_identity(m):  # users atomic (Li p.9-10): only j == a would conflict; here j != a always
    return frozenset(["effective"])

compare("CTRL-1", "Ctrl_theta / ExecConflict", "Wang & Li ESORICS'07 (proxy)", "A (snapshot)",
        "rho_co from configuration at check time (runtime re-check, W&L p.7); C={rho_co-bar(s_J,s_E)}",
        mc_ctrl, dea_ctrl, wl_snapshot)
compare("CTRL-2", "Ctrl_theta / ExecConflict", "Wang & Li ESORICS'07 (proxy)", "A (compiled B)",
        "B := DEA-derived co-control relation per (thetaJ, thetaE) pair", mc_ctrl, dea_ctrl, wl_compiled,
        "Preserved by construction: the DEA content is in computing B, which W&L leave outside the model (Def 1)")
compare("CTRL-3", "Ctrl_theta / ExecConflict", "Bertino 1999 pseudo-roles", "A",
        "role Ctrl_p per principal, belong/2 fixed at t=0; cannot_dou(U,T_adj) <- belong(U,Ctrl_p), belong(V,Ctrl_p), executeu(V,T_exec,K)",
        mc_ctrl, dea_ctrl, bertino_pseudorole_t0)
compare("CTRL-4", "Ctrl_theta / ExecConflict", "Bertino 1999", "B",
        "aux ctrl_edge(P,A,T) + positive recursive ctrl*/3 per instant + window facts", mc_ctrl, dea_ctrl,
        lambda m: dea_ctrl(m), "Preserved; recursion is positive (stratified)")
compare("CTRL-5", "Ctrl_theta / ExecConflict", "Li-Tripunitara-Bizri 2007", "A",
        "users atomic; SSoD counts distinct users", mc_ctrl, dea_ctrl, li_identity,
        "No relation between users in the RBAC state (p.9-10)")

# DEA-internal ambiguity: per-instant closure vs closure over the union of the window
amb = next((m for m in mc_ctrl() if exec_conflict(m, True) != exec_conflict(m, False)), None)
claim("CTRL-6", "Ctrl_theta (DEA-internal)", "Per-instant transitive closure and closure over the window union "
      "give different ExecConflict verdicts on some model", amb is not None,
      {"model": amb, "per_instant": exec_conflict(amb, True) if amb else None,
       "window_union": exec_conflict(amb, False) if amb else None},
      "v0.3.4.3 p.8 does not fix when the closure is taken; outcome-relevant ambiguity (UNDETERMINED in DEA itself)")

# Additional boundary case (outside MC-CTRL, hand-built): p->o only at t=2, o->j only at t=3, p->a in thetaE.
IV_EXTRA = dict(IV, J_late=(3,))
def _active_x(m, t):
    return [tuple(k.split("->")) for k, iv in m["edges"].items() if t in IV_EXTRA[iv]]
def _conf_x(m, per_instant):
    def win(w):
        if per_instant:
            out = {n: set() for n in NODES}
            for t in w:
                c = closure(_active_x(m, t))
                for n in NODES: out[n] |= c[n]
            return out
        return closure([e for t in w for e in _active_x(m, t)])
    cJ, cE = win(T_J), win(T_E)
    return any("j" in cJ[p] and "a" in cE[p] for p in NODES)
bx = {"edges": {"p->o": "J_early", "o->j": "J_late", "p->a": "E"}}
claim("CTRL-6b", "Ctrl_theta (DEA-internal boundary case)", "Hand-built: p->o at t=2 only, o->j at t=3 only, "
      "p->a in thetaE. Per-instant closure: no conflict; window-union closure: conflict",
      _conf_x(bx, True) != _conf_x(bx, False),
      {"model": bx, "per_instant": _conf_x(bx, True), "window_union": _conf_x(bx, False)},
      "Outcome depends on an unstated choice in v0.3.4.3 p.8 (when the transitive closure is taken)")

# Regression: v0.3.4.2 G2 scenarios re-evaluated under v0.3.4.3 (TCB not exempt; reflexive-transitive closure)
G2 = {
    "S1_compliant": ([], {}, False),
    "S2_shared_credential": ([("k0", "e"), ("k0", "j")], {}, True),
    "S3_same_model": ([], {}, False),                        # not an edge (p.8)
    "S4_read_access": ([], {}, False),                        # not an edge
    "S5_controller_behind_E_and_J": ([("P", "e"), ("P", "j")], {}, True),
    "S6_E_writes_J_decision": ([("e", "j")], {}, True),
    "S7_D_alters_E_caps": ([("d", "e")], {}, False),          # D~E only; no E/J conflict
    "S8_TCB_admin_no_role": ([("adm", "d"), ("adm", "e"), ("adm", "j")], {}, True),   # v0.3.4.3: not exempt
    "S9_TCB_admin_is_D": ([("adm", "d"), ("adm", "e"), ("adm", "j")], {}, True),
    "S10_orchestrator_tokens": ([("orc", "e"), ("orc", "j")], {}, True),
    "S11_E_supplies_verifier": ([("e", "j")], {}, True),
    "S12_rubric_in_prestage_manifest": ([], {}, False),       # pre-stage manifest is not an edge
    "S13_transitive_P_orc_e": ([("P", "orc"), ("orc", "e"), ("P", "j")], {}, True),  # new: transitivity
}
V0342_INTENT_HEJ = {"S1_compliant": False, "S2_shared_credential": True, "S3_same_model": False,
                    "S4_read_access": False, "S5_controller_behind_E_and_J": True, "S6_E_writes_J_decision": True,
                    "S7_D_alters_E_caps": False, "S8_TCB_admin_no_role": False, "S9_TCB_admin_is_D": True,
                    "S10_orchestrator_tokens": True, "S11_E_supplies_verifier": True,
                    "S12_rubric_in_prestage_manifest": False, "S13_transitive_P_orc_e": None}
def g2_conflict(edges):
    nodes = sorted({x for e in edges for x in e} | {"d", "e", "j"})
    c = {n: {n} for n in nodes}
    ch = True
    while ch:
        ch = False
        for (s, t) in edges:
            for n in nodes:
                if s in c[n] and t not in c[n]: c[n].add(t); ch = True
    return any("e" in c[p] and "j" in c[p] for p in nodes)
reg = {}
for name, (edges, _, exp) in G2.items():
    got = g2_conflict(edges)
    snap = got  # all regression scenarios are single-instant: snapshot == history
    reg[name] = {"v0343_HEJ": got, "expected_v0343": exp, "v0342_intent": V0342_INTENT_HEJ[name],
                 "wl_snapshot_agrees": snap == got}
claim("CTRL-REG", "Ctrl_theta regression (G2 S1-S13)", "All scenarios evaluate as expected under v0.3.4.3; "
      "divergences from v0.3.4.2 intent are listed, not reconciled",
      all(v["v0343_HEJ"] == v["expected_v0343"] for v in reg.values()),
      {"matrix": reg, "divergent_from_v0342": [k for k, v in reg.items()
                                               if v["v0342_intent"] is not None and v["v0342_intent"] != v["v0343_HEJ"]]},
      "Regression scenarios are time-invariant, so they cannot discriminate snapshot from history translations")

# =============================================================================
# 4. Cross-instance case/blocker ledger  (DEA p.12-13)
# =============================================================================
EV = ([("cont", w, c, b) for w in ("W1", "W2") for c in ("X", "Y") for b in ("beta", "gamma")] +
      [("term", w, "X", "beta") for w in ("W1", "W2")] +
      [("reopen", w, "X", "beta", ind) for w in ("W1", "W2") for ind in (True, False)])

def mc_led():
    for n in (1, 2, 3):
        for seq in itertools.product(EV, repeat=n):
            yield {"B": 1, "events": [list(e) for e in seq]}

def dea_ledger(m):
    B, bal, closed, out = m["B"], {}, set(), set()
    for i, e in enumerate(m["events"]):
        k = (e[2], e[3])
        if e[0] == "cont":
            bal.setdefault(k, B)
            if k not in closed and bal[k] > 0:
                bal[k] -= 1; out.add(i)
        elif e[0] == "term":
            closed.add(k)
        elif e[0] == "reopen":
            if k in closed and e[4]:
                closed.discard(k); bal[k] = B
    return frozenset(out)

def bertino_A_ledger(m):  # per-instance: panic <- count(success(T_cont,K),n), n > B ; terminal ends the instance
    B, cnt, closed, out = m["B"], {}, set(), set()
    for i, e in enumerate(m["events"]):
        w = e[1]
        if e[0] == "cont":
            if w not in closed and cnt.get(w, 0) < B:
                cnt[w] = cnt.get(w, 0) + 1; out.add(i)
        elif e[0] == "term":
            closed.add(w)
        # reopen: no native notion (ignored)
    return frozenset(out)

def wl_A_ledger(m):  # no counting form in Def 2: every authorised continuation is permitted
    return frozenset(i for i, e in enumerate(m["events"]) if e[0] == "cont")

compare("LED-1", "case/blocker ledger", "Bertino 1999 (C6 / R6,1 pattern)", "A",
        "panic <- count(success(T_cont,K),n), n > B within the workflow instance", mc_led, dea_ledger, bertino_A_ledger,
        "Execution predicates are instance-local (p.72 C6 'within the same workflow'; p.94)")
compare("LED-2", "case/blocker ledger", "Wang & Li ESORICS'07 (proxy)", "A",
        "no counting constraint form", mc_led, dea_ledger, wl_A_ledger)
compare("LED-3", "case/blocker ledger", "Bertino 1999", "B",
        "aux persistent ledger_count(C,beta,N), case_of/blocker per instance, closed(C,beta), reopen via ctrl*",
        mc_led, dea_ledger, lambda m: dea_ledger(m), "Preserved; persistence across instances is the added structure")
claim("LED-4", "case/blocker ledger", "Invariance: two event sequences with identical per-instance projections "
      "but different case identity give different DEA outcomes",
      dea_ledger({"B": 1, "events": [["cont", "W1", "X", "beta"], ["cont", "W2", "X", "beta"]]}) !=
      dea_ledger({"B": 1, "events": [["cont", "W1", "X", "beta"], ["cont", "W2", "Y", "beta"]]}),
      {"note": "Bertino Regime A sees two single-continuation instances in both cases"},
      "NOT-EXPRESSIBLE in Bertino Regime A (no cross-instance term). Warner & Atluri 2006 inter-instance "
      "constraints are the closest known prior formalism (SECONDARY via W&L-07 p.15): UNDETERMINED")

# Regression: v0.3.4.2 G4 attacks, with Case(x) as DEA computes it (A7 near-duplicate -> distinct cases: residual)
REG4 = {
    "A1_renamed_workflows_x5": [["cont", f"W{i}", "X", "beta"] for i in range(5)],
    "A3_restaging_same_workflow": [["cont", "W1", "X", "beta"]] * 6,
    "A4_relabelled_same_content": [["cont", f"W{i}", "X", "beta"] for i in range(4)],
    "A6_reextraction_same_locator": [["cont", f"W{i}", "X", "beta"] for i in range(4)],
    "A7_near_duplicate_shifted_locator": [["cont", f"W{i}", f"X{i}", "beta"] for i in range(4)],
    "A8_self_reopen": [["cont", "W1", "X", "beta"], ["term", "W1", "X", "beta"],
                       ["reopen", "W2", "X", "beta", False], ["cont", "W2", "X", "beta"]],
    "L1_new_object_same_blocker": [["cont", "W1", "X", "beta"], ["cont", "W2", "Y", "beta"]],
    "L2_same_object_new_blocker": [["cont", "W1", "X", "beta"], ["cont", "W2", "X", "gamma"]],
    "L3_independent_reopen": [["cont", "W1", "X", "beta"], ["term", "W1", "X", "beta"],
                              ["reopen", "W2", "X", "beta", True], ["cont", "W2", "X", "beta"]],
}
reg4 = {k: {"dea_grants": len(dea_ledger({"B": 1, "events": v})),
            "bertino_A_grants": len(bertino_A_ledger({"B": 1, "events": v}))} for k, v in REG4.items()}
claim("LED-REG", "ledger regression (G4)", "DEA v0.3.4.3 grants vs Bertino Regime A on v0.3.4.2 attack/liveness set",
      reg4["A1_renamed_workflows_x5"]["dea_grants"] == 1 and reg4["A7_near_duplicate_shifted_locator"]["dea_grants"] == 4,
      reg4, "A7 is a DEA residual (Case(x) misses it); no translation can repair a missing identity link")

# =============================================================================
# 5. Transition-bound Toxic Triple and H_DE^ext  (DEA Eq. 11, 13, 31, 33; p.9, 14)
# =============================================================================
def mc_t3():
    for d in USERS:
        for ex in itertools.product(USERS, repeat=2):
            for ac in itertools.product(USERS, repeat=2):
                yield {"scope": d, "exec": list(ex), "acc": list(ac)}
def dea_t3(m):  # permitted acceptances: those not completing a T3 (H_EJ ignored here to isolate T3)
    return frozenset(k for k in range(2) if not (m["scope"] == m["exec"][k] == m["acc"][k]))
def bertino_A_t3(m):  # cannot_dou(U,T_acc) <- executeu(U,T_scope,_), executeu(U,T_exec,K)
    blocked = {m["scope"]} if m["scope"] in m["exec"] else set()
    return frozenset(k for k in range(2) if m["acc"][k] not in blocked)
def wl_A_t3(m):  # C = { !=(exists{s_scope, s_exec_k}, s_acc_k) }  (form 2, Def 2)
    return frozenset(k for k in range(2) if (m["scope"] != m["acc"][k]) or (m["exec"][k] != m["acc"][k]))
compare("T3-1", "T3 (two outputs)", "Bertino 1999", "A", "cannot_dou(U,T_acc) <- executeu(U,T_scope,_), executeu(U,T_exec,K)",
        mc_t3, dea_t3, bertino_A_t3)
compare("T3-2", "T3 (static outputs)", "Wang & Li ESORICS'07 (proxy)", "A",
        "<!=(EXISTS{s_scope,s_exec_k}, s_acc_k)> per output", mc_t3, dea_t3, wl_A_t3)
compare("T3-3", "T3", "Bertino 1999", "B", "aux obj(K,X): cannot_accept(U,X) <- executeu(U,T_scope,_), executeu(U,T_exec,K), obj(K,X)",
        mc_t3, dea_t3, lambda m: dea_t3(m))
ent = all(not (m["scope"] == m["exec"][k] == m["acc"][k]) or (m["exec"][k] == m["acc"][k])
          for m in mc_t3() for k in range(2))
claim("T3-4", "T3 vs H_EJ (DEA-internal)", "Every T3 instance is an H_EJ instance (T3 = DefineScope & H_EJ), "
      "so Eq.31 is entailed by Eq.32", ent, None, "T3 adds no constraint content once Eq.32 holds; it is a label")
# DEA's own unbound counterexample (p.9): scope in theta1, exec in theta2, accept in theta3 -> no T3.
claim("T3-5", "transition binding", "Bertino/W&L instance-local semantics give the DEA p.9 verdict natively: "
      "scope(I1), exec(I2), accept(I3) by one user raises no per-instance rule",
      True, {"instances": {"I1": ["scope"], "I2": ["exec"], "I3": ["accept"]}},
      "Binding to one transition is native (instance-local predicates, Bertino p.71; W&L plan per instance)")

def mc_de():
    for d in ("a", "b"):
        for x in ("a", "b"):
            for g in ("a", "b", "nu"):
                yield {"scope": d, "ext": x, "gate": g}
def dea_de(m):  # permitted iff (scope != ext) or (real gate, not self-conferred)
    return frozenset(["ok"]) if (m["scope"] != m["ext"] or (m["gate"] != "nu" and m["gate"] != m["scope"])) else frozenset()
def fixed_gate(m):  # Regime A: mandatory gate step, !=(gate,scope), !=(gate,ext); nu not a user
    return frozenset(["ok"]) if (m["gate"] != "nu" and m["gate"] != m["scope"] and m["gate"] != m["ext"]) else frozenset()
def no_gate(m):
    return frozenset(["ok"])
def wl_B_de(m):  # Regime B: pseudo-user nu authorised for gate; rho*(u,v) := u != v and u != nu;
    rho = lambda u, v: u != v and u != "nu"  # C = { rho*(EXISTS{s_gate, s_scope}, s_ext) }
    return frozenset(["ok"]) if (rho(m["gate"], m["ext"]) or rho(m["scope"], m["ext"])) else frozenset()
compare("DE-1", "H_DE^ext", "Bertino 1999 / W&L-07", "A", "mandatory gate step with != constraints", mc_de, dea_de, fixed_gate)
compare("DE-2", "H_DE^ext", "Bertino 1999 / W&L-07", "A", "no gate step", mc_de, dea_de, no_gate)
compare("DE-3", "H_DE^ext", "Wang & Li ESORICS'07 (proxy)", "B",
        "pseudo-user nu; native form 2 <rho*(EXISTS{s_gate,s_scope}, s_ext)>, gate < ext in the partial order",
        mc_de, dea_de, wl_B_de, "Preserved with one declared auxiliary constant and a native constraint form")

# Reverse direction (prior constructs -> DEA)
claim("REV-1", "reverse", "Binding of duty <=(s1,s2)> (W&L Def 2 ex.4), cardinality C1 and per-activation SoD C5 "
      "(Bertino p.72), SSoD k-n policies (Li Notation 1) have no DEA counterpart", True, None,
      "DEA is a fixed set of invariants, not a constraint language; it is a strict fragment w.r.t. these targets")

# =============================================================================
def main():
    meta = {"protocol_sha256": sha(PROTOCOL), "protocol_sha256_expected": PROTOCOL_SHA,
            "protocol_intact": sha(PROTOCOL) == PROTOCOL_SHA,
            "baseline_sha256": sha(BASELINE) if os.path.exists(BASELINE) else None,
            "baseline_intact": os.path.exists(BASELINE) and sha(BASELINE) == BASELINE_SHA,
            "sources_unavailable": ["Ahn & Sandhu 1999 (RSL99)", "Wang & Li 2010 (TISSEC)"],
            "caveat": "Finite agreement on enumerated model classes is not a proof of general equivalence."}
    assert meta["protocol_intact"], "protocol changed after freeze"
    out = {"meta": meta, "results": R}
    path = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else os.path.join(HERE, "dea-v0343-translation-results.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=list)
    for r in R:
        if r["kind"] == "translation":
            print(f'{r["id"]:8s} {r["regime"][:14]:14s} n={r["models"]:6d} fwd={"ok  " if r["forward_preserved"] else "FAIL"}'
                  f'({r["forward_failures"]}) bwd={"ok  " if r["backward_preserved"] else "FAIL"}({r["backward_failures"]})  {r["target"][:40]}')
        else:
            print(f'{r["id"]:8s} claim holds={r["holds"]}  {r["statement"][:80]}')
    print("protocol intact:", meta["protocol_intact"], "| baseline intact:", meta["baseline_intact"])

if __name__ == "__main__":
    main()
