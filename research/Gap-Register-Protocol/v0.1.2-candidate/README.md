# DEA Research Gap Register · v0.1.2 Candidate

**FREEZE NO-GO.** The bounded synthetic oracles and the public revision checks are executable. The candidate awaits a human review, accepted comparator profiles, and private assessor custody before scored work.

Read the [protocol](PROTOCOL_v0.1.2.md), [freeze-readiness report](FREEZE_READINESS_REPORT.md), and [open obligations](OPEN_OBLIGATIONS.md). This draft is stacked on the exact [PR #12 review](https://github.com/HenricTBoehm/DEA-Translation-Audit/pull/12). Its own commit adds this directory only.

Run from this directory with CPython 3.12 and the standard library:

```sh
bash verify.sh
```

The script checks the candidate digest manifest and regenerates the public assessor cases/results in memory under two hash seeds, comparing exact bytes. `PUBLIC_CASES.json` is a public assessor bundle with explicit truth and expected labels. A participant receives only canonical evidence bytes as specified in [EVIDENCE_INTERFACE.md](EVIDENCE_INTERFACE.md). The repository contains no private corpus.

To replay the preceding version, use the exact v0.1.1 and D0 ZIPs in [SOURCE_MANIFEST.md](SOURCE_MANIFEST.md) with `research/Gap-Register-Freeze-Review/v0.1.1/verify.sh`.

`python3 verify.py --write-public` is a maintainer regeneration command. Review expectation and fixture changes prospectively with the manifest; the ordinary test command performs neither regeneration on disk nor expectation edits.
