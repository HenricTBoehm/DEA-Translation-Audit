package phasea_p01_probe

import rego.v1

# Diagnostic reconfiguration to a different target, outside the primary cells.
default verdict := "UNDETERMINED"

verdict := "MODEL_INVALID" if {
	input.provenance.event_check == "contradiction"
} else := "CONFLICT" if {
	p := input.provenance
	p.event_check == "settled"
	p.producer.principal == p.reviewer.principal
} else := "CONFLICT" if {
	p := input.provenance
	p.event_check == "settled"
	some read in p.reads
	p.versions[read.version].fields.threshold.origin.principal == p.producer.principal
} else := "NO_CONFLICT_ESTABLISHED" if {
	p := input.provenance
	p.event_check == "settled"
	p.scope.history
	p.scope.reads
}
