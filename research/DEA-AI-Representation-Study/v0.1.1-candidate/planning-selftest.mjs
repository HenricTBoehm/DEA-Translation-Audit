import {binomialCdf, pairedInterval, planningTable} from "./planning.mjs";

function must(condition) {
  if (!condition) throw new Error("planning check failed");
}

must(binomialCdf(5, 5, 1) === 1);
must(Math.abs(binomialCdf(4, 1, 0.5) - 5/16) < 1e-12);
must(pairedInterval(0, 0, 0) === null);
const tail = 0.05 / 36;
const noDiscordance = pairedInterval(300, 0, 0);
must(Math.abs(noDiscordance[1] - (1 - (tail ** (1 / 300)))) < 1e-10);
must(Math.abs(noDiscordance[0] + noDiscordance[1]) < 1e-12);
const reversed = pairedInterval(300, 30, 8);
const forward = pairedInterval(300, 8, 30);
must(Math.abs(forward[0] + reversed[1]) < 1e-12);
must(Math.abs(forward[1] + reversed[0]) < 1e-12);
must(pairedInterval(100, 0, 100).every(Number.isFinite));
let rejected = false;
try { pairedInterval(100, 60, 60); } catch { rejected = true; }
must(rejected);
const report = planningTable();
must(report.grid.length === 20 && report.grid.filter(row => row.better === 0).every(row => row.demonstrations === 0));
console.log(JSON.stringify(report, null, 2));
