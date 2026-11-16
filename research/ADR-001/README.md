# DEA-ADR-001 — Temporal Effective Control and Attribution

**Status: PROPOSED / NON-NORMATIVE.** Research and architecture proposal, not an accepted change to DEA v0.3.4.3 and not a proof of novelty or effectiveness. In particular, the accompanying DEA v0.3.5 manuscript is a *working draft*, not the normative baseline.

## Provenance

The original user-supplied `dea-adr-001.zip` is retained **unchanged** in `source-archive/dea-adr-001.zip` (SHA-256 in `SHA256SUMS`). Four extracted substantive artifacts are published verbatim:

- `DEA-ADR-001_temporal-effective-control.md`: design drivers, alternative temporal control semantics, countermodels, and proposed decision.
- `adr001_ctrl.py`: standalone Python 3 standard-library test harness.
- `adr001-regression-cases.json`: separately documented named regression cases.
- `results/adr001-results.json`: supplied saved full-run results (not a substitute for rerunning the harness).

The ZIP also contains `__pycache__/adr001_ctrl.cpython-314.pyc`, which is **not** tracked as a separate source file. The ZIP is retained verbatim for provenance; inspect before executing code or using bytecode from untrusted sources.

## Local checks performed at intake (2026-11-16)

- ZIP CRC test: PASS (5 members).
- SHA-256 hashes calculated on the extracted source and compared to the supplied standalone ADR document / JSON files: exact byte matches.
- Invoked `run_cms()` directly from the supplied `adr001_ctrl.py`: **11/11 named countermodels matched** the embedded expected conflict decisions and saved `countermodels` JSON.
- **The full 470,596 + 20,000 model run was not rerun at this intake.** Counts in the stored `results/adr001-results.json` remain results *reported by the submitted package*.

## Reproduction

From the repository root:

```sh
cd research/ADR-001
sha256sum -c SHA256SUMS
python3 adr001_ctrl.py --out /tmp/adr001-results.json
# Then compare the generated JSON with results/adr001-results.json
```

The full run may take several minutes depending on Python and host. The output path is intentionally outside the committed results directory.

## Explicitly unresolved

1. Behavioural assumption A-PLANT: distinguish the **capability for persistent interference** from evidence that interference occurred.
2. Adjudication should require a sealed result: establish `t_exec <= seal <= t_adj` as a well-formedness precondition.
3. Same-instant reset/control-event order and reset scope require a normative definition; CM8 depends on these choices.
4. Principal identity, aliases/key rotation, and mutual control must not be silently conflated.
5. Temporal reachability over a fixed window need not be transitive; downstream DEA definitions must be reviewed before adoption.
6. The JSON regression specification and Python fixture table are separate artifacts; the Python script currently hardcodes named countermodels instead of reading `adr001-regression-cases.json`.

This directory is **a companion research artifact** within the translation-audit repository. It does **not** modify `RP-1.0/`, `VP-1.0/`, the source DEA baseline or any audit result. Review this as a separate Draft PR; do not merge as a normative architecture decision.
