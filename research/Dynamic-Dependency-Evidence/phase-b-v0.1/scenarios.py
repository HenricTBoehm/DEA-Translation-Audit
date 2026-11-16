"""Controlled public fixture administration. This module is not a decider."""
from hashlib import sha256
import json

POLICY = "sum-thresholds@1"
SCENARIOS = {
    "B01": ("none", "r@0", "r@0", False, False, False),
    "B02": ("both", "r@1", "r@1", True, False, False),
    "B03": ("write", "r@0", "r@0", False, False, False),
    "B04": ("select", "r@1", "r@1", True, False, False),
    "B05": ("revoke", "r@1", "r@1", False, False, False),
    "B06": ("reset", "r@2", "r@2", False, False, False),
    "B07": ("both", "r@1", "r@1", True, True, False),
    "B08": ("both", "r@1", "r@1", True, False, True),
    "B09": ("layout", "r@1", "r@1", False, False, False),
    "B10": ("both", "r@0", "r@1", True, False, False),
}


def pack(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def event(rank, kind, key, **values):
    return {"id": rank, "rank": rank, "time": rank, "kind": kind, "key": key, **values}


def fixture(directory, name):
    mode, planned, used, selectable, omit, false = SCENARIOS[name]
    history = [event(0, "grant", "ki", subject="ka", target="x", channel="score")]
    registry, by_role = {}, {}

    def publish(role, record):
        data = pack(record)
        checksum = sha256(data).hexdigest()
        filename = f"{role}-{checksum}.json"
        path = directory / filename
        with path.open("xb") as handle:
            handle.write(data)
        path.chmod(0o444)
        by_role[role] = filename
        registry[filename] = {"sha256": checksum, "value": record, "role": role}

    score = 1 if false else 0
    publish("score", {"version": "x@1", "score": score})
    publish("policy", {"version": POLICY, "operation": "ge"})
    publish("r@0", {"version": "r@0", "threshold": 0, "layout": 0})
    if mode != "none":
        key = "kq" if mode == "select" else "ka"
        channel = "layout" if mode == "layout" else "threshold"
        history.extend([event(1, "grant", "ki", subject=key, target="r", channel=channel),
                        event(2, "modify", key, base="r@0", version="r@1", channel=channel, value=1)])
        publish("r@1", {"version": "r@1", "threshold": int(channel == "threshold"),
                        "layout": int(channel == "layout")})
    history.append(event(4, "produce", "ka", version="x@1", value=score))
    if mode in ("revoke", "reset"):
        history.append(event(5, "revoke", "ki", subject="ka"))
    if mode == "reset":
        history.append(event(6, "reset", "ki", base="r@1", version="r@2", channel="threshold"))
        publish("r@2", {"version": "r@2", "threshold": 0, "layout": 0})
    history.append(event(7, "seal", "kj", version="x@1", policy=POLICY))

    roots = [role for role in by_role if role.startswith("r@")]
    allowed = roots if selectable else [planned]
    for index, version in enumerate(roots):
        publish(f"resolver-{version}", {"version": f"resolver@{index}", "threshold": by_role[version]})

    def pointer(version):
        return pack({"resolver": by_role[f"resolver-{version}"]})

    (directory / "binding.json").write_bytes(pointer(planned))
    false_claim = {}
    if false:
        for claim, role in (("read", "r@0"), ("resolver", "resolver-r@0"),
                            ("planned_resolver", "resolver-r@0")):
            filename = by_role[role]
            false_claim[claim] = {"file": filename, "sha256": registry[filename]["sha256"]}
    runtime = {"score": by_role["score"], "policy": by_role["policy"],
               "reread": planned != used, "omit": omit, "false_claim": false_claim}
    control = {"history": history, "allowed_thresholds": allowed,
               "selector_owners": ["p"] if selectable else ["q"],
               "policy_owners": ["issuer"], "procedural_authority": "kj"}
    plan = {"binding_before": planned, "intended_read": used, "fault": (
            "omit_read" if omit else "false_trace" if false else "binding_race" if planned != used else None)}
    return registry, runtime, control, plan, pointer(used) if planned != used else None
