"""Neutral E1/E2 adapters. Reference FD snapshots never enter these adapters."""
from observe import OPEN, OVERFLOW, accessed


def e1(claims, registry):
    if claims["order"] != ["score", "policy", "planned_resolver", "resolver", "read", "result"]:
        raise ValueError("out-of-profile application event sequence")
    # Registry checks claimed bytes/IDs; never treat that as proof they were read.
    return {key: value["file"] for key, value in claims.items()
            if key not in {"order", "result"}
            and registry.get(value["file"], {}).get("sha256") == value["sha256"]}


def e2(epochs, registry):
    all_events = [event for batch in epochs for event in batch]
    if any(event["mask"] & OVERFLOW for event in all_events):
        return {}
    opens = {event["name"] for event in all_events if event["mask"] & OPEN}
    accesses = accessed(all_events)
    obs = {}

    def unique(files, role):
        candidates = {name for name in files if name in opens and name in registry
                      and registry[name]["role"].startswith(role)}
        return next(iter(candidates)) if len(candidates) == 1 else None

    for field, role in (("score", "score"), ("policy", "policy"), ("read", "r@")):
        if candidate := unique(accesses, role):
            obs[field] = candidate
    if "binding.json" not in accesses or "binding.json" not in opens:
        return obs
    if planned := unique(accessed(epochs[0]), "resolver-"):
        obs["planned_resolver"] = planned
    later = [event for batch in epochs[1:] for event in batch]
    later_candidates = accessed(later, "resolver-")
    if used := unique(later_candidates if later_candidates else accessed(epochs[0]), "resolver-"):
        obs["resolver"] = used
    return obs


FIELDS = {"score", "policy", "planned_resolver", "resolver", "read"}


def candidate(observed, registry, control):
    """Map evidence to the frozen Phase A profile, with an explicit BC extension."""
    history = control["history"]
    bounded = FIELDS <= set(observed)
    if not bounded:
        return {"state": "incomplete", "reason": "runtime_observation_missing",
                "wire": {"events": history, "history_closed": False, "dependencies_closed": False}}
    contents = {field: registry[observed[field]]["value"] for field in FIELDS}
    intended, approved = contents["planned_resolver"]["threshold"], contents["resolver"]["threshold"]
    used = contents["read"]["version"]
    intended_version = registry[intended]["value"]["version"]
    if (approved != observed["read"] or intended_version not in control["allowed_thresholds"]
            or used not in control["allowed_thresholds"]):
        return {"state": "contradiction", "reason": "runtime_binding_evidence_inconsistent", "wire": None}
    from scenarios import event
    scope = history + [
        event(8, "bind", "kj", version=contents["score"]["version"],
              policy=contents["policy"]["version"], root=intended_version),
        event(10, "read", "kj", version=used, parent=None),
        event(14, "adjudicate", "kj", version=contents["score"]["version"],
              policy=contents["policy"]["version"]),
    ]
    return {"state": "projected", "reason": "closed_under_scoped_collection_assumptions",
            "wire": {"events": scope, "history_closed": True, "dependencies_closed": True}}


def combine(first, second):
    conflicts = sorted(key for key in first.keys() & second.keys() if first[key] != second[key])
    return ({} if conflicts else {**first, **second}), conflicts
