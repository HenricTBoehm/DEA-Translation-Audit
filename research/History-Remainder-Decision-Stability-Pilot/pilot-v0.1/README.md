# HR-1 × Decision Stability, independent pilot v0.1

A stacked executable pilot for [Draft PR #8](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/8). The protocol at the base commit is the frozen research plan. See [execution and decision report](REPORT.md), [counterexamples](COUNTEREXAMPLES.md), [pre-run criteria](EVALUATION_CRITERIA.md) and [remaining obligations](OPEN_OBLIGATIONS.md).

## Reproduce

From this directory, use CPython 3.12.14, Bash, Git, GNU patch, unzip and sha256sum. Supply the original HR-1 ZIP with the checksum recorded in the parent protocol. Fetch the P-01 comparison ref to make its pinned commit locally available.

```sh
git fetch origin research/precision-amendment-p01
bash verify.sh /absolute/path/to/dea-hr1-history-remainder.zip
```

The verifier reads the pinned P-01 implementation from commit 91e842fdae94356ff323f3afb2e99245369108da. It compares the complete JSON from all six HR-1 runs, including the original cases, and both hash-seed runs of the new pilot. All corrections are applied in scratch. Checks are fail-on-difference. Wall times are observations and are excluded from byte-equality assertions.

For the timing benchmark, extract the pinned P-01 tree from git and place its research/Precision-Amendment-P01 directory on PYTHONPATH, then run:

```sh
PYTHONHASHSEED=0 python3 pilot.py --n 1000 --out /tmp/pilot.json --timing /tmp/pilot-timing.json
cmp /tmp/pilot.json evidence/PILOT.json
```

The substantive input is a fixed finite threshold policy over historical facts. Governance and scientific evidence have separate roles. Missing authentication, invalid event order, unjustified historical coverage and incomplete procedure dependencies each have explicit fixtures. The implementation consumes synthetic oracle attestations and an exact finite world census. Actual certificate production, verified world abstraction and enforcement are outside this executable pilot.
