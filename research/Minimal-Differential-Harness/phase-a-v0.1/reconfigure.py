"""Optional diagnostic: configure native predicates for D1's scoped target."""
import json
import sys

from adapters import opa_query, verified_opa
from d1 import decide
from provenance import export
from run import REFERENCE, project

if __name__ == "__main__":
    opa, _ = verified_opa(sys.argv[1])
    cases = json.loads((REFERENCE / "PUBLIC_CASES.json").read_text())
    for case in cases:
        facts = export(project(case["evidence"]))
        observed = opa_query(opa, "p01_probe.rego", '{"verdict": data.phasea_p01_probe.verdict}', facts)["verdict"]
        assert observed == decide(facts)["verdict"], case["label"]
    print(f"PASS: configured Rego D1 diagnostic verdict parity on {len(cases)} public cases")
