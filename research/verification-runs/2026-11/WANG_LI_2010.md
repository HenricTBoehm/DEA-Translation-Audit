# W1 source review supplement

**CONFIRMED** source identity. Qihua Wang and Ninghui Li, *Satisfiability and Resiliency in Workflow Authorization Systems*, ACM TISSEC 13(4), Article 40, December 2010, DOI [10.1145/1880022.1880034](https://doi.org/10.1145/1880022.1880034). The journal PDF inspected has SHA-256 `e3e40380bf674ccb891d792a9d16129f39b734471f083c2ab3803d2caa948e4d`. The RP/VP published result snapshots retain their historical W1 status. This supplement checks definitions directly in the journal edition.

| Crosswalk | Reviewed journal definitions | Finding |
|---|---|---|
| C1a, C1b | Defs. 1–4, pp. 40:6–7 | **CONFIRMED** native user equality, inequality and existential step-set constraints for identity-level assignments. Example `!=(EXISTS{s_D,s_E}, s_J)` rejects exactly the nominal all-three-equal triple. Distinct assigned users can share a controller; native inequality alone permits that case. No W&L-07 run is transferred. |
| C1c | Defs. 1–2, pp. 40:6–7 | **UNDETERMINED** for a native optional-gate encoding. The source supports declared binary relations. A synthetic user for a missing gate changes the domain and must be identified as a reduction. |
| C2, C2t | Defs. 1–5, pp. 40:6–8 and §6, pp. 40:24–26 | **CONFIRMED** that binary relations enter the model as inputs and the §6 games vary user availability. A precomputed co-control relation still imports an external result. Admissible expressibility and the required temporal-control translation remain **UNDETERMINED**. |
| C3 | Defs. 2, 4–5, pp. 40:6–8 | **CONFIRMED** valid plan is an authorization and constraint predicate on step assignments. An independent epistemic validity interpretation would require a translation argument. |
| C4, C4d | Def. 4, §3 and Defs. 6–8, pp. 40:7–8, 40:24–26 | **CONFIRMED** WSP asks for a valid assignment to a fixed step set. Resiliency changes quantification over user availability. Neither directly supplies a goal-relative path predicate or a bounded diagnostic uncertainty status. An admissible NAP translation and its expressiveness remain **UNDETERMINED**. |
| C6 | Defs. 2, 4–5; §6 budget | **UNDETERMINED** for admissible ledger expressibility. The decremental game budget counts absent users. DEA counting, case identity, terminal closure and independent reopening require separate correspondence. |

The 2007 comparison and tests remain bound to their own source. This targeted definition check adds no TISSEC engine run and establishes no general non-expressibility theorem.
