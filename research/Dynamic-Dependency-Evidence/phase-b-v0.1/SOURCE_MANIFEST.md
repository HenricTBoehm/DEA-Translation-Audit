# Sources and recorded environment

Verified remote PR heads on 16 November 2026. Phase A was also verified against its committed digest manifest. These references are pinned source objects, independent of later branch movement.

| Source | Exact pin | Use |
|---|---|---|
| PR #7 | `91e842fdae94356ff323f3afb2e99245369108da` | P-01 exact-version dependency and tri-valued admission |
| PR #11 | `7fee1797e31963fe60720476d8f34305148e2415` | Limits of detecting omitted dependencies under identical inputs |
| PR #12 | `80d0e5a77937df62521f3a4f47a9437097ad5eb7` | Evidence separation, X-TRUST and freeze limitations |
| PR #13 | `b1631406c9434a214da98b2a49115be26a40c7db` | Bounded neutral wire and SR-1 baseline |
| PR #14 | `228d793b1a1c2edcd7e0b1c0cc914482b76359e6` | Parent commit, D0, D1 and OPA SR-1 adapters, Phase A reference observations |

D0 and D1 are the same scoped source translations used by Phase A. Full D0 manuscript provenance and SHA are recorded there in MAPPING.md. The SHA-256 fingerprints of the unchanged consumer files are:

```text
6e23b95720170c80b99ae239e487671c02ff85f4f7b55e411de11bab9caceb89  d0.py
77f843168f00534ff98c68640ac973e74f242722144ca4bccb5cbe3dcd6dc0c1  d1.py
a11225f914174baf7182b4ee40969dca14a039cff26d8f219628b1f8eb3a32c3  gate.rego
```

Official OPA v1.22.4 linux/amd64 static asset SHA-256 `35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba`, verified by the Phase A adapter before execution. No OPA assets committed. Debian 13.6, Linux 6.18.57 x86-64, CPython 3.12.14 and glibc 2.41. No extra Python dependency.

The preinstalled strace 6.13 binary (SHA-256 `69f88291a4e47f258b8e32b089c919a247509f063ef3d6afe5389939051102b3`) has no matching dpkg package record here. A bounded local capability probe returned PTRACE_TRACEME “Operation not permitted”. strace data collection is NOT EXECUTED. E2 uses the Linux kernel inotify facility via installed libc. The separate adjudicating reference additionally uses child-owned /proc file descriptors. See [inotify(7)](https://man7.org/linux/man-pages/man7/inotify.7.html), [proc_pid_fdinfo(5)](https://man7.org/linux/man-pages/man5/proc_pid_fdinfo.5.html), [OPA release](https://github.com/open-policy-agent/opa/releases/tag/v1.22.4).
