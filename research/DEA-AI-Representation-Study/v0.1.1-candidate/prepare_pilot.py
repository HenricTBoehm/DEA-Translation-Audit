"""Build exactly 48 public technical requests. This script makes no model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import random

from score import load_items, read_jsonl

HERE = Path(__file__).resolve().parent


def public_schedule(out, model, seed):
    rng = random.Random(seed)
    items = load_items()
    picked = []
    for verdict in ("CLEAR", "CONFLICT", "INVALID", "UNDETERMINED"):
        eligible = sorted(item["item_id"] for item in items.values() if item["justified"] == verdict)
        picked.extend(rng.sample(eligible, 6 if len(eligible) >= 6 else len(eligible)))
    # The original public pool has fewer than six distinct abstention views.
    # Fill remaining places from all unused views without repeating any input.
    remaining = sorted(set(items) - set(picked))
    picked += rng.sample(remaining, 24 - len(picked))
    prompts = {c: {r["item_id"]: r for r in read_jsonl(HERE / "build" / "prompts" / f"{c}.jsonl")}
               for c in ("B", "C")}
    pairs = [(condition, ident) for ident in picked for condition in ("B", "C")]
    rng.shuffle(pairs)
    runs, requests = [], []
    for order, (condition, ident) in enumerate(pairs):
        prompt = prompts[condition][ident]
        assert prompt["user"] == prompts["B" if condition == "C" else "C"][ident]["user"]
        messages = {k: prompt[k] for k in ("system", "user")}
        digest = hashlib.sha256(json.dumps(messages, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        token = f"public-{order:03d}"
        runs.append({"run_token": token, "order": order, "condition": condition, "item_id": ident,
                     "model": model, "sample": 0, "prompt_sha256": digest,
                     "evidence_sha256": items[ident]["wire_sha256"]})
        requests.append({"run_token": token, **messages})
    assert len(runs) == 48 and len({r["item_id"] for r in runs}) == 24
    out.mkdir(parents=True, exist_ok=True)
    for name, records in (("schedule", runs), ("requests", requests)):
        with (out / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for rec in records:
                handle.write(json.dumps(rec, sort_keys=True) + "\n")
    metadata = {"state": "PUBLIC_TECHNICAL_NOT_EXECUTED", "model": model, "seed": seed,
                "scheduled_calls": 48, "distinct_evidence_views": 24,
                "fresh_context": True, "tools": False, "retrieval": False, "max_output_tokens": 1024}
    (out / "manifest.json").write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--model", required=True, help="exact provider model label, no request is sent")
    parser.add_argument("--seed", type=int, default=1017)
    args = parser.parse_args()
    public_schedule(args.out, args.model, args.seed)
