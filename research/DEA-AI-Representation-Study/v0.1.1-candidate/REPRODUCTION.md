# Provenance and reproduction

| Upstream | Confirmed GitHub PR head |
|---|---|
| #13 | b1631406c9434a214da98b2a49115be26a40c7db |
| #14 | 228d793b1a1c2edcd7e0b1c0cc914482b76359e6 |
| #15 | ed22942b350ac54f9dd32b07e8ef8a3860c3428f |
| #16 | f821785d6fb623d7f62737324fde039b96d3fcaf |

Read PR #13 oracle.py, EVENT_SEMANTICS.md and SHA256SUMS by exact commit, and P-01 by 91e842fdae94356ff323f3afb2e99245369108da. Recomputed the UTF-8 oracle.py SHA-256 (df0a42304114a21468318a43a602ede71a05c68df33632a48b86982a5a37ce18); it agrees with the pinned SHA256SUMS. The reference oracle is upstream, not vendored or modified. Historical study counts and the inaccessible archive digest are supplied claims.

Reproduce only the public prototypes in this directory with Node.js:

```sh
sha256sum -c SHA256SUMS
node planning-selftest.mjs
node score-selftest.mjs
```

Compare outputs to PLANNING_RESULTS.json and SCORING_FIXTURE_RESULTS.json as JSON values. For this draft, pure JavaScript test bodies ran in a hosted V8 isolate. Original Python suite, public representation rebuild, oracle-certificate integration, E4, O1/O2, private custody and model runs were NOT EXECUTED. No editor/executor with archive extraction was available. Treat the read-only source reproduction below as pending: verify the full ZIP SHA-256 before extraction, inventory all members (reject names escaping destination), retain a read-only original, and rerun the four original scripts only after inspection. Keep generations and modified candidates in a separate directory.
