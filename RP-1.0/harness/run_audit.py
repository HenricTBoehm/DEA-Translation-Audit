#!/usr/bin/env python3
"""DEA v0.3.4.3 translation-audit remediation harness (RP-1.0). Standard library only.

Usage:
  python3 harness/run_audit.py --baseline /path/to/DEA_v0.3.4.3_architecture_closure_candidate_2026-11-15.pdf \
                               [--out results/remediation-results.json]
  (or set DEA_BASELINE).  Exit codes: 0 ok; 2 integrity failure (no results written); 3 static
  independence check failed; 4 internal error.
"""
import argparse, hashlib, json, os, re, sys, itertools, platform

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

BASELINE_SHA = "51a2553e8bb13fe80bc3f0e6245ba0c4dcbe0a31db03ad577a3f3f26f8c97c33"
PROTOCOL = os.path.join(ROOT, "01-remediation-protocol-v1.md")
PROTOCOL_SHA = "107a9793d29df592a26665aeeda34a80de5772a6c2d641f8d2b270cb207e3dac"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def die(code, msg):
    sys.stderr.write(f"INTEGRITY/PRECONDITION FAILURE: {msg}\nNo results were written.\n")
    sys.exit(code)


def integrity(baseline):
    if not baseline:
        die(2, "no baseline path given (--baseline or DEA_BASELINE)")
    if not os.path.isfile(baseline):
        die(2, f"baseline not found: {baseline}")
    h = sha(baseline)
    if h != BASELINE_SHA:
        die(2, f"baseline SHA-256 mismatch: {h}")
    if not os.path.isfile(PROTOCOL):
        die(2, "remediation protocol missing")
    hp = sha(PROTOCOL)
    if hp != PROTOCOL_SHA:
        die(2, f"remediation protocol altered: {hp}")
    return {"baseline_sha256": h, "protocol_sha256": hp}


def static_independence():
    bad = []
    for d in (os.path.join(HERE, "engines"), HERE):
        for f in sorted(os.listdir(d)):
            if not f.endswith(".py") or f in ("run_audit.py", "dea_ref.py", "models.py"):
                continue
            src = open(os.path.join(d, f)).read()
            if re.search(r"^\s*(from|import)\s+.*dea_ref", src, re.M):
                bad.append(os.path.join(os.path.basename(d), f))
    return bad


# ---------------------------------------------- preconditions run BEFORE any test is computed
_ap = argparse.ArgumentParser()
_ap.add_argument("--baseline", default=os.environ.get("DEA_BASELINE"))
_ap.add_argument("--out", default=os.path.join(ROOT, "results", "remediation-results.json"))
ARGS = _ap.parse_args(sys.argv[1:]) if __name__ == "__main__" else None
if __name__ == "__main__":
    META = integrity(ARGS.baseline)
    _bad = static_independence()
    if _bad:
        sys.stderr.write(f"STATIC INDEPENDENCE FAILURE: {_bad}\nNo results were written.\n")
        sys.exit(3)
    if not os.path.isfile(os.path.join(HERE, "engines", "__init__.py")):
        die(2, "harness incomplete: engines/__init__.py missing")

import dea_ref
import models as M
import translations as T

RES = {"translations": [], "proofs": [], "regression": [], "coverage": {}}


def size(m):
    return len(json.dumps(m, sort_keys=True, default=list))


def compare(tid, construct, target, source, regime, kind, desc, gen, dea, tgt, assumptions="", info=""):
    n = ff = bf = 0
    fx = bx = None
    for m in gen():
        n += 1
        d, e = dea(m), tgt(m)
        if not d <= e:
            ff += 1
            if fx is None or size(m) < size(fx["model"]):
                fx = {"model": m, "dea": sorted(map(str, d)), "target": sorted(map(str, e))}
        if not e <= d:
            bf += 1
            if bx is None or size(m) < size(bx["model"]):
                bx = {"model": m, "dea": sorted(map(str, d)), "target": sorted(map(str, e))}
    RES["translations"].append(dict(
        id=tid, construct=construct, target=target, source=source, regime=regime, kind=kind,
        translation=desc, assumptions=assumptions, informativeness=info, models=n,
        forward_preserved=ff == 0, forward_failures=ff, forward_min_countermodel=fx,
        backward_preserved=bf == 0, backward_failures=bf, backward_min_countermodel=bx))


def proof(pid, construct, status, statement, assumptions, argument, check, witness=None):
    RES["proofs"].append(dict(id=pid, construct=construct, status=status, statement=statement,
                              assumptions=assumptions, argument=argument, machine_check_passed=bool(check),
                              witness=witness))


# ================================================================ 1 H_EJ / Eq.16
BER = "Bertino, Ferrari & Atluri 1999"
WL7 = "Wang & Li ESORICS 2007 (NOT the 2010 article)"
LI = "Li, Tripunitara & Bizri 2007"
RSL = "Ahn & Sandhu 1999 (RSL99)"
BAS = "Basin, Burri & Karjoth (extended CSF'11)"

dej = dea_ref.ej_effective
compare("EJ-A-BER-1", "H_EJ + AuthorizedForDisposition", BER, "Tab. I-III pp.73-75; Def 4.2", "A", "translation",
        "original encoding: one T_exec, one T_adj; cannot_dou(U,T_adj) <- executeu(U,T_exec,K)", M.mc_ej, dej,
        T.tr_ej_bertino_coarse)
compare("EJ-A-BER-2", "H_EJ + AuthorizedForDisposition", BER, "Def 2.1 p.71; Tab. I-III; Def 4.2", "A", "translation",
        "A-IDX: tasks T_exec_k, T_adj_k_s; roles R_adj_k_s from grants; cannot_dou(U,T_adj_k_s) <- executeu(U,T_exec_k,K)",
        M.mc_ej, dej, T.tr_ej_bertino_idx, "A-IDX; output count fixed in the specification")
compare("EJ-B-BER", "H_EJ + AuthorizedForDisposition", BER, "Defs 4.2, 4.7; Prop. 4.1", "B", "translation",
        "aux produced/2, granted/3, req/2, cand/1; prevention via cannot_dou", M.mc_ej, dej, T.tr_ej_bertino_B,
        "dynamic object binding", "RESTATEMENT")
compare("EJ-A-WL-1", "H_EJ + AuthorizedForDisposition", WL7, "Defs 1-5 pp.6-7", "A", "translation",
        "original encoding: steps s_exec_k, s_adj_k; <!=(s_adj_k, s_exec_k)>", M.mc_ej, dej, T.tr_ej_wl_coarse)
compare("EJ-A-WL-2", "H_EJ + AuthorizedForDisposition", WL7, "Defs 1-5 pp.6-7", "A", "translation",
        "A-IDX: step s_adj_k_s for the requested disposition; SA from grants with that disposition",
        M.mc_ej, dej, T.tr_ej_wl_idx, "A-IDX; output count fixed in S")
compare("EJ-A-LI", "H_EJ + AuthorizedForDisposition", LI, "Notation 1 p.9; Def 3 p.10", "A", "translation",
        "ssod<{p_exec_k, p_adj_k_s},2> on the current RBAC state", M.mc_ej, dej, T.tr_ej_li)
compare("EJ-A-RSL", "H_EJ + AuthorizedForDisposition", RSL, "Table 1 #1 p.53; p.47 snapshot", "A", "translation",
        "SSOD-CR with CR={{Rex_k, Radj_k_s}} on the current snapshot", M.mc_ej, dej, T.tr_ej_rsl)

# ================================================================ 2 T3, H_DE^ext
compare("EJ-B-LI-HIST", "H_EJ + AuthorizedForDisposition", LI, "Notation 1 p.9; Def 3 p.10", "B", "translation",
        "A-HIST: UA records past execution irrespective of revocation; ssod<{p_exec_k, p_adj_k_s},2>", M.mc_ej, dej,
        lambda m: T.tr_ej_li(m, True), "UA reinterpreted as acted-as record", "RESTATEMENT")
compare("EJ-B-RSL-HIST", "H_EJ + AuthorizedForDisposition", RSL, "Table 1 #1; p.44 history-based SoD", "B",
        "translation", "A-HIST snapshot; SSOD-CR", M.mc_ej, dej, lambda m: T.tr_ej_rsl(m, True),
        "UA reinterpreted as acted-as record", "RESTATEMENT")
compare("T3-A-BER-1", "T3 (Eq.31)", BER, "Tab. III; Def 4.2", "A", "translation",
        "original: cannot_dou(U,T_acc) <- executeu(U,T_scope,_), executeu(U,T_exec,_)", M.mc_t3, dea_ref.t3_permitted,
        T.tr_t3_bertino_coarse)
compare("T3-A-BER-2", "T3 (Eq.31)", BER, "Tab. III; Def 4.2", "A", "translation",
        "A-IDX: cannot_dou(U,T_acc_k) <- executeu(U,T_scope,_), executeu(U,T_exec_k,_)", M.mc_t3,
        dea_ref.t3_permitted, T.tr_t3_bertino_idx, "A-IDX")
compare("T3-A-WL", "T3 (Eq.31)", WL7, "Def 2 form 2 p.6", "A", "translation",
        "<!=(EXISTS{s_scope, s_exec_k}, s_acc_k)>", M.mc_t3, dea_ref.t3_permitted, T.tr_t3_wl, "A-IDX")
compare("T3-B-RSL-HIST", "T3 (Eq.31)", RSL, "Fig. 3 size bound; Table 1 #1", "B", "translation",
        "A-HIST: performing a function = holding its role; for all u, cr: |roles(u) & {Scope, Exec_k, Acc_k}| <= 2",
        M.mc_t3, dea_ref.t3_permitted, T.tr_t3_rsl, "A-IDX; UA reinterpreted as acted-as record", "RESTATEMENT")
compare("T3-B-LI-HIST", "T3 (Eq.31)", LI, "Notation 1; Def 3 (k-n SSoD)", "B", "translation",
        "A-HIST: performing a function = holding its role; ssod<{p_scope,p_exec_k,p_acc_k},2>", M.mc_t3,
        dea_ref.t3_permitted, T.tr_t3_li, "UA reinterpreted as acted-as record", "RESTATEMENT")
compare("DE-A-WL-1", "H_DE^ext (Eq.33)", WL7, "Defs 2-3", "A", "translation", "mandatory gate step, != constraints",
        M.mc_de, dea_ref.de_permitted, T.tr_de_wl_fixed)
compare("DE-A-WL-2", "H_DE^ext (Eq.33)", WL7, "Def 2", "A", "translation", "no gate step", M.mc_de,
        dea_ref.de_permitted, T.tr_de_wl_nogate)
compare("DE-B-WL", "H_DE^ext (Eq.33)", WL7, "Def 1 (user-defined relation), Def 2 form 2", "B", "translation",
        "declared pseudo-user nu; rho* = {(u,v): u != v, u != nu}; <rho*(EXISTS{s_gate,s_scope}, s_ext)>",
        M.mc_de, dea_ref.de_permitted, T.tr_de_wl_nu, "pseudo-user", "REDUCTION")
compare("DE-A-BER", "H_DE^ext (Eq.33)", BER, "Def 4.2; Tab. IV count", "A", "translation",
        "cannot_dou(U,T_ext) <- executeu(U,T_scope,K), count(executeu(V,T_gate,K2), V != U) = 0",
        M.mc_de, dea_ref.de_permitted, T.tr_de_bertino, "optional gate task (runtime does not force completion)")

# ================================================================ 3 Ctrl_theta (both DEA readings)
def edges_at(m):
    return lambda t: [tuple(k.split("->")) for k, iv in m["edges"].items() if t in M.IV[iv]]


def dea_ctrl(sem):
    def f(m):
        c = dea_ref.exec_conflict(T.NODES, edges_at(m), T.T_E, T.T_J, "a", "j", sem)
        return frozenset() if c else frozenset(["effective"])
    return f


for sem in ("A", "B"):
    lab = {"A": "DEA-A per-instant", "B": "DEA-B window-union"}[sem]
    compare(f"CTRL-A-WL-snap/{sem}", f"Ctrl_theta ExecConflict vs {lab}", WL7, "Def 1; p.7 runtime", "A", "translation",
            "element-local: ctl = direct edges active at t=3; <~ctl(s_J,s_E)>, <~ctl(s_E,s_J)>", M.mc_ctrl, dea_ctrl(sem),
            lambda m: T.tr_ctrl_wl_snapshot(m, M.IV), "A-STEP")
    for s2 in ("A", "B"):
        compare(f"CTRL-ORACLE-WL[{s2}]/{sem}", f"Ctrl_theta vs {lab}", WL7, "Def 1", "oracle", "ORACLE-EMBEDDING",
                f"B := co-control relation precomputed under reading {s2}", M.mc_ctrl, dea_ctrl(sem),
                lambda m, s2=s2: T.tr_ctrl_wl_oracle(m, M.IV, s2), "excluded as evidence")
        compare(f"CTRL-B-BER[{s2}]/{sem}", f"Ctrl_theta vs {lab}", BER, "Prop. 4.1 + declared recursive IDB", "B",
                "translation", f"aux edge/3 + positive recursion, closure reading {s2}", M.mc_ctrl, dea_ctrl(sem),
                lambda m, s2=s2: T.tr_ctrl_bertino_B(m, M.IV, s2), "recursion added", "RESTATEMENT")
        compare(f"CTRL-B-LI-RH[{s2}]/{sem}", f"Ctrl_theta vs {lab}", LI, "Notation 2 + RH* p.10; Def 3", "B",
                "translation", f"principal-as-role reduction, RH from edges (reading {s2}); ssod<{{p_exec,p_adj}},2>",
                M.mc_ctrl, dea_ctrl(sem), lambda m, s2=s2: T.tr_ctrl_li_rh(m, M.IV, s2),
                "roles reinterpreted as (principal, time) scopes", "REDUCTION")
        compare(f"CTRL-B-RSL-RH[{s2}]/{sem}", f"Ctrl_theta vs {lab}", RSL, "Fig. 1 roles* p.46; Table 1 #2", "B",
                "translation", f"principal-as-role reduction; MOD-CP (reading {s2})", M.mc_ctrl, dea_ctrl(sem),
                lambda m, s2=s2: T.tr_ctrl_rsl_rh(m, M.IV, s2), "roles reinterpreted; time-indexed copies",
                "REDUCTION")
    compare(f"CTRL-A-LI/{sem}", f"Ctrl_theta vs {lab}", LI, "Notation 1-2; Def 3", "A", "translation",
            "users atomic; ssod<{pex,padj},2>", M.mc_ctrl, dea_ctrl(sem), lambda m: T.tr_ctrl_li_identity(m, M.IV))
    compare(f"CTRL-A-RSL-CU/{sem}", f"Ctrl_theta vs {lab}", RSL, "Table 1 #5 p.53; p.47", "A", "translation",
            "CU = direct edges at check time; SSOD-CU", M.mc_ctrl, dea_ctrl(sem),
            lambda m: T.tr_ctrl_rsl_cu_snapshot(m, M.IV))

# ================================================================ 4 Ledger
def dea_led(m):
    return dea_ref.ledger([tuple(e) for e in m["events"]], m["B"])


compare("LED-A-BER-INST", "case/blocker ledger", BER, "Def 4.7 CB(W); C6 p.72; Tab. IV", "A", "translation",
        "one instance per (workflow, case, blocker); native count rules; cannot_dou PREVENTION", M.mc_led, dea_led,
        T.tr_led_bertino_inst, "A-INST; A-IDX; B=1")
compare("LED-A-BER-DETECT", "case/blocker ledger", BER, "Def 4.4 (integrity rule)", "A", "detection-only",
        "original LED-1 label: panic <- count(success(T_cont,K),N), N > B per workflow (DETECTION observable)",
        M.mc_led, dea_led, T.tr_led_bertino_inst_detect, "A-INST; panic is not enforcement")
compare("LED-A-BER-MERGE", "case/blocker ledger", BER, "Def 4.7; Tab. IV", "A*", "translation",
        "one instance per (case, blocker) across DEA workflows (non-standard instance mapping)", M.mc_led, dea_led,
        T.tr_led_bertino_merge, "A-MERGE (instance boundary reinterpreted); B=1")
compare("LED-B-BER", "case/blocker ledger", BER, "Prop. 4.1 + declared persistent store", "B", "translation",
        "persistent cross-instance aux facts led/term/opn; count/max aggregates; cannot_dou prevention", M.mc_led,
        dea_led, T.tr_led_bertino_B, "persistence added", "RESTATEMENT")
compare("LED-A-WL", "case/blocker ledger", WL7, "Def 2", "A", "translation", "no counting form", M.mc_led, dea_led,
        T.tr_led_wl)

# ================================================================ 5 NAP
dnap = dea_ref.nap
compare("NAP-A-WSP-1", "goal-relative NAP", WL7, "Defs 3-4 p.7", "A", "translation",
        "S = all carrier actions; NAP := unsatisfiable", M.mc_nap, dnap, T.tr_nap_wsp_all)
compare("NAP-A-WSP-2", "goal-relative NAP", WL7, "Defs 3-4 p.7", "A", "translation",
        "S = authorised actions; NAP := S empty", M.mc_nap, dnap, T.tr_nap_wsp_allowed)
compare("NAP-R-WSP-LABEL", "goal-relative NAP", WL7, "Defs 1-4", "R3-violating reduction", "reduction",
        "users {R,N} as reachability labels; <imp(s_x,s_y)> per allowed edge; NAP := satisfiable", M.mc_nap, dnap,
        T.tr_nap_wsp_label, "users repurposed as labels", "REDUCTION")
compare("NAP-R-WSP-PATH", "goal-relative NAP", WL7, "Defs 1-4", "R3-violating reduction", "reduction",
        "users := allowed edges + idle; slots 1..|S|; rho_chain", M.mc_nap, dnap, T.tr_nap_wsp_path,
        "users repurposed as transitions", "REDUCTION")
compare("NAP-B-BER", "goal-relative NAP", BER, "Prop. 4.1 + declared recursive IDB", "B", "translation",
        "reach/1 positive recursion; nap <- not reached", M.mc_nap, dnap, T.tr_nap_bertino_B, "recursion added",
        "RESTATEMENT")
compare("NAP-B-LI-RH", "goal-relative NAP", LI, "Notation 2, RH* p.10", "B", "translation",
        "roles-as-states: allowed edge -> RH; probe user at start; NAP iff probe lacks p_goal", M.mc_nap, dnap,
        T.tr_nap_li_rh, "roles reinterpreted as states", "REDUCTION")
compare("NAP-B-RSL-RH", "goal-relative NAP", RSL, "Fig. 1 roles* p.46; Fig. 3", "B", "translation",
        "roles-as-states: allowed edge -> RH; probe at r_start; NAP iff |permissions(roles*(probe)) & {p_goal}| <= 0",
        M.mc_nap, dnap, T.tr_nap_rsl_rh, "roles reinterpreted as states", "REDUCTION")
compare("NAP-A-BAS-OBS", "goal-relative NAP", BAS, "Def 7 p.14", "A", "translation",
        "NAP := obstructed", M.mc_nap, dnap, T.tr_nap_basin_obstruction)
compare("NAP-B-BAS-TICK", "goal-relative NAP", BAS, "Defs 1-8 + declared goal termination", "B", "translation",
        "TICK enabled exactly in goal states; NAP := no authorised trace ends in TICK (word enumeration)",
        M.mc_nap, dnap, T.tr_nap_basin_tick, "goal termination added", "REDUCTION")


# ================================================================ PROOFS / REFUTATIONS
def tr_ok(tid):
    r = next(x for x in RES["translations"] if x["id"] == tid)
    return r["forward_preserved"] and r["backward_preserved"]


proof("PRF-EJ7", "AuthorizedForDisposition", "REFUTED (original claim withdrawn)",
      "Original EJ-7: disposition-specific authorization NOT-EXPRESSIBLE in Regime A for Bertino and W&L.",
      "A-IDX (tasks/steps are uninterpreted labels: Bertino Def 2.1; W&L Def 2)",
      "The invariance pair (grant Hold vs grant Accept) has DIFFERENT images under the uniform A-IDX translations "
      "EJ-A-BER-2 and EJ-A-WL-2, which preserve outcomes on all of MC-EJ. The original argument quantified only over "
      "translations with one adjudication task per output.",
      tr_ok("EJ-A-BER-2") and tr_ok("EJ-A-WL-2"))

m1, m2 = M.NAP_NAMED["diag_only_p19"], M.NAP_NAMED["diag_goal_twin"]
proof("PRF-NAP3", "goal-relative NAP", "REFUTED as stated; NON-EXPRESSIBILITY NOT ESTABLISHED for WSP",
      "Original NAP-3: NAP not expressible in WSP/R2BAC under R3, by an invariance pair.",
      "Original R3; element-local translations",
      "(i) m1/m2 differ in a 1-local feature (allowed edge from start into a goal), so an element-local translation "
      "can separate them; identical images were shown only for translations ignoring edge endpoints. "
      "(ii) Exact WSP reductions exist (NAP-R-WSP-LABEL, NAP-R-WSP-PATH); they repurpose users, so they violate R3, "
      "but they show the obstacle is the sort discipline, not expressive power.",
      T.tr_nap_wsp_label(m1) != T.tr_nap_wsp_label(m2) and tr_ok("NAP-R-WSP-LABEL") and tr_ok("NAP-R-WSP-PATH"),
      {"m1": m1, "m2": m2})


def hanf_pair(L, Mc):
    """A: s->x1..xL->g  +  y0->y1..yL->z1..zM->z1 ;  B: s->x1..xL->z1..zM->z1  +  y0->y1..yL->g."""
    def chain(pref, n):
        return [f"{pref}{i}" for i in range(1, n + 1)]
    xs, ys, zs = chain("x", L), ["y0"] + chain("y", L), chain("z", Mc)
    A = [("s", xs[0])] + list(zip(xs, xs[1:])) + [(xs[-1], "g")] + list(zip(ys, ys[1:])) + [(ys[-1], zs[0])] + \
        list(zip(zs, zs[1:])) + [(zs[-1], zs[0])]
    B = [("s", xs[0])] + list(zip(xs, xs[1:])) + [(xs[-1], zs[0])] + list(zip(zs, zs[1:])) + [(zs[-1], zs[0])] + \
        list(zip(ys, ys[1:])) + [(ys[-1], "g")]
    return A, B


def r_types(edges, r, start="s", goal="g"):
    nodes = sorted({x for e in edges for x in e})
    adj = {n: set() for n in nodes}
    for a, b in edges:
        adj[a].add(b); adj[b].add(a)
    out = []
    for c in nodes:
        ball, fr = {c}, {c}
        for _ in range(r):
            fr = {y for x in fr for y in adj[x]} - ball
            ball |= fr
        bl = sorted(ball)
        E = [(a, b) for (a, b) in edges if a in ball and b in ball]
        best = None
        others = [x for x in bl if x != c]
        for perm in itertools.permutations(range(1, len(bl))):
            idx = {c: 0, **{x: p for x, p in zip(others, perm)}}
            lab = tuple(sorted((idx[x], x == start, x == goal) for x in bl))
            code = (lab, tuple(sorted((idx[a], idx[b]) for a, b in E)))
            if best is None or code < best:
                best = code
        out.append(best)
    return sorted(out)


A_, B_ = hanf_pair(6, 6)
def as_nap(edges):
    st = sorted({x for e in edges for x in e})
    return {"states": st, "start": "s", "goals": ["g"], "edges": [(f"e{i}", a, b, True) for i, (a, b) in enumerate(edges)]}
same = all(r_types(A_, r) == r_types(B_, r) for r in (1, 2))
proof("PRF-NAP-HANF", "goal-relative NAP", "PROVEN-NON-EXPRESSIBLE under stated assumptions (class T_loc(r), r<=2 checked)",
      "No translation whose target verdict is a function of the multiset of radius-r neighbourhood types of the DEA "
      "state graph (labels: start, goal, authorised) preserves NAP, for r = 1, 2 (and any r with L, M > 2r+1).",
      "T_loc(r): includes WSP translations in which every step has a single authorised user and every constraint "
      "is generated from an r-neighbourhood (verdict = conjunction of locally fixed truth values). Does NOT cover "
      "translations with >= 2 candidate users per step (CSP search is global) -- see NAP-R-WSP-LABEL.",
      "Machine check: graphs A and B have identical multisets of r-types (r = 1, 2) but NAP(A) != NAP(B).",
      same and dea_ref.nap(as_nap(A_)) != dea_ref.nap(as_nap(B_)),
      {"A_edges": A_, "B_edges": B_, "NAP_A": bool(dea_ref.nap(as_nap(A_))), "NAP_B": bool(dea_ref.nap(as_nap(B_)))})

# LED A-INST-LOCAL
wit = None
seen = {}
for m in M.mc_led():
    ev = [tuple(e) for e in m["events"]]
    d = dea_ref.ledger(ev, 1)
    for i, e in enumerate(ev):
        if e[0] != "cont":
            continue
        proj = tuple(x for x in ev[:i + 1] if x[1] == e[1])
        key = proj
        v = i in d
        if key in seen and seen[key][0] != v:
            wit = {"model_1": seen[key][1], "model_2": m["events"], "instance_projection": [list(p) for p in proj],
                   "dea_1": seen[key][0], "dea_2": v}
            break
        seen.setdefault(key, (v, m["events"]))
    if wit:
        break
proof("PRF-LED4", "case/blocker ledger", "PROVEN-NON-EXPRESSIBLE under stated assumptions (A-INST-LOCAL)",
      "No Bertino translation preserves the ledger if each DEA workflow maps to its own Bertino instance and the "
      "constraint base and facts of an instance are functions of that instance's own events (A-INST-LOCAL).",
      "A-INST-LOCAL; Def 4.7 (CB(W) per workflow); execution predicates range over the activations of W only "
      "(Tab. II: 'within a workflow').",
      "The permit/deny verdict for an event in instance W is a function of W's CB, spec and history, all of which are "
      "functions of W's own event projection. The witness gives two models with identical projection of W up to the "
      "event and different DEA verdicts; hence any A-INST-LOCAL translation errs on one of them. Dropping "
      "A-INST-LOCAL (LED-A-BER-MERGE, LED-B-BER) removes the obstruction.",
      wit is not None, wit)

# CTRL monotonicity (W&L) under A-STEP + element-local relations
def mono_check():
    import engines.r2bac as rb
    viol = 0
    base_users = ["a", "j"]
    pairs_new = [("p", "a"), ("a", "p"), ("p", "j"), ("j", "p"), ("p", "p")]
    for rels in itertools.product([set(), {("a", "j")}, {("j", "a")}], repeat=1):
        for extra in itertools.chain.from_iterable(itertools.combinations(pairs_new, k) for k in range(6)):
            for C in ([("pair", "~ctl", "s_J", "s_E")], [("pair", "ctl", "s_J", "s_E")], [("pair", "!=", "s_J", "s_E")],
                      [("pair", "~ctl", "s_J", "s_E"), ("pair", "~ctl", "s_E", "s_J")]):
                W = rb.Workflow(["s_E", "s_J"], {("s_E", "s_J")}, {("RE", "s_E"), ("RJ", "s_J")}, C)
                c0 = rb.Config(base_users, {("a", "RE"), ("j", "RJ")}, {"ctl": rels[0]})
                c1 = rb.Config(base_users + ["p"], {("a", "RE"), ("j", "RJ")}, {"ctl": rels[0] | set(extra)})
                v0 = rb.runtime(c0, W, [("a", "s_E"), ("j", "s_J")])[1]
                v1 = rb.runtime(c1, W, [("a", "s_E"), ("j", "s_J")])[1]
                if v0 and not v1:
                    viol += 1
    return viol == 0


m0 = {"edges": {}}
mp = {"edges": {"p->a": "E", "p->j": "J"}}
pair_ok = all(dea_ctrl(s)(m0) != dea_ctrl(s)(mp) for s in ("A", "B"))
proof("PRF-CTRL-WL-MONO", "Ctrl_theta ExecConflict", "PROVEN-NON-EXPRESSIBLE under stated assumptions (A-STEP + LOCAL-REL)",
      "No W&L-07 translation preserves ExecConflict if (A-STEP) steps, order, SA and constraints depend only on DEA "
      "acts and grants, not on the set of non-acting principals, and (LOCAL-REL) each control edge contributes only "
      "pairs containing its endpoints.",
      "W&L-07 Defs 1-5; A-STEP; LOCAL-REL; both DEA closure readings.",
      "Lemma (monotonicity): adding fresh users and relation pairs that each contain a fresh user leaves UR, SA and "
      "every relation on old users unchanged, so every valid (partial) plan over old users stays valid. DEA pair: "
      "m0 (no edges, effective) and m1 = m0 + principal p with p->a in theta_E and p->j in theta_J (conflict). Under "
      "A-STEP + LOCAL-REL, tr(m1) extends tr(m0) by fresh user p, so the target permits in m1 and errs. "
      "Machine check: lemma verified on all enumerated 2-step instances with one fresh user; pair verified.",
      mono_check() and pair_ok, {"m0": m0, "m1": mp})

cmp_ab = sum(1 for m in M.mc_ctrl() if dea_ctrl("A")(m) != dea_ctrl("B")(m))
bx = {"edges": {"p->o": "J_early", "o->j": "J_late", "p->a": "E"}}
proof("PRF-CTRL6B", "Ctrl_theta closure timing (DEA-internal)", "ARCHITECTURAL AMBIGUITY (outcome-relevant)",
      "Per-instant closure (A) and window-union closure (B) give different ExecConflict decisions; DEA v0.3.4.3 p.8 "
      "does not select either.",
      "Windows theta_E=[0,1], theta_J=[2,3]; MC-CTRL with 7 interval options.",
      "Boundary model: p->o only at t=2, o->j only at t=3, p->a in theta_E. A: no conflict; B: conflict. "
      f"Disagreements inside MC-CTRL: {cmp_ab} of 16807.",
      dea_ctrl("A")(bx) != dea_ctrl("B")(bx),
      {"model": bx, "A_effective": bool(dea_ctrl("A")(bx)), "B_effective": bool(dea_ctrl("B")(bx)),
       "mc_ctrl_disagreements": cmp_ab})

# ================================================================ REGRESSION
def reg(suite, name, status, dea_out, expected_v0343, v0342_intent, target_outputs, note=""):
    RES["regression"].append(dict(suite=suite, case=name, status=status, dea_v0343=dea_out,
                                  expected_v0343=expected_v0343, v0342_intent=v0342_intent,
                                  matches_expected=dea_out == expected_v0343,
                                  diverges_from_v0342=(v0342_intent is not None and dea_out != v0342_intent),
                                  targets=target_outputs, note=note))


def g2_eval(edges):
    nodes = sorted({x for e in edges for x in e} | {"d", "e", "j"})
    c = dea_ref._closure(nodes, edges)
    ctl = {n: {p for p in nodes if n in c[p]} for n in nodes}
    return (bool(ctl["d"] & ctl["e"] & ctl["j"]), bool(ctl["e"] & ctl["j"]), bool(ctl["d"] & ctl["e"]))


def g2_li(edges):
    nodes = sorted({x for e in edges for x in e} | {"d", "e", "j"})
    UA = {(n, f"r_{n}") for n in nodes}
    RH = {(f"r_{a}", f"r_{b}") for a, b in edges}
    PA = {("r_e", "p_exec"), ("r_j", "p_adj")}
    import engines.rbac_li as rl
    return not rl.safe(UA, PA, RH, [({"p_exec", "p_adj"}, 2)])


EXP_G2 = {k: g2_eval(v) for k, v in M.G2.items()}
for name, edges in M.G2.items():
    out = g2_eval(edges)
    exp = dict(M.G2_V0342_INTENT)[name]
    exp43 = (True, True, True) if name.startswith("S8") else exp
    # S8 under v0.3.4.3 p.8-9: TCB not exempt; acts attributed to every controlling principal for T3, H_EJ, H_DE
    reg("G2", name, "included", list(out), list(exp43), list(exp), {"Li-RH H_EJ": g2_li(edges)},
        "v0.3.4.3 p.8-9: TCB not exempt" if name.startswith("S8") else "")
for name, edges in M.G2_NEW.items():
    out = g2_eval(edges)
    reg("G2", name, "newly constructed", list(out), [False, True, False], None, {"Li-RH H_EJ": g2_li(edges)},
        "transitive control P->orc->e plus P->j")

for name, s in M.G3.items():
    ctrl = s["ctrl"]
    if s["assign"] is None:
        out, tgt = 0, {}
    else:
        j, disp = s["assign"]
        m = {"n": 1, "exec": [s["prod"]], "adj": [j], "disp": [disp],
             "grants": [(u, 0, d) for (u, d) in s["grants"]], "exec_perm_revoked": []}
        out = len(dea_ref.ej_effective(m, ctrl))
        tgt = {"Bertino A-IDX": len(T.tr_ej_bertino_idx(m)), "W&L-07 A-IDX": len(T.tr_ej_wl_idx(m))}
    exp43 = 0 if name.startswith("M8") else M.G3_V0342_INTENT[name]
    reg("G3", name, "included", out, exp43, M.G3_V0342_INTENT[name], tgt,
        ("v0.3.4.3 p.10: guard covers every s in Sigma_adj" if name.startswith("M8") else "") +
        ("; targets see identities only (proxy collapse not representable in A)" if name.startswith("M5") else ""))

for name, evs in M.g4_scenarios().items():
    objs = []
    for e in evs:
        if e[2]["oid"] not in [x["oid"] for x in objs]:
            objs.append(e[2])
    cases = dea_ref.case_of(objs)          # Case(x) over the complete record (classes only merge)
    ev2 = [(e[0], e[1], cases[e[2]["oid"]], e[3]) + tuple(e[4:]) for e in evs]
    out = len([i for i in dea_ref.ledger(ev2, 1) if ev2[i][0] == "cont"])
    mm = {"B": 1, "events": [list(x) for x in ev2]}
    tgt = {"Bertino A-INST": len(T.tr_led_bertino_inst(mm)), "Bertino A-MERGE": len(T.tr_led_bertino_merge(mm)),
           "Bertino B": len(T.tr_led_bertino_B(mm))}
    intent = M.G4_V0342_INTENT.get(name)
    status = "newly constructed" if "(new)" in name else "included"
    exp43 = intent if intent is not None else {"N1_term_reopen_cont_cont (new)": 1,
                                               "N2_double_term_single_reopen (new)": 1}[name]
    reg("G4", name, status, out, exp43, intent, tgt,
        "Case(x) computed by the DEA reference and supplied to targets as an input attribute" +
        ("; documented DEA residual" if name.startswith("A7") else ""))

for name, m in M.NAP_NAMED.items():
    out = bool(dea_ref.nap(m))
    tgt = {"WSP-LABEL": bool(T.tr_nap_wsp_label(m)), "Bertino-B": bool(T.tr_nap_bertino_B(m)),
           "Li-RH": bool(T.tr_nap_li_rh(m)), "Basin-TICK": bool(T.tr_nap_basin_tick(m)),
           "WSP-A1": bool(T.tr_nap_wsp_all(m))}
    reg("NAP", name, "included", out, M.NAP_NAMED_EXPECTED[name], None, tgt)
chain = {"states": ["0", "1", "2", "3"], "start": "0", "goals": ["3"],
         "edges": [("a1", "0", "1", True), ("a2", "1", "2", True), ("a3", "2", "3", True)]}
reg("NAP", "diagnostic_bound_depth2 (new)", "newly constructed", dea_ref.nap_diagnostic(chain, 2), "undetermined", None,
    {"note": "no compared formalism has a three-valued verdict"})

RES["coverage"] = {
    "excluded": ["NAP hybrid cases (dea-nap-hybrid-cases.py): continuous flows; no discrete target semantics in the four "
                 "formalisms; not translated",
                 "G1 placement-vs-disposition cases: typing only (P(x) not in Sigma_adj); no target counterpart tested"],
    "unavailable": ["Wang & Li 2010 TISSEC: all comparisons SOURCE-UNVERIFIED",
                    "DEA v0.3.4.3 .tex source: not in workspace (PDF used)"],
    "historical_scripts_rerun_previously": "The original package's '53/53, 32/32' figures refer to v0.3.4.2/v0.3.4.1 "
                                           "semantics; they are NOT counted here. Regression cases above are re-encoded "
                                           "and re-evaluated under v0.3.4.3.",
}


def main():
    a, meta = ARGS, META
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(HERE) for f in fs if f.endswith(".py"))
    meta["harness_sha256"] = {os.path.relpath(f, ROOT): sha(f) for f in files}
    meta["python"] = platform.python_version()
    meta["static_independence"] = "passed: no engine/translation module imports dea_ref"
    meta["caveat"] = "Finite agreement is bounded regression evidence, not a general equivalence theorem."
    out = {"meta": meta, **RES,
           "counts": {"translation_comparisons": len(RES["translations"]),
                      "of_which_oracle_embeddings": sum(r["kind"] == "ORACLE-EMBEDDING" for r in RES["translations"]),
                      "proof_or_refutation_records": len(RES["proofs"]),
                      "regression_cases": len(RES["regression"])}}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True, default=list)
    cat = []
    for t in RES["translations"]:
        for d in ("forward", "backward"):
            cm = t[d + "_min_countermodel"]
            if cm:
                cat.append({"test": t["id"], "direction": d, "target": t["target"], "regime": t["regime"],
                            "kind": t["kind"], "failures_in_class": t[d + "_failures"],
                            "models_in_class": t["models"], **cm})
    for p in RES["proofs"]:
        if p["witness"]:
            cat.append({"proof": p["id"], "status": p["status"], "witness": p["witness"]})
    with open(os.path.join(os.path.dirname(a.out), "countermodels.json"), "w") as f:
        json.dump(cat, f, indent=1, sort_keys=True, default=list)
    for r in RES["translations"]:
        print(f'{r["id"]:26s} {r["regime"][:8]:8s} n={r["models"]:6d} '
              f'fwd={"ok" if r["forward_preserved"] else "FAIL(%d)" % r["forward_failures"]:11s} '
              f'bwd={"ok" if r["backward_preserved"] else "FAIL(%d)" % r["backward_failures"]}')
    for p in RES["proofs"]:
        print(f'{p["id"]:18s} check={p["machine_check_passed"]}  {p["status"]}')
    print("regression mismatches vs v0.3.4.3 expectation:",
          [r["case"] for r in RES["regression"] if not r["matches_expected"]])
    print("wrote", a.out)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"INTERNAL ERROR: {e!r}\nNo results were written.\n")
        sys.exit(4)
