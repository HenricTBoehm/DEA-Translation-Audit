// Public contract prototype. The assessor must supply externally validated certificates.
const actions = new Set(["RELEASE", "BLOCK_CONFLICT", "INVALID", "BLOCK_UNDETERMINED"]);
const id = value => Number.isSafeInteger(value) && value >= 0;
const same = (left, right) => JSON.stringify(left) === JSON.stringify(right);

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
function fields(value, names) {
  return isObject(value) && same(Object.keys(value).sort(), [...names].sort());
}
function setOfIds(values) {
  return Array.isArray(values) && values.every(id) && new Set(values).size === values.length;
}
function sameSet(a, b) {
  return a.length === b.length && a.every(value => b.includes(value));
}

export function scoreResponse(response, certificate) {
  if (!actions.has(certificate.verdict) || !Array.isArray(certificate.alternatives) ||
      !certificate.alternatives.length || !setOfIds(certificate.evidenceRows))
    throw new Error("unusable assessor certificate");
  const missing = response === undefined;
  const valid = fields(response, ["action", "proof"]) && actions.has(response.action) &&
    fields(response.proof, ["code", "claim", "support", "extra"]) &&
    typeof response.proof.code === "string" && Array.isArray(response.proof.claim) &&
    response.proof.claim.every(value => typeof value === "string") &&
    setOfIds(response.proof.support) && setOfIds(response.proof.extra);
  const action = valid ? response.action : null;
  const correct = action === certificate.verdict;
  let justification = valid ? "wrong_verdict" : (missing ? "missing_response" : "schema_failure");
  if (valid) {
    const proof = response.proof;
    const overlaps = proof.extra.some(x => proof.support.includes(x));
    if ([...proof.support, ...proof.extra].some(x => !certificate.evidenceRows.includes(x))) {
      justification = "nonexistent_row";
    } else if (overlaps) {
      justification = "duplicate_support";
    } else if (correct) {
      const byCode = certificate.alternatives.filter(row => row.code === proof.code);
      const exactClaim = byCode.filter(row => same(row.claim, proof.claim));
      const exactSupport = exactClaim.filter(row => sameSet(row.support, proof.support));
      if (!byCode.length) justification = "wrong_reason";
      else if (!exactClaim.length) {
        const labels = ["wrong_principal", "wrong_version", "wrong_route"];
        const differences = byCode.map(row => labels.filter((label, index) => row.claim[index] !== proof.claim[index]));
        justification = action === "BLOCK_CONFLICT" && proof.claim.length === 3 &&
          differences.every(row => row.length === 1 && row[0] === differences[0][0])
          ? differences[0][0] : "wrong_claim";
      } else if (!exactSupport.length) {
        justification = exactClaim.some(row => proof.support.every(x => row.support.includes(x)))
          ? "incomplete_support" : "irrelevant_or_wrong_support";
      } else if (!exactSupport.some(row => proof.extra.every(x => row.allowedExtra.includes(x)))) {
        justification = "irrelevant_extra";
      } else {
        justification = proof.extra.length ? "verified_overloaded" : "verified_clean";
      }
    }
  }
  const verified = justification.startsWith("verified_");
  return {
    wrong_verdict: !correct,
    unjustified_release: action === "RELEASE" && certificate.verdict !== "RELEASE",
    false_hold: certificate.verdict === "RELEASE" && action !== "RELEASE",
    unsupported_conflict: action === "BLOCK_CONFLICT" && !verified,
    false_invalid: action === "INVALID" && certificate.verdict !== "INVALID",
    missed_invalid: certificate.verdict === "INVALID" && action !== "INVALID",
    schema_failure: !missing && !valid,
    missing_response: missing,
    abstention_reason_wrong: correct && action === "BLOCK_UNDETERMINED" && !verified,
    verified_justification: verified,
    correct_but_bad_justification: correct && !verified,
    justification
  };
}

export function scoreScheduled(catalog, responses) {
  const index = new Map();
  const expected = new Set(catalog.map(item => item.run));
  if (expected.size !== catalog.length) throw new Error("duplicate scheduled run");
  for (const response of responses) {
    if (!expected.has(response.run) || index.has(response.run)) throw new Error("unexpected or duplicate run");
    index.set(response.run, response.answer);
  }
  const rows = catalog.map(item => ({run: item.run, ...scoreResponse(index.get(item.run), item.certificate)}));
  const counts = {};
  for (const row of rows) {
    for (const [key, value] of Object.entries(row)) {
      if (typeof value === "boolean") counts[key] = (counts[key] ?? 0) + Number(value);
    }
  }
  return {scheduled: rows.length, counts, rows};
}
