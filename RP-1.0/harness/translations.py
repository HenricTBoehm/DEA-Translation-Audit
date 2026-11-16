"""Translations DEA model -> target structure, executed by the independent engines.

This module MUST NOT import dea_ref (checked statically by run_audit.py). Each function maps model
elements locally to target structures and returns the TARGET observable (set of permitted event ids or
a verdict) as computed by the target engine.  The only exception is tr_ctrl_wl_oracle, which is an
explicitly labelled ORACLE-EMBEDDING kept for transparency.
"""
import itertools
from engines import bertino, r2bac, rbac_li, rsl99, lts, datalog

DISPS = ("Accept", "Reject", "Hold", "Supplement")


# =============================================================== H_EJ / Eq.16
def _ej_users(m):
    return sorted(set(m["exec"]) | set(m["adj"]) | {g[0] for g in m["grants"]})


def tr_ej_bertino_coarse(m):
    """Regime A (original EJ-1/2 encoding): one exec task, one adjudication task."""
    spec = [("role", ("R_exec", "T_exec")), ("role", ("R_adj", "T_adj"))]
    spec += [("belong", (u, "R_exec")) for u in set(m["exec"])]
    spec += [("belong", (u, "R_adj")) for u in {g[0] for g in m["grants"]}]
    rules = [("cannot_dou", ("U", "T_adj"), [("+", "executeu", ("U", "T_exec", "K"))])]
    I = bertino.Instance(spec, rules, "A")
    for k in range(m["n"]):
        I.request(m["exec"][k], "T_exec")
    return frozenset(k for k in range(m["n"]) if I.request(m["adj"][k], "T_adj")["permitted"])


def tr_ej_bertino_idx(m):
    """Regime A with A-IDX: tasks per output and per (output, disposition); roles from grants."""
    spec, rules = [], []
    for k in range(m["n"]):
        spec += [("role", (f"R_exec_{k}", f"T_exec_{k}")), ("belong", (m["exec"][k], f"R_exec_{k}"))]
        for s in DISPS:
            spec.append(("role", (f"R_adj_{k}_{s}", f"T_adj_{k}_{s}")))
            rules.append(("cannot_dou", ("U", f"T_adj_{k}_{s}"), [("+", "executeu", ("U", f"T_exec_{k}", "K"))]))
    spec += [("belong", (u, f"R_adj_{k}_{s}")) for (u, k, s) in m["grants"]]
    I = bertino.Instance(spec, rules, "A")
    for k in range(m["n"]):
        I.request(m["exec"][k], f"T_exec_{k}")
    return frozenset(k for k in range(m["n"])
                     if I.request(m["adj"][k], f"T_adj_{k}_{m['disp'][k]}")["permitted"])


def tr_ej_bertino_B(m):
    """Regime B: aux produced/2 (post-fact of exec activation), granted/3, req/2, cand/1."""
    aux = {"produced", "granted", "req", "cand"}
    users = _ej_users(m)
    spec = [("role", ("R", "T_exec")), ("role", ("R", "T_adj"))] + [("belong", (u, "R")) for u in users]
    spec += [("cand", (u,)) for u in users] + [("granted", (u, f"x{k}", s)) for (u, k, s) in m["grants"]]
    rules = [("cannot_dou", ("U", "T_adj"), [("+", "req", ("X", "S")), ("+", "cand", ("U",)),
                                           ("-", "granted", ("U", "X", "S"))]),
             ("cannot_dou", ("U", "T_adj"), [("+", "req", ("X", "S")), ("+", "executeu", ("U", "T_exec", "K")),
                                           ("+", "produced", ("K", "X"))])]
    I = bertino.Instance(spec, rules, "B", aux)
    for k in range(m["n"]):
        I.request(m["exec"][k], "T_exec", post_facts=lambda kk, k=k: [("produced", (kk, f"x{k}"))])
    return frozenset(k for k in range(m["n"])
                     if I.request(m["adj"][k], "T_adj", request_facts=[("req", (f"x{k}", m["disp"][k]))])["permitted"])


def _wl_ej(m, idx):
    users = _ej_users(m)
    UR, SA, C, steps, order, seq = set(), set(), [], [], set(), []
    for k in range(m["n"]):
        se = f"s_exec_{k}"
        sj = f"s_adj_{k}_{m['disp'][k]}" if idx else f"s_adj_{k}"
        steps += [se, sj]
        order.add((se, sj))
        UR.add((m["exec"][k], f"Rex_{k}"))
        SA |= {(f"Rex_{k}", se), (f"Radj_{sj}", sj)}
        for (u, kk, s) in m["grants"]:
            if kk == k and (not idx or s == m["disp"][k]):
                UR.add((u, f"Radj_{sj}"))
        C.append(("pair", "!=", sj, se))
    cfg = r2bac.Config(users, UR, {})
    W = r2bac.Workflow(steps, order, SA, C)
    for k in range(m["n"]):
        seq.append((m["exec"][k], f"s_exec_{k}"))
    for k in range(m["n"]):
        seq.append((m["adj"][k], f"s_adj_{k}_{m['disp'][k]}" if idx else f"s_adj_{k}"))
    res = r2bac.runtime(cfg, W, seq)
    return frozenset(k for k in range(m["n"]) if res[m["n"] + k])


def tr_ej_wl_coarse(m):
    return _wl_ej(m, False)


def tr_ej_wl_idx(m):
    return _wl_ej(m, True)


def tr_ej_li(m, history=False):
    """Li: UA from executions and grants; ssod<{p_exec_k, p_adj_k_s},2> per (k,s).
    history=False: current state (revoked execution permissions removed) -- Regime A.
    history=True : UA(e, Rex_k) records that e executed k, irrespective of revocation (A-HIST, Regime B)."""
    out = set()
    for k in range(m["n"]):
        s, j = m["disp"][k], m["adj"][k]
        UA = {(e, f"Rex_{kk}") for kk, e in enumerate(m["exec"]) if history or e not in m["exec_perm_revoked"]}
        UA |= {(u, f"Radj_{kk}_{ss}") for (u, kk, ss) in m["grants"]}
        PA = {(f"Rex_{kk}", f"pex_{kk}") for kk in range(m["n"])}
        PA |= {(f"Radj_{kk}_{ss}", f"padj_{kk}_{ss}") for kk in range(m["n"]) for ss in DISPS}
        holds = f"padj_{k}_{s}" in rbac_li.auth_perms(UA, PA, set(), j)
        if holds and rbac_li.safe({x for x in UA if x[0] == j or x[1] == f"Rex_{k}"}, PA, set(),
                                  [({f"pex_{k}", f"padj_{k}_{s}"}, 2)]):
            out.add(k)
    return frozenset(out)


def tr_ej_rsl(m, history=False):
    """RSL99 SSOD-CR (Table 1 #1) on the snapshot; CR = {{Rex_k, Radj_k_s}} for the event."""
    out = set()
    for k in range(m["n"]):
        s, j = m["disp"][k], m["adj"][k]
        UA = {(e, f"Rex_{kk}") for kk, e in enumerate(m["exec"]) if history or e not in m["exec_perm_revoked"]}
        UA |= {(u, f"Radj_{kk}_{ss}") for (u, kk, ss) in m["grants"] if u == j}
        S = rsl99.Snapshot({"U": _ej_users(m), "CR": [{f"Rex_{k}", f"Radj_{k}_{s}"}]}, UA)
        if (j, f"Radj_{k}_{s}") in UA and rsl99.sat(S, rsl99.SSOD_CR(1)):
            out.add(k)
    return frozenset(out)


# =============================================================== T3
def tr_t3_bertino_coarse(m):
    spec = [("role", ("R", t)) for t in ("T_scope", "T_exec", "T_acc")]
    spec += [("belong", (u, "R")) for u in "abc"]
    rules = [("cannot_dou", ("U", "T_acc"), [("+", "executeu", ("U", "T_scope", "K1")),
                                            ("+", "executeu", ("U", "T_exec", "K2"))])]
    I = bertino.Instance(spec, rules, "A")
    I.request(m["scope"], "T_scope")
    for e in m["exec"]:
        I.request(e, "T_exec")
    return frozenset(k for k in range(2) if I.request(m["acc"][k], "T_acc")["permitted"])


def tr_t3_bertino_idx(m):
    tasks = ["T_scope"] + [f"T_exec_{k}" for k in range(2)] + [f"T_acc_{k}" for k in range(2)]
    spec = [("role", ("R", t)) for t in tasks] + [("belong", (u, "R")) for u in "abc"]
    rules = [("cannot_dou", ("U", f"T_acc_{k}"), [("+", "executeu", ("U", "T_scope", "K1")),
                                                 ("+", "executeu", ("U", f"T_exec_{k}", "K2"))]) for k in range(2)]
    I = bertino.Instance(spec, rules, "A")
    I.request(m["scope"], "T_scope")
    for k, e in enumerate(m["exec"]):
        I.request(e, f"T_exec_{k}")
    return frozenset(k for k in range(2) if I.request(m["acc"][k], f"T_acc_{k}")["permitted"])


def tr_t3_wl(m):
    steps = ["s_scope", "s_exec_0", "s_exec_1", "s_acc_0", "s_acc_1"]
    cfg = r2bac.Config("abc", {(u, "R") for u in "abc"}, {})
    C = [("ex_l", "!=", ["s_scope", f"s_exec_{k}"], f"s_acc_{k}") for k in range(2)]
    W = r2bac.Workflow(steps, set(), {("R", s) for s in steps}, C)
    seq = [(m["scope"], "s_scope"), (m["exec"][0], "s_exec_0"), (m["exec"][1], "s_exec_1"),
           (m["acc"][0], "s_acc_0"), (m["acc"][1], "s_acc_1")]
    res = r2bac.runtime(cfg, W, seq)
    return frozenset(k for k in range(2) if res[3 + k])


def tr_t3_rsl(m):
    out = set()
    for k in range(2):
        UA = {(m["scope"], "Scope"), (m["exec"][k], f"Exec_{k}"), (m["acc"][k], f"Acc_{k}")}
        S = rsl99.Snapshot({"U": list("abc"), "CR": [{"Scope", f"Exec_{k}", f"Acc_{k}"}]}, UA)
        if rsl99.sat(S, rsl99.SSOD_CR(2)):
            out.add(k)
    return frozenset(out)


# =============================================================== H_DE^ext
def tr_de_wl_fixed(m):
    cfg = r2bac.Config("ab", {(u, "R") for u in "ab"}, {})
    W = r2bac.Workflow(["s_scope", "s_gate", "s_ext"], {("s_scope", "s_gate"), ("s_gate", "s_ext")},
                       {("R", s) for s in ("s_scope", "s_gate", "s_ext")},
                       [("pair", "!=", "s_gate", "s_scope"), ("pair", "!=", "s_gate", "s_ext")])
    seq = [(m["scope"], "s_scope")] + ([(m["gate"], "s_gate")] if m["gate"] != "nu" else []) + [(m["ext"], "s_ext")]
    return frozenset(["ext"]) if _wl_runtime_ordered(cfg, W, seq)[-1] else frozenset()


def tr_de_wl_nogate(m):
    cfg = r2bac.Config("ab", {(u, "R") for u in "ab"}, {})
    W = r2bac.Workflow(["s_scope", "s_ext"], {("s_scope", "s_ext")}, {("R", "s_scope"), ("R", "s_ext")}, [])
    return frozenset(["ext"]) if _wl_runtime_ordered(cfg, W, [(m["scope"], "s_scope"), (m["ext"], "s_ext")])[-1] else frozenset()


def tr_de_wl_nu(m):
    """Regime B: declared pseudo-user nu; rho* = {(u,v): u != v and u != nu}; native form 2."""
    users = ["a", "b", "nu"]
    rho = {(u, v) for u in users for v in users if u != v and u != "nu"}
    cfg = r2bac.Config(users, {(u, "R") for u in users}, {"rho*": rho})
    W = r2bac.Workflow(["s_scope", "s_gate", "s_ext"], {("s_scope", "s_gate"), ("s_gate", "s_ext")},
                       {("R", s) for s in ("s_scope", "s_gate", "s_ext")},
                       [("ex_l", "rho*", ["s_gate", "s_scope"], "s_ext")])
    seq = [(m["scope"], "s_scope"), (m["gate"], "s_gate"), (m["ext"], "s_ext")]
    return frozenset(["ext"]) if _wl_runtime_ordered(cfg, W, seq)[-1] else frozenset()


def _wl_runtime_ordered(cfg, W, seq):
    """Def 3 partial-plan condition: a step may be added only if all its predecessors are assigned."""
    done, ok_seq, out = set(), [], []
    for (u, s) in seq:
        preds_ok = all(a in done for (a, b) in W.order if b == s)
        res = r2bac.runtime(cfg, W, ok_seq + [(u, s)])[-1] if preds_ok else False
        out.append(res)
        if res:
            ok_seq.append((u, s))
            done.add(s)
    return out


def tr_de_bertino(m):
    """Regime A: cannot_dou(U,T_ext) <- executeu(U,T_scope,K), count(executeu(V,T_gate,K2), V != U) = 0."""
    spec = [("role", ("R", t)) for t in ("T_scope", "T_gate", "T_ext")] + [("belong", (u, "R")) for u in "ab"]
    rules = [("cannot_dou", ("U", "T_ext"),
              [("+", "executeu", ("U", "T_scope", "K")),
               ("count", [("+", "executeu", ("V", "T_gate", "K2")), ("cmp", "!=", "V", "U")], "N"),
               ("cmp", "==", "N", 0)])]
    I = bertino.Instance(spec, rules, "A")
    I.request(m["scope"], "T_scope")
    if m["gate"] != "nu":
        I.request(m["gate"], "T_gate")
    return frozenset(["ext"]) if I.request(m["ext"], "T_ext")["permitted"] else frozenset()


# =============================================================== Ctrl_theta
NODES = ["p", "o", "a", "j"]
T_E, T_J, T_CHECK = (0, 1), (2, 3), 3


def _active(m, t, IV):
    return [tuple(k.split("->")) for k, iv in m["edges"].items() if t in IV[iv]]


def tr_ctrl_wl_snapshot(m, IV):
    """Regime A, element-local: relation ctl = direct edges active at check time t=3."""
    ctl = set(_active(m, T_CHECK, IV))
    cfg = r2bac.Config(NODES, {("a", "RE"), ("j", "RJ")}, {"ctl": ctl})
    W = r2bac.Workflow(["s_E", "s_J"], {("s_E", "s_J")}, {("RE", "s_E"), ("RJ", "s_J")},
                       [("pair", "~ctl", "s_J", "s_E"), ("pair", "~ctl", "s_E", "s_J"), ("pair", "!=", "s_J", "s_E")])
    return frozenset(["effective"]) if r2bac.runtime(cfg, W, [("a", "s_E"), ("j", "s_J")])[1] else frozenset()


def tr_ctrl_wl_oracle(m, IV, semantics):
    """ORACLE-EMBEDDING (excluded as evidence): B := co-control relation computed outside R2BAC."""
    def clo(edges):
        c = {n: {n} for n in NODES}
        ch = True
        while ch:
            ch = False
            for (s, t) in edges:
                for n in NODES:
                    if s in c[n] and t not in c[n]:
                        c[n].add(t); ch = True
        return c
    def win(w):
        if semantics == "A":
            out = {n: set() for n in NODES}
            for t in w:
                c = clo(_active(m, t, IV))
                for n in NODES:
                    out[n] |= c[n]
            return out
        return clo([e for t in w for e in _active(m, t, IV)])
    cE, cJ = win(T_E), win(T_J)
    cc = {("j", "a")} if any("j" in cJ[p] and "a" in cE[p] for p in NODES) else set()
    cfg = r2bac.Config(NODES, {("a", "RE"), ("j", "RJ")}, {"cc": cc})
    W = r2bac.Workflow(["s_E", "s_J"], {("s_E", "s_J")}, {("RE", "s_E"), ("RJ", "s_J")}, [("pair", "~cc", "s_J", "s_E")])
    return frozenset(["effective"]) if r2bac.runtime(cfg, W, [("a", "s_E"), ("j", "s_J")])[1] else frozenset()


def tr_ctrl_bertino_B(m, IV, semantics):
    """Regime B: aux edge/3, node/1, inE/1, inJ/1 + declared recursive IDB (positive recursion)."""
    aux = {"edge", "node", "inE", "inJ", "time", "rp", "ctrlE", "ctrlJ", "eE", "eJ", "rE", "rJ"}
    spec = [("role", ("RE", "T_exec")), ("role", ("RJ", "T_adj")), ("belong", ("a", "RE")), ("belong", ("j", "RJ"))]
    spec += [("node", (n,)) for n in NODES] + [("time", (t,)) for t in range(4)]
    spec += [("inE", (t,)) for t in T_E] + [("inJ", (t,)) for t in T_J]
    spec += [("edge", (s, d, t)) for t in range(4) for (s, d) in _active(m, t, IV)]
    if semantics == "A":
        rules = [("rp", ("P", "P", "T"), [("+", "node", ("P",)), ("+", "time", ("T",))]),
                 ("rp", ("P", "B", "T"), [("+", "rp", ("P", "A", "T")), ("+", "edge", ("A", "B", "T"))]),
                 ("ctrlE", ("P", "A"), [("+", "rp", ("P", "A", "T")), ("+", "inE", ("T",))]),
                 ("ctrlJ", ("P", "A"), [("+", "rp", ("P", "A", "T")), ("+", "inJ", ("T",))])]
    else:
        rules = [("eE", ("A", "B"), [("+", "edge", ("A", "B", "T")), ("+", "inE", ("T",))]),
                 ("eJ", ("A", "B"), [("+", "edge", ("A", "B", "T")), ("+", "inJ", ("T",))]),
                 ("rE", ("P", "P"), [("+", "node", ("P",))]), ("rJ", ("P", "P"), [("+", "node", ("P",))]),
                 ("rE", ("P", "B"), [("+", "rE", ("P", "A")), ("+", "eE", ("A", "B"))]),
                 ("rJ", ("P", "B"), [("+", "rJ", ("P", "A")), ("+", "eJ", ("A", "B"))]),
                 ("ctrlE", ("P", "A"), [("+", "rE", ("P", "A"))]), ("ctrlJ", ("P", "A"), [("+", "rJ", ("P", "A"))])]
    rules.append(("cannot_dou", ("J", "T_adj"), [("+", "ctrlJ", ("P", "J")), ("+", "ctrlE", ("P", "A")),
                                                ("+", "executeu", ("A", "T_exec", "K"))]))
    I = bertino.Instance(spec, rules, "B", aux)
    I.request("a", "T_exec")
    return frozenset(["effective"]) if I.request("j", "T_adj")["permitted"] else frozenset()


def _rh_encoding(m, IV, semantics):
    """Principal-as-role reduction: role r_<x>_<t> per node and time (A) or per node and window (B);
    edge x->y active at t gives RH (r_x_t, r_y_t); each node is a user assigned all its own roles;
    p_exec attached to a's roles in theta_E, p_adj to j's roles in theta_J."""
    UA, PA, RH = set(), set(), set()
    if semantics == "A":
        for t in range(4):
            for n in NODES:
                UA.add((n, f"r_{n}_{t}"))
            for (s, d) in _active(m, t, IV):
                RH.add((f"r_{s}_{t}", f"r_{d}_{t}"))
        PA |= {(f"r_a_{t}", "p_exec") for t in T_E} | {(f"r_j_{t}", "p_adj") for t in T_J}
    else:
        for w, ts in (("E", T_E), ("J", T_J)):
            for n in NODES:
                UA.add((n, f"r_{n}_{w}"))
            for t in ts:
                for (s, d) in _active(m, t, IV):
                    RH.add((f"r_{s}_{w}", f"r_{d}_{w}"))
        PA |= {("r_a_E", "p_exec"), ("r_j_J", "p_adj")}
    return UA, PA, RH


def tr_ctrl_li_rh(m, IV, semantics):
    """Regime B reduction into Li 2007: RH* (p.10) supplies the transitive closure;
    ssod<{p_exec,p_adj},2> unsafe iff a single user (principal) holds both permissions."""
    UA, PA, RH = _rh_encoding(m, IV, semantics)
    return frozenset(["effective"]) if rbac_li.safe(UA, PA, RH, [({"p_exec", "p_adj"}, 2)]) else frozenset()


def tr_ctrl_rsl_rh(m, IV, semantics):
    """Regime B reduction into RSL99: roles* with role hierarchy (Fig. 1, p.46);
    Table 1 property 2 (MOD-CP): |permissions(roles*(u)) & cp| <= 1."""
    UA, PA, RH = _rh_encoding(m, IV, semantics)
    S = rsl99.Snapshot({"U": NODES, "CP": [{"p_exec", "p_adj"}]}, UA, {(p, r) for (r, p) in PA}, RH=RH)
    return frozenset(["effective"]) if rsl99.sat(S, rsl99.MOD_CP()) else frozenset()


def tr_ctrl_li_identity(m, IV):
    UA = {("a", "Rex"), ("j", "Radj")}
    PA = {("Rex", "pex"), ("Radj", "padj")}
    return frozenset(["effective"]) if rbac_li.safe(UA, PA, set(), [({"pex", "padj"}, 2)]) else frozenset()


def tr_ctrl_rsl_cu_snapshot(m, IV):
    """Regime A: CU = {{x,y}: direct edge x->y active at check time}; Table 1 property 5 (SSOD-CU)."""
    cus = [{s, d} for (s, d) in _active(m, T_CHECK, IV)]
    S = rsl99.Snapshot({"CR": [{"Rex", "Radj"}], "CU": cus or [set()]}, {("a", "Rex"), ("j", "Radj")})
    return frozenset(["effective"]) if rsl99.sat(S, rsl99.SSOD_CU()) else frozenset()


# =============================================================== Ledger
def _ledger_bertino_rules(B):
    assert B == 1, "native comparison-only encoding is stated for B = 1"
    return [
        ("cannot_dou", ("U", "T_term"), [("+", "belong", ("U", "R_t")),
                                         ("count", [("+", "success", ("T_term", "K"))], "N1"),
                                         ("count", [("+", "success", ("T_reopen", "K2"))], "N2"),
                                         ("cmp", ">", "N1", "N2")]),
        ("cannot_dou", ("U", "T_cont"), [("+", "belong", ("U", "R_c")),
                                         ("count", [("+", "success", ("T_cont", "K"))], "N"),
                                         ("count", [("+", "success", ("T_reopen", "K2"))], "R"),
                                         ("cmp", ">", "N", "R")]),          # B = 1 form: N >= 1 + R
        ("cannot_dou", ("U", "T_cont"), [("+", "belong", ("U", "R_c")),
                                         ("count", [("+", "success", ("T_term", "K"))], "N1"),
                                         ("count", [("+", "success", ("T_reopen", "K2"))], "N2"),
                                         ("cmp", ">", "N1", "N2")]),
        ("cannot_dou", ("U", "T_reopen"), [("+", "belong", ("U", "R_ind")),
                                           ("count", [("+", "success", ("T_term", "K"))], "N1"),
                                           ("count", [("+", "success", ("T_reopen", "K2"))], "N2"),
                                           ("cmp", "<=", "N1", "N2")])]


def _ledger_spec(tasks_suffix=""):
    return [("role", ("R_c", "T_cont" + tasks_suffix)), ("role", ("R_t", "T_term" + tasks_suffix)),
            ("role", ("R_ind", "T_reopen" + tasks_suffix)), ("role", ("R_c", "T_stage")),
            ("belong", ("u_c", "R_c")), ("belong", ("u_t", "R_t")), ("belong", ("u_ind", "R_ind")),
            ("belong", ("u_dep", "R_dep"))]


def _ledger_run(m, key_of):
    """key_of(event) -> instance key. Native rules (B=1 form: conts allowed <= 1 + reopens) per key."""
    inst, out = {}, set()
    for i, e in enumerate(m["events"]):
        if e[0] == "cont" and e[3] is None:
            out.add(i)
            continue
        k = key_of(e)
        if k not in inst:
            inst[k] = bertino.Instance(_ledger_spec(), _ledger_bertino_rules(m["B"]), "A")
        I = inst[k]
        if e[0] == "cont":
            if I.request("u_c", "T_cont")["permitted"]:
                out.add(i)
        elif e[0] == "term":
            I.request("u_t", "T_term")
        elif e[0] == "reopen":
            I.request("u_ind" if e[4] else "u_dep", "T_reopen")
    return frozenset(out)


def tr_led_bertino_inst(m):
    """Regime A, A-INST: one Bertino instance per (DEA workflow, case, blocker) -- instance boundaries
    preserved; within-instance ledger is native (count aggregates, cannot_dou prevention)."""
    return _ledger_run(m, lambda e: (e[1], e[2], e[3]))


def tr_led_bertino_inst_detect(m):
    """Original LED-1 label: panic <- count(success(T_cont,K),N), N > B per workflow (DETECTION).
    Returns the continuation events after which panic is NOT raised (detection observable)."""
    inst, out = {}, set()
    rules = [("panic", (), [("count", [("+", "success", ("T_cont", "K"))], "N"), ("cmp", ">", "N", m["B"])])]
    for i, e in enumerate(m["events"]):
        if e[0] != "cont":
            continue
        if e[3] is None:
            out.add(i)
            continue
        I = inst.setdefault(e[1], bertino.Instance([("role", ("R_c", "T_cont")), ("belong", ("u_c", "R_c"))], rules, "A"))
        r = I.request("u_c", "T_cont")
        if r["permitted"] and not r["panic_after"]:
            out.add(i)
    return frozenset(out)


def tr_led_bertino_merge(m):
    """Regime A with A-MERGE (non-standard): one Bertino instance per DEA (case, blocker) ledger key."""
    return _ledger_run(m, lambda e: (e[2], e[3]))


def tr_led_bertino_B(m):
    """Regime B: declared persistent cross-instance fact store (aux led/3, term/3, opn/3, key/2,
    req/2, budget/1, cand/1, closed/2, lastopen/3, used/3)."""
    aux = {"led", "term", "opn", "key", "req", "budget", "cand", "closed", "lastopen", "used", "reqr", "reqt"}
    keys = {(e[2], e[3]) for e in m["events"] if e[3] is not None}
    store = {("opn", (c, b, -1)) for (c, b) in keys} | {("key", (c, b)) for (c, b) in keys} | {("budget", (m["B"],))}
    rules = [
        ("closed", ("C", "B"), [("+", "key", ("C", "B")), ("count", [("+", "term", ("C", "B", "K"))], "N1"),
                                ("count", [("+", "opn", ("C", "B", "K2")), ("cmp", ">=", "K2", 0)], "N2"),
                                ("cmp", ">", "N1", "N2")]),
        ("lastopen", ("C", "B", "L"), [("+", "key", ("C", "B")), ("max", "K", [("+", "opn", ("C", "B", "K"))], "L")]),
        ("used", ("C", "B", "N"), [("+", "lastopen", ("C", "B", "L")),
                                   ("count", [("+", "led", ("C", "B", "K")), ("cmp", ">", "K", "L")], "N")]),
        ("cannot_dou", ("U", "T_cont"), [("+", "req", ("C", "B")), ("+", "cand", ("U",)), ("+", "closed", ("C", "B"))]),
        ("cannot_dou", ("U", "T_cont"), [("+", "req", ("C", "B")), ("+", "cand", ("U",)), ("+", "used", ("C", "B", "N")),
                                         ("+", "budget", ("Bd",)), ("cmp", ">=", "N", "Bd")]),
        ("cannot_dou", ("U", "T_reopen"), [("+", "reqr", ("C", "B")), ("+", "cand", ("U",)), ("-", "closed", ("C", "B"))]),
        ("cannot_dou", ("U", "T_term"), [("+", "reqt", ("C", "B")), ("+", "cand", ("U",)), ("+", "closed", ("C", "B"))]),
    ]
    spec = _ledger_spec() + [("cand", (u,)) for u in ("u_c", "u_ind", "u_dep", "u_t")]
    out = set()
    for i, e in enumerate(m["events"]):
        if e[0] == "cont" and e[3] is None:
            out.add(i)
            continue
        I = bertino.Instance(spec, rules, "B", aux)          # fresh instance per event; state lives in store
        I.hist = set()
        c, b = e[2], e[3]
        if e[0] == "cont":
            r = I.request("u_c", "T_cont", request_facts=list(store) + [("req", (c, b))])
            if r["permitted"]:
                out.add(i)
                store.add(("led", (c, b, i)))
        elif e[0] == "term":
            if I.request("u_t", "T_term", request_facts=list(store) + [("reqt", (c, b))])["permitted"]:
                store.add(("term", (c, b, i)))
        elif e[0] == "reopen":
            r = I.request("u_ind" if e[4] else "u_dep", "T_reopen", request_facts=list(store) + [("reqr", (c, b))])
            if r["permitted"]:
                store.add(("opn", (c, b, i)))
    return frozenset(out)


def tr_led_wl(m):
    """Regime A: W&L-07 has no counting constraint form; each continuation is an authorised step."""
    return frozenset(i for i, e in enumerate(m["events"]) if e[0] == "cont")


# =============================================================== NAP
def tr_nap_wsp_all(m):
    steps = [e[0] for e in m["edges"]]
    UR = {("E", "R")}
    SA = {("R", e[0]) for e in m["edges"] if e[3]}
    sat = r2bac.satisfiable(r2bac.Config(["E"], UR, {}), r2bac.Workflow(steps, set(), SA, []))
    return frozenset() if sat else frozenset(["NAP"])


def tr_nap_wsp_allowed(m):
    steps = [e[0] for e in m["edges"] if e[3]]
    return frozenset(["NAP"]) if not steps else frozenset()


def tr_nap_wsp_label(m):
    """R3-violating reduction: users {R,N} are reachability LABELS. NAP iff exists a labelling with
    start=R, goals=N and no allowed edge from R to N (closed set avoiding the goals)."""
    users = ["R", "N"]
    imp = {("R", "R"), ("N", "R"), ("N", "N")}
    steps = [f"s_{x}" for x in m["states"]]
    UR = {("R", "RR"), ("N", "RN")}
    SA = set()
    for x in m["states"]:
        if x == m["start"] and x in m["goals"]:
            continue                                  # start must be R and goals N: no admissible user
        if x == m["start"]:
            SA.add(("RR", f"s_{x}"))
        if x in m["goals"]:
            SA.add(("RN", f"s_{x}"))
        if x != m["start"] and x not in m["goals"]:
            SA |= {("RR", f"s_{x}"), ("RN", f"s_{x}")}
    C = [("pair", "imp", f"s_{a}", f"s_{b}") for (_, a, b, ok) in m["edges"] if ok]
    sat = r2bac.satisfiable(r2bac.Config(users, UR, {"imp": imp}), r2bac.Workflow(steps, set(), SA, C))
    return frozenset(["NAP"]) if sat else frozenset()


def tr_nap_wsp_path(m):
    """R3-violating reduction (original NAP-4): users := allowed edges + idle loops; slots 1..|S|."""
    users = [f"{e[0]}|{e[1]}|{e[2]}" for e in m["edges"] if e[3]] + [f"idle_{s}|{s}|{s}" for s in m["states"]]
    src = {u: u.split("|")[1] for u in users}
    dst = {u: u.split("|")[2] for u in users}
    H = max(1, len(m["states"]))
    slots = [f"slot{i}" for i in range(H)]
    UR = {(u, "Rany") for u in users} | {(u, "Rfirst") for u in users if src[u] == m["start"]}
    UR |= {(u, "Rlast") for u in users if dst[u] in m["goals"]}
    UR |= {(u, "Rboth") for u in users if src[u] == m["start"] and dst[u] in m["goals"]}
    SA = set()
    for i, s in enumerate(slots):
        role = "Rboth" if H == 1 else ("Rfirst" if i == 0 else ("Rlast" if i == H - 1 else "Rany"))
        SA.add((role, s))
    chain = {(u, v) for u in users for v in users if dst[u] == src[v]}
    C = [("pair", "chain", slots[i], slots[i + 1]) for i in range(H - 1)]
    sat = r2bac.satisfiable(r2bac.Config(users, UR, {"chain": chain}), r2bac.Workflow(slots, set(), SA, C))
    return frozenset() if sat else frozenset(["NAP"])


def tr_nap_bertino_B(m):
    aux = {"edge", "ok", "start", "goal", "reach", "reached", "nap"}
    facts = [("edge", (a, n, b)) for (n, a, b, _) in m["edges"]] + [("ok", (n,)) for (n, _, _, ok) in m["edges"] if ok]
    facts += [("start", (m["start"],))] + [("goal", (g,)) for g in m["goals"]]
    rules = [("reach", ("S",), [("+", "start", ("S",))]),
             ("reach", ("Y",), [("+", "reach", ("X",)), ("+", "edge", ("X", "E", "Y")), ("+", "ok", ("E",))]),
             ("reached", (), [("+", "reach", ("G",)), ("+", "goal", ("G",))]),
             ("nap", (), [("-", "reached", ())])]
    bertino.validate(rules, facts, "B", aux)
    db = datalog.evaluate(set(facts), rules)
    return frozenset(["NAP"]) if db.get("nap") else frozenset()


def tr_nap_li_rh(m):
    """Regime B reduction (roles-as-states) into Li 2007: allowed edge x->y gives RH (r_x, r_y);
    probe user assigned r_start; goal roles hold p_goal. NAP iff probe lacks p_goal (RH*, p.10)."""
    RH = {(f"r_{a}", f"r_{b}") for (_, a, b, ok) in m["edges"] if ok}
    UA = {("probe", f"r_{m['start']}")}
    PA = {(f"r_{g}", "p_goal") for g in m["goals"]}
    return frozenset() if "p_goal" in rbac_li.auth_perms(UA, PA, RH, "probe") else frozenset(["NAP"])


def _lts(m):
    return {"init": m["start"], "goals": set(m["goals"]),
            "trans": [(a, n, b) for (n, a, b, _) in m["edges"]],
            "auth": {n: ({"E"} if ok else set()) for (n, _, _, ok) in m["edges"]}}


def tr_nap_basin_obstruction(m):
    return frozenset(["NAP"]) if lts.obstructed(_lts(m), len(m["states"])) else frozenset()


def tr_nap_basin_tick(m):
    return frozenset() if lts.tick_reachable(_lts(m), len(m["states"])) else frozenset(["NAP"])


# ---------------------------------------------------------------- added after first run (see change log)
def tr_t3_li(m):
    """A-HIST into Li 2007: performing a DEA function = holding its role; ssod<{p_scope,p_exec_k,p_acc_k},2>
    (no single user holds all three permissions)."""
    out = set()
    for k in range(2):
        UA = {(m["scope"], "Scope"), (m["exec"][k], f"Exec_{k}"), (m["acc"][k], f"Acc_{k}")}
        PA = {("Scope", "p_scope"), (f"Exec_{k}", f"p_exec_{k}"), (f"Acc_{k}", f"p_acc_{k}")}
        if rbac_li.safe(UA, PA, set(), [({"p_scope", f"p_exec_{k}", f"p_acc_{k}"}, 2)]):
            out.add(k)
    return frozenset(out)


def tr_nap_rsl_rh(m):
    """Roles-as-states into RSL99: RH from allowed edges; probe assigned r_start; goal roles hold p_goal;
    NAP iff |permissions(roles*(probe)) & {p_goal}| <= 0 holds."""
    RH = {(f"r_{a}", f"r_{b}") for (_, a, b, ok) in m["edges"] if ok}
    S = rsl99.Snapshot({"U": ["probe"], "CP": [{"p_goal"}]}, {("probe", f"r_{m['start']}")},
                       {("p_goal", f"r_{g}") for g in m["goals"]}, RH=RH)
    f = ("forall", "u", ("set", "U"), ("forall", "cp", ("set", "CP"),
         ("leq", ("inter", ("app", "permissions", ("app", "roles*", ("var", "u"))), ("var", "cp")), 0)))
    return frozenset(["NAP"]) if rsl99.sat(S, f) else frozenset()
