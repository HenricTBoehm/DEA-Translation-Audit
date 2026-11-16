"""Single isolated evaluator. Evaluation steps and E1 claims share a process."""
import json
import hashlib
from pathlib import Path
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(path, payload):
    return {"file": path.name, "sha256": digest(payload)}


def load(path):
    payload = path.read_bytes()
    if not path.name.endswith(f"-{digest(payload)}.json"):
        raise ValueError("content-address mismatch")
    return json.loads(payload), record(path, payload)


def checkpoint(name):
    print(name, file=sys.stderr, flush=True)
    if sys.stdin.readline() != "continue\n":
        raise RuntimeError("missing controller handshake")


def main(root, config):
    score, score_claim = load(root / config["score"])
    policy, policy_claim = load(root / config["policy"])
    if policy["operation"] != "ge" or score["score"] not in range(4):
        raise ValueError("outside the bounded procedure")

    def resolve():
        pointer = json.loads((root / "binding.json").read_bytes())
        resolver, claim = load(root / pointer["resolver"])
        return resolver, claim

    planned, planned_claim = resolve()
    checkpoint("planned")
    selected, resolver_claim = resolve() if config["reread"] else (planned, planned_claim)
    path = root / selected["threshold"]
    with path.open("rb", buffering=0) as source:
        checkpoint("threshold_open")
        payload = source.read()
        checkpoint("consumed")
    read_claim = record(path, payload)
    if not path.name.endswith(f'-{read_claim["sha256"]}.json'):
        raise ValueError("threshold digest mismatch")
    threshold = json.loads(payload)["threshold"]
    if threshold not in (0, 1):
        raise ValueError("outside the threshold alphabet")
    result = {"accept": score["score"] >= threshold}
    claims = {"score": score_claim, "policy": policy_claim, "planned_resolver": planned_claim,
              "resolver": resolver_claim, "read": read_claim, "result": result,
              "order": ["score", "policy", "planned_resolver", "resolver", "read", "result"]}
    if config["omit"]:
        del claims["read"]
    if config["false_claim"]:
        claims.update(config["false_claim"])
    print(json.dumps(result), flush=True)
    print(json.dumps(claims), file=sys.stderr, flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]), json.loads(sys.argv[2]))
