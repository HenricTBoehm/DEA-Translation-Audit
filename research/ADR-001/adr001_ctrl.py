#!/usr/bin/env python3
"""DEA-ADR-001 executable model: temporal effective control and attribution (standard library only).

Usage: python3 adr001_ctrl.py [--out results/adr001-results.json]

Model (discrete time; intervals are represented by their instant sets):
  T = {0,1,2,3}; execution stage theta_E = {0,1}; adjudication stage theta_J = {2,3}.
  A model gives, for each directed control edge x->y, the set of instants at which it is active, an
  execution act by `a` at tE, an output seal time sigma >= tE, an adjudication act by `j` at tJ, and
  optional recorded independent resets {node: set of instants}.
Path semantics (DEA-ADR-001 s3):
  A  simultaneous   : exists t in W with p ->* x in E(t)
  B  union          : p ->* x in union_{t in W} E(t)
  C  time-respecting: a journey p=v0 -> ... -> vk=x with nondecreasing edge instants in W
                      (C-R: journeys are cut by a recorded reset of an intermediate node)
Windows (s4):
  stage   : W_E = theta_E,                W_J = theta_J                (audit readings)
  act     : W_E = theta_E cap [.., tE],   W_J = theta_J cap [.., tJ]
  causal  : W_E = [min theta_E, sigma],   W_J = [min theta_E, tJ]      (proposed)
ExecConflict holds iff some principal p satisfies Ctrl_{W_E}(p,a) and Ctrl_{W_J}(p,j).
"""
import argparse, itertools, json, random, sys

T = (0, 1, 2, 3)
TE, TJ = (0, 1), (2, 3)
NODES = ("p", "o", "a", "j")


def E_at(m, t):
    return [tuple(k.split("->")) for k, s in m["edges"].items() if t in s]


def closure_from(start, edges, init=None):
    R = set(init) if init is not None else {start}
    st = list(R)
    while st:
        x = st.pop()
        for (u, v) in edges:
            if u == x and v not in R:
                R.add(v); st.append(v)
    return R


def ctrl_set(m, p, W, sem, resets=None):
    """Set of identities controlled by p over window W under semantics sem."""
    W = sorted(W)
    if not W:
        return {p}
    if sem == "A":
        out = {p}
        for t in W:
            out |= closure_from(p, E_at(m, t))
        return out
    if sem == "B":
        return closure_from(p, [e for t in W for e in E_at(m, t)])
    if sem in ("C", "CR"):
        R = {p}
        for t in W:
            if sem == "CR" and resets:
                R -= {n for n, ts in resets.items() if t in ts and n != p}
            R = closure_from(p, E_at(m, t), init=R)
        return R
    raise ValueError(sem)


def windows(m, anchor):
    tE, tJ, sig = m["tE"], m["tJ"], m.get("sigma", m["tE"])
    if anchor == "stage":
        return set(TE), set(TJ)
    if anchor == "act":
        return {t for t in TE if t <= tE}, {t for t in TJ if t <= tJ}
    if anchor == "causal":
        return {t for t in T if TE[0] <= t <= sig}, {t for t in T if TE[0] <= t <= tJ}
    raise ValueError(anchor)


def ctrl_all(m, sem, W):
    nodes = sorted(set(NODES) | {x for k in m["edges"] for x in k.split("->")})
    return {p: ctrl_set(m, p, W, sem, m.get("resets")) for p in nodes}


def conflict(m, sem, anchor):
    WE, WJ = windows(m, anchor)
    cE, cJ = ctrl_all(m, sem, WE), ctrl_all(m, sem, WJ)
    wit = sorted(p for p in cE if "a" in cE[p] and "j" in cJ[p])
    return bool(wit), wit


SEMS = ("A", "B", "C")
ANCHORS = ("stage", "act", "causal")


def M(edges, tE=1, tJ=3, sigma=None, resets=None):
    return {"edges": {k: frozenset(v) for k, v in edges.items()}, "tE": tE, "tJ": tJ,
            "sigma": tE if sigma is None else sigma, **({"resets": resets} if resets else {})}


# ---------------------------------------------------------------- named countermodels
CMS = {
    "CM1_forward_relay_CTRL6b": (M({"p->a": {0, 1}, "p->o": {2}, "o->j": {3}}, tE=1, tJ=3),
        "p controls o only at 2, o controls j only at 3 (audit CTRL-6b)"),
    "CM2_reverse_relay_phantom": (M({"p->a": {0, 1}, "o->j": {2}, "p->o": {3}}, tE=1, tJ=3),
        "o controls j only at 2; p gains o only at 3: the union path p->o->j never existed in causal order"),
    "CM3_anachronistic_adjudicator_control": (M({"p->a": {0, 1}, "p->j": {3}}, tE=1, tJ=2),
        "j adjudicates at 2; p gains control over j only at 3"),
    "CM4_post_act_producer_control_unsealed": (M({"p->a": {1}, "p->j": {2, 3}}, tE=0, tJ=3, sigma=1),
        "a executes at 0; p controls a at 1, before the output is sealed at 1"),
    "CM4b_post_seal_producer_control": (M({"p->a": {1}, "p->j": {2, 3}}, tE=0, tJ=3, sigma=0),
        "as CM4, but the output is sealed at 0, before p controls a"),
    "CM5_cross_stage_relay": (M({"p->a": {0, 1}, "p->o": {1}, "o->j": {2, 3}}, tE=1, tJ=3),
        "p controls o only during execution; o controls j during adjudication"),
    "CM6_static_cycle": (M({"p->o": set(T), "o->p": set(T), "o->j": set(T), "p->a": set(T)}),
        "p and o control each other throughout"),
    "CM7_alternating_mutual_control": (M({"o->a": {0, 1}, "o->p": {2}, "p->o": {3}, "p->j": {2, 3}}, tE=1, tJ=3),
        "o controls a; o->p at 2, p->o at 3; p controls j"),
    "CM8_forward_relay_with_reset": (M({"p->a": {0, 1}, "p->o": {2}, "o->j": {3}}, tE=1, tJ=3, resets={"o": {3}}),
        "CM1 plus a recorded, independently authorised reset of o at 3"),
    "CM9_uncertain_timestamp_widened": (M({"p->a": {0, 1}, "p->o": {2, 3}, "o->j": {3}}, tE=1, tJ=3),
        "p->o known only to lie in [2,3]; fail-closed widening to {2,3}"),
    "CM10_no_common_controller": (M({"p->a": {0, 1}, "o->j": {2, 3}}), "distinct controllers throughout"),
}


# Normative expectations under the proposed configuration (C, causal window; CR where resets are recorded).
# True = ExecConflict (j may not assign any s in Sigma_adj to x); False = no conflict on control grounds.
EXPECTED = {"CM1_forward_relay_CTRL6b": True, "CM2_reverse_relay_phantom": False,
            "CM3_anachronistic_adjudicator_control": False, "CM4_post_act_producer_control_unsealed": True,
            "CM4b_post_seal_producer_control": False, "CM5_cross_stage_relay": True, "CM6_static_cycle": True,
            "CM7_alternating_mutual_control": True, "CM8_forward_relay_with_reset": False,
            "CM9_uncertain_timestamp_widened": True, "CM10_no_common_controller": False}


def run_cms():
    out = {}
    for name, (m, desc) in CMS.items():
        row = {"description": desc}
        for an in ANCHORS:
            for s in SEMS:
                c, w = conflict(m, s, an)
                row[f"{s}/{an}"] = {"ExecConflict": c, "j_may_adjudicate": not c, "common_controllers": w}
        if "resets" in m:
            c, w = conflict(m, "CR", "causal")
            row["CR/causal"] = {"ExecConflict": c, "j_may_adjudicate": not c, "common_controllers": w}
        sem = "CR" if "resets" in m else "C"
        got = conflict(m, sem, "causal")[0]
        row["expected_proposed"] = EXPECTED[name]
        row["matches_expected"] = got == EXPECTED[name]
        out[name] = row
    return out


# ---------------------------------------------------------------- model classes
SLOTS = ["p->a", "p->o", "o->p", "o->j", "o->a", "p->j"]
OPTS = [frozenset(), frozenset({0}), frozenset({1}), frozenset({2}), frozenset({3}), frozenset({1, 2}), frozenset(T)]
ALL_EDGES = [f"{x}->{y}" for x in NODES for y in NODES if x != y]


def mc_exhaustive():
    for combo in itertools.product(OPTS, repeat=len(SLOTS)):
        e = {k: v for k, v in zip(SLOTS, combo) if v}
        for tE in TE:
            for tJ in TJ:
                yield {"edges": e, "tE": tE, "tJ": tJ, "sigma": tE}


def mc_random(n, seed=20261116):
    rnd = random.Random(seed)
    for _ in range(n):
        e = {}
        for k in ALL_EDGES:
            if rnd.random() < 0.45:
                s = frozenset(t for t in T if rnd.random() < 0.5)
                if s:
                    e[k] = s
        tE = rnd.choice(TE); tJ = rnd.choice(TJ)
        yield {"edges": e, "tE": tE, "tJ": tJ, "sigma": rnd.choice([t for t in T if t >= tE])}


def analyse(models, perturb_seed=7):
    rnd = random.Random(perturb_seed)
    st = {"models": 0}
    viol = {k: 0 for k in ("I1_inclusion_A_C_B", "I2_monotone_in_activity", "I3_static_agreement",
                           "I4_no_anachronism_C_causal", "I6_cycle_equal_rows_static")}
    wit = {}
    dis = {}
    for m in models:
        st["models"] += 1
        res = {}
        for an in ANCHORS:
            for s in SEMS:
                res[(s, an)] = conflict(m, s, an)[0]
            # I1 at Ctrl level
            WE, WJ = windows(m, an)
            for W in (WE, WJ):
                cA, cB, cC = (ctrl_all(m, s, W) for s in SEMS)
                for p in cA:
                    if not (cA[p] <= cC[p] <= cB[p]):
                        viol["I1_inclusion_A_C_B"] += 1; wit.setdefault("I1", m)
        for an in ANCHORS:
            for s1, s2 in (("A", "C"), ("C", "B"), ("A", "B")):
                if res[(s1, an)] != res[(s2, an)]:
                    dis[f"{s1}!={s2}/{an}"] = dis.get(f"{s1}!={s2}/{an}", 0) + 1
        for s in SEMS:
            for a1, a2 in (("stage", "causal"), ("act", "causal")):
                if res[(s, a1)] != res[(s, a2)]:
                    dis[f"{s}:{a1}!={a2}"] = dis.get(f"{s}:{a1}!={a2}", 0) + 1
        # I2 monotonicity: add one instant to one edge
        k = rnd.choice(ALL_EDGES); t = rnd.choice(T)
        m2 = dict(m); m2["edges"] = dict(m["edges"]); m2["edges"][k] = frozenset(m["edges"].get(k, frozenset()) | {t})
        for an in ANCHORS:
            for s in SEMS:
                if res[(s, an)] and not conflict(m2, s, an)[0]:
                    viol["I2_monotone_in_activity"] += 1; wit.setdefault("I2", (m, k, t))
        # I3 static agreement
        if all(v == frozenset(T) for v in m["edges"].values()):
            for an in ANCHORS:
                if len({res[(s, an)] for s in SEMS}) != 1:
                    viol["I3_static_agreement"] += 1
            st["static_models"] = st.get("static_models", 0) + 1
        # I4 no-anachronism under C/causal: randomise all activity after max(sigma, tJ) and after tJ on j's side
        cut = max(m["sigma"], m["tJ"])
        m3 = dict(m); m3["edges"] = {}
        for kk in ALL_EDGES:
            past = frozenset(t for t in m["edges"].get(kk, ()) if t <= cut)
            fut = frozenset(t for t in T if t > cut and rnd.random() < 0.5)
            if past | fut:
                m3["edges"][kk] = past | fut
        if conflict(m3, "C", "causal")[0] != res[("C", "causal")]:
            viol["I4_no_anachronism_C_causal"] += 1; wit.setdefault("I4", (m, m3))
        # I6 cycles (static part): nodes in the same SCC of the union graph over all T have equal Ctrl rows (B)
        if all(v == frozenset(T) for v in m["edges"].values()):
            c = ctrl_all(m, "B", set(T))
            for x in c:
                for y in c:
                    if x in c[y] and y in c[x] and c[x] != c[y]:
                        viol["I6_cycle_equal_rows_static"] += 1
    return st, viol, dis, {k: str(v)[:400] for k, v in wit.items()}


def nontransitivity_witness():
    """Ctrl^C is not a transitively closed relation (s3.4)."""
    m = M({"o->j": {2}, "p->o": {3}})
    W = set(TJ)
    c = ctrl_all(m, "C", W)
    return {"model": {k: sorted(v) for k, v in m["edges"].items()}, "window": sorted(W),
            "Ctrl_C(p,o)": "o" in c["p"], "Ctrl_C(o,j)": "j" in c["o"], "Ctrl_C(p,j)": "j" in c["p"]}


def relay_properties():
    """I5a relay robustness and I5b phantom-freeness, checked on CM1/CM2 for every semantics/anchor."""
    r = {}
    for s in SEMS:
        for an in ANCHORS:
            r[f"{s}/{an}"] = {"I5a_detects_forward_relay_CM1": conflict(CMS["CM1_forward_relay_CTRL6b"][0], s, an)[0],
                              "I5b_rejects_phantom_CM2": not conflict(CMS["CM2_reverse_relay_phantom"][0], s, an)[0],
                              "I5c_detects_cross_stage_relay_CM5": conflict(CMS["CM5_cross_stage_relay"][0], s, an)[0],
                              "I4_ignores_post_act_control_CM3": not conflict(CMS["CM3_anachronistic_adjudicator_control"][0], s, an)[0],
                              "I7_counts_pre_seal_producer_control_CM4": conflict(CMS["CM4_post_act_producer_control_unsealed"][0], s, an)[0]}
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/adr001-results.json")
    ap.add_argument("--random", type=int, default=20000)
    a = ap.parse_args()
    cms = run_cms()
    ex = analyse(mc_exhaustive())
    rn = analyse(mc_random(a.random))
    res = {"time_domain": list(T), "theta_E": list(TE), "theta_J": list(TJ),
           "countermodels": cms, "relay_properties": relay_properties(),
           "nontransitivity_C": nontransitivity_witness(),
           "MC_T_exhaustive": {"slots": SLOTS, "activity_options": [sorted(o) for o in OPTS],
                               "stats": ex[0], "invariant_violations": ex[1], "disagreements": ex[2], "witnesses": ex[3]},
           "MC_T_random": {"n": a.random, "seed": 20261116, "stats": rn[0], "invariant_violations": rn[1],
                           "disagreements": rn[2], "witnesses": rn[3]}}
    import os
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=sorted)
    print(json.dumps({k: res[k]["invariant_violations"] for k in ("MC_T_exhaustive", "MC_T_random")}))
    print(json.dumps(ex[2])); print(json.dumps(rn[2])); print(ex[0], rn[0])
    bad = sum(ex[1].values()) + sum(rn[1].values()) + sum(not v["matches_expected"] for v in cms.values())
    print("regression:", sum(v["matches_expected"] for v in cms.values()), "/", len(cms))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
