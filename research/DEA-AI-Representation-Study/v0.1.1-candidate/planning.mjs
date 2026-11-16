// Public synthetic planning only. No model responses, item bank, or oracle.
export function binomialCdf(n, x, p) {
  if (x < 0) return 0;
  if (x >= n || p === 0) return 1;
  if (p === 1) return 0;
  let logMass = n * Math.log1p(-p), sum = 0;
  const logOdds = Math.log(p) - Math.log1p(-p);
  for (let k = 0; k <= x; k++) {
    sum += Math.exp(logMass);
    logMass += Math.log(n - k) - Math.log(k + 1) + logOdds;
  }
  return Math.min(1, sum);
}

function root(n, x, target) {
  let lo = 0, hi = 1;
  for (let i = 0; i < 48; i++) {
    const p = (lo + hi) / 2;
    if (binomialCdf(n, x, p) > target) lo = p;
    else hi = p;
  }
  return (lo + hi) / 2;
}

export function pairedInterval(n, worse, better, comparisons = 9, alpha = 0.05) {
  if (![n, worse, better, comparisons].every(Number.isSafeInteger) ||
      !(alpha > 0 && alpha < 1) || n < 0 || worse < 0 || better < 0 ||
      worse + better > n || comparisons < 1) throw new Error("invalid counts or family");
  if (!n) return null;
  const tail = alpha / (4 * comparisons);
  const low = x => x === 0 ? 0 : root(n, x - 1, 1 - tail);
  const high = x => x === n ? 1 : root(n, x, tail);
  return [low(worse) - high(better), high(worse) - low(better)];
}

export function planningTable(reps = 2000) {
  let state = 38141;
  function uniform() {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    return state / 4294967296;
  }
  const grid = [];
  for (const n of [60, 120, 240, 600, 1200]) {
    const memo = new Map();
    for (const [worse, better] of [[0, 0.15], [0.02, 0.12], [0.05, 0.10], [0, 0]]) {
      let demonstrations = 0;
      for (let trial = 0; trial < reps; trial++) {
        let w = 0, b = 0;
        for (let i = 0; i < n; i++) {
          const draw = uniform();
          if (draw < worse) w++;
          else if (draw < worse + better) b++;
        }
        const key = w + "/" + b;
        if (!memo.has(key)) memo.set(key, pairedInterval(n, w, b)[1]);
        if (memo.get(key) < -0.05) demonstrations++;
      }
      grid.push({n, worse, better, reps, demonstrations});
    }
  }
  return {seed: 38141, family: 9, alpha: 0.05, target_upper: -0.05,
          grid, noDiscordanceUpper: Object.fromEntries([60,120,240,600,1200].map(n=>[n,pairedInterval(n,0,0)[1]]))};
}
