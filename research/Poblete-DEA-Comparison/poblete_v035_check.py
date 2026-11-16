#!/usr/bin/env python3
"""Re-evaluate the Poblete et al. (2026) readings PB-1..PB-4 under the DEA v0.3.5 working-draft gate
(Eq. temporal-execconflict + validity-def, PDF pp.10-11): outcome in {CONFLICT, NO_CONFLICT_ESTABLISHED,
UNDETERMINED}; MayAdjudicate requires RecordComplete and no witness. Stdlib only; reuses ../dea-adr-001.
Usage: python3 poblete_v035_check.py --out poblete-v035-results.json
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "dea-adr-001"))
import adr001_ctrl as A
from poblete_adr001_check import READINGS

# RecordComplete (v0.3.5 p.10): authenticated graph versions, executing event, valid seal, adjudication event,
# order t_E <= sigma <= t_J. "as_reported": what the paper documents (p.26 traceability partial; p.30 no explicit
# identity/authorization mechanisms; pp.31-32 full records unavailable) -> False. "hypothetical": assumed complete.
RECORD = {"as_reported": False, "hypothetical_complete": True}


def v035(m, record_complete):
    order_ok = m["tE"] <= m["sigma"] <= m["tJ"]
    witness, w = A.conflict(m, "C", "causal")
    if witness:
        out = "CONFLICT"
    elif record_complete and order_ok:
        out = "NO_CONFLICT_ESTABLISHED"
    else:
        out = "UNDETERMINED"
    return {"outcome": out, "witness_principals": w, "event_order_ok": order_ok,
            "MayAdjudicate_control_part": out == "NO_CONFLICT_ESTABLISHED"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="poblete-v035-results.json"); a = ap.parse_args()
    res = {k: {"reading": d, **{rk: v035(m, rv) for rk, rv in RECORD.items()}} for k, (m, d) in READINGS.items()}
    res["_note"] = ("A positive witness is reported as CONFLICT even when the record is incomplete (v0.3.5 p.11: a recorded "
                    "witness yields CONFLICT). PB-2 'hypothetical_complete' additionally assumes the record start t0 covers "
                    "the Stage-4 authorization (v0.3.5 O2, p.38, lookback open).")
    json.dump(res, open(a.out, "w"), indent=1)
    for k, v in res.items():
        if not k.startswith("_"):
            print(k, v["as_reported"]["outcome"], "|", v["hypothetical_complete"]["outcome"])


if __name__ == "__main__":
    main()
