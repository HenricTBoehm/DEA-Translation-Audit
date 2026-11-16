import {scoreResponse, scoreScheduled} from "./score-contract.mjs";
const cert = (verdict, code, claim, support = [0,1]) =>
  ({verdict,evidenceRows:[0,1,2,3],alternatives:[{code,claim,support,allowedExtra:[2]}]});
const answer = (action, code, claim, support = [0,1], extra = []) =>
  ({action, proof:{code,claim,support,extra}});
const conflict = cert("BLOCK_CONFLICT","scoped_replay",["p","r@1","surviving"]);
const claim = conflict.alternatives[0].claim;
const fixtures = [
  [answer("BLOCK_CONFLICT","scoped_replay",claim), conflict, "verified_clean"],
  [answer("BLOCK_CONFLICT","scoped_replay",claim,[0,1],[2]), conflict, "verified_overloaded"],
  [answer("BLOCK_CONFLICT","scoped_replay",claim,[0,1],[3]), conflict, "irrelevant_extra"],
  [answer("BLOCK_CONFLICT","scoped_replay",claim,[0,9]), conflict, "nonexistent_row"],
  [answer("BLOCK_CONFLICT","scoped_replay",["q","r@1","surviving"]), conflict, "wrong_principal"],
  [answer("BLOCK_CONFLICT","scoped_replay",["p","r@0","surviving"]), conflict, "wrong_version"],
  [answer("BLOCK_CONFLICT","scoped_replay",["p","r@1","potential"]), conflict, "wrong_route"],
  [answer("BLOCK_CONFLICT","scoped_replay",claim,[0]), conflict, "incomplete_support"],
  [answer("RELEASE","unfounded",[]), conflict, "wrong_verdict"],
  [undefined, conflict, "missing_response"],
  [{action:"RELEASE"}, conflict, "schema_failure"],
  [answer("INVALID","duplicate_rank",[]), cert("INVALID","duplicate_rank",[]), "verified_clean"],
  [answer("INVALID","no_closed_completion",[]), cert("INVALID","duplicate_rank",[]), "wrong_reason"],
  [answer("RELEASE","scoped_replay_and_dependency_coverage",[]), cert("RELEASE","scoped_replay_and_dependency_coverage",[]), "verified_clean"],
  [answer("RELEASE","scoped_replay_and_dependency_coverage",[],[0]), cert("RELEASE","scoped_replay_and_dependency_coverage",[]), "incomplete_support"],
  [answer("BLOCK_UNDETERMINED","history_open",[]), cert("BLOCK_UNDETERMINED","rank_unverified",[]), "wrong_reason"]
];
for (const [reply, certificate, expected] of fixtures)
  if (scoreResponse(reply,certificate).justification !== expected) throw new Error(expected);
const aggregation = scoreScheduled([{run:"first",certificate:conflict},{run:"second",certificate:conflict}],
  [{run:"first",answer:{action:"RELEASE"}}]);
if (aggregation.scheduled !== 2 || aggregation.counts.schema_failure !== 1 ||
    aggregation.counts.missing_response !== 1 || aggregation.counts.wrong_verdict !== 2)
  throw new Error("missing or malformed answer was lost");
console.log(JSON.stringify({synthetic_cases:fixtures.length,aggregation_checks:4,status:"PASS"}));
