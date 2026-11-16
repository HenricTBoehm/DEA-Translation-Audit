"""Six paths through fixed projection and three separately callable deciders."""
import hashlib
import json
from pathlib import Path
import subprocess

import d0
import d1
from provenance import encode
from raw import reconstruct

HERE = Path(__file__).resolve().parent
OPA_SHA256 = "35e3b352e715e80624ead6c89930d8585f6f7d94cdc409eb2a9fe36620dcccba"


def verified_opa(path):
    path = Path(path).resolve()
    with path.open("rb") as binary:
        if hashlib.file_digest(binary, "sha256").hexdigest() != OPA_SHA256:
            raise ValueError("unexpected OPA executable digest")
    descriptor = subprocess.run([path, "version"], capture_output=True, check=True, text=True,
                                timeout=5).stdout
    if not {"Version: 1.22.4", "Platform: linux/amd64", "Rego Version: v1"} <= set(descriptor.splitlines()):
        raise ValueError("unexpected OPA executable profile")
    return path, descriptor


def decide(arm, layer, wire_bytes, derived_bytes=None, opa=None):
    if layer == "raw":
        if derived_bytes is not None:
            raise ValueError("raw adapter cannot receive derived evidence")
        facts = reconstruct(wire_bytes)
    elif layer == "derived":
        submitted = json.loads(derived_bytes)
        if hashlib.sha256(wire_bytes).hexdigest() != submitted["wire_sha256"]:
            raise ValueError("provenance belongs to a different wire")
        facts = submitted["provenance"]
    else:
        raise ValueError("unknown layer")

    if arm == "D0":
        return d0.decide(facts)
    if arm == "D1":
        return d1.decide(facts)
    if arm != "OPA":
        raise ValueError("unknown arm")
    if opa is None:
        return {"status": "NOT EXECUTED", "reason": "no verified official binary"}
    return opa_query(opa, "gate.rego", "data.phasea.decision", facts)


def opa_query(opa, module, query, facts):
    result = subprocess.run(
        [opa, "eval", "--stdin-input", "--strict", "--strict-builtin-errors", "--fail",
         "--format", "raw", "--data", HERE / module, query],
        input=encode({"provenance": facts}), capture_output=True, check=True, timeout=5,
    )
    return json.loads(result.stdout)
