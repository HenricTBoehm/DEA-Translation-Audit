# DEA v0.3.5.1 Precision Amendment P-01

Non-normative research candidate for the historical-closure and commit-safety section. P-01 refines decision dependencies and event admission. DEA v0.3.4.3 is the frozen reference.

## G-B. Event domain and admissible extensions

Fix one governed attempt, exact output version (x), record start (t_0), dependency policy, and a scope containing the proposed disposition and protected bundle versions. An authenticated assertion has a nonempty ID and one of the following event tags. Authentication in the fixture stands for external evidence verification.

| Tag | Required payload |
|---|---|
| produce | Exact output version, producer identity, input version list |
| seal | Exact output version, map of sealed dependency-role keys to exact versions |
| adjudicate | Exact output version, adjudicator identity, exact committed decision roots by role |
| control | Typed source and target, protected channel, effect persistence classification |
| reset | Typed target and affected channels. Effect deletion additionally needs independence, exact scope and successful neutralization. |
| read | Actor and exact read object |

Control and reset endpoints occupy disjoint namespaces for operational identities and exact artifact versions. The attested map resolves identity keys to canonical principals for this attempt. An omitted alias means the attestation treats that key as canonical. Exact artifact references identify protected content or the corresponding evidence object. Role keys identify exclusive instances of obligations within a decision, for example *checks/a/rubric*.

Use lexicographic coordinates in $\mathbb N_0\times\mathbb Q$. A signed rank assertion includes its timestamp in the same envelope. Join compatible partial assertions by event ID. Identical retransmissions are idempotent. Two distinct IDs occupying one confirmed coordinate, or one authenticated ID with unequal values of a fixed field, are contradictory. Exactly one production, seal and adjudication belong to the selected output version. Require $t_0\le\tau_{\rm produce}$ and strict produce–seal–adjudicate order. Auxiliary activity after the proposed adjudication supplies no witness for this attempt. Pre-window effects enter the replay through the initial historical certificate.

An admissible extension preserves every authenticated field. It can complete missing fields of the same ID, add a missing lifecycle event with a fresh ID and available coordinate, and supply the required verified bindings. An immutable contradiction or out-of-grammar authenticated assertion persists under extension. This includes authenticated version mismatch, or absence of a sealed role from an authenticated closure already certified complete. An uncertified incomplete closure can still receive its missing evidence.

$$
\operatorname{WellFormedEvents}(R_{\mathrm{auth}})=
\begin{cases}
\bot & \text{if no admissible extension exists},\\
\top & \text{if the authenticated record supplies the required evidence},\\
? & \text{otherwise}.
\end{cases}
$$

The submission gate withholds a definite result when an unmatched unverified assertion remains. A matching authenticated assertion resolves it. This accounts for W3: the authenticated projection alone satisfies the structural rules, while the submitted late-seal claim remains unverified. Such a claim supplies neither a contradiction nor a witness.

**Order-fragment argument.** Known lifecycle timestamps must be nondecreasing in role order and lie above $t_0$. Known lifecycle coordinate pairs must strictly increase. These are necessary by projection and sufficient for the stated bounded order fragment. Fill missing timestamps at the preceding valid tick, starting at $t_0$. Fill unresolved ranks with distinct rationals respecting the fixed anchors. Any nonempty rational gap can host the finite number of required ranks while avoiding finitely many occupied auxiliary positions. Unbounded ends likewise have room. This argument relies on rank density and the bounded event grammar. Clock provenance and distributed ordering remain separate obligations.

**Growth.** Under fixed scope, policy and immutable facts, $R\subseteq R'$ implies that completions of $R'$ form a subset of completions of $R$. Therefore $\bot$ is absorbing under append-only authentic evidence. Missing evidence can resolve to $\top$ or reveal a contradiction. A valid trace can become invalid through an authenticated fork, or unresolved through a new relevant partial record. A complete frozen snapshot excludes adding records under the same certificate. A negative conflict verdict is also scoped to its snapshot. Retraction, correction and scope changes are separate operations.

## G-A. Versioned decision dependencies and effective control

A decision binding is mandatory when the proposed disposition consumes the version or its value can determine whether the disposition is allowed by the declared evaluation procedure. This can include rubric, executable criteria, thresholds, references, instructions and configuration, with all required indirect dependencies. Informational artifacts contribute no binding. Define $\operatorname{Bound}^{\star}(j,x,\nu)$ as the least closure of authenticated committed roots under authenticated mandatory links. Cycles are allowed. For a negative result, an independent certificate must attest that the roots and all relevant reachable links were enumerated against the actual procedure, including condition-dependent and dynamically resolved references.

Every sealed dependency role must resolve to the same exact version in the committed closure. Merely finding those bytes under a different role does not satisfy the pin. Commit-specific roles may be added when authorized by the procedure and covered by the certified closure. A confirmed replacement of a sealed version is an immutable contradiction in this attempt. An unverified resolution or uncertified missing binding remains unresolved. A policy-authorized replacement needs a separate attempt with explicit provenance. Snapshot stability binds graph, identity, output, dependencies, history and policy versions from evaluation through commit. Equal labels in the fixture stand for comparison of authenticated bundles. Commit enforcement must be atomic.

Use the underlying potential-effect state of v0.3.5.1 with typed endpoints and exact artifact versions. A supported authenticated persistent-capable control edge transfers origin principals to the affected target channel. Historical seeds carry independently attested surviving influence. Read-only access creates no control token. An unverified claim supplies no positive witness. A verified reset deletes exactly the effects on its target and attested channels. A credential reset alone leaves criteria effects. A reset of the source leaves effects already propagated downstream. Producer attribution includes supported potential influence through mutability up to the seal and effects copied from the production inputs. Seal fixes that attribution. The model conservatively preserves accumulated production lineage after neutralizing the producer.

$$
J^\star_{j,x}(t_J)=J_j(t_J)\cup
\bigcup_{r\in\operatorname{Bound}^{\star}(j,x,\nu_{\rm commit})}
\operatorname{EffectiveControllers}_{S_{t_J^-}}(r).
$$

$J_j$ includes the adjudicator's canonical principal. A witness identifies the common principal, production-side evidence, and either identity-side evidence or the versioned mandatory dependency path with its control evidence. It establishes potential control in the certified model. Actual manipulation is a distinct empirical claim. Later exposure of the *same protected version* before commit counts (RA2). Merely publishing a new immutable version does not create control over the version that is pinned and actually read. Attach mutable resolution or evaluation policy to its own versioned dependency when relevant. Optimizing against known reference material remains a separate question.

| Condition | Verdict |
|---|---|
| $\bot$ | MODEL_INVALID |
| $?$, or unresolved submission authentication | UNDETERMINED |
| $\top$ and supported $P_x\cap J^\star_{j,x}$ witness | CONFLICT |
| $\top$, empty intersection, certified historical and control-record coverage, complete authenticated dependencies, compatible seal pins and stable attested snapshots | NO_CONFLICT_ESTABLISHED |
| Otherwise | UNDETERMINED |

A supported witness may block despite incomplete global coverage when the constituent evidence, bindings and event order are established. A negative result is scoped to the authenticated model. Disposition authority is a separate condition.
