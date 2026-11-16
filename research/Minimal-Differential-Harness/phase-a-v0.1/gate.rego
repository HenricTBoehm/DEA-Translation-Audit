package phasea

import rego.v1

# The configured policy evaluates SR-1 over neutral facts using native Rego.
# The producer has supplied neither candidate witnesses nor verdicts.
default decision := {"verdict": "UNDETERMINED", "reason": "read_coverage_open", "witness": null}

decision := {"verdict": "MODEL_INVALID", "reason": input.provenance.event_reason, "witness": null} if {
	input.provenance.event_check == "contradiction"
} else := {"verdict": "UNDETERMINED", "reason": input.provenance.event_reason, "witness": null} if {
	input.provenance.event_check != "settled"
} else := {"verdict": "CONFLICT", "reason": "material_path", "witness": sort(paths)[0]} if {
	count(paths) > 0
} else := {"verdict": "NO_CONFLICT_ESTABLISHED", "reason": "coverage_conditional", "witness": null} if {
	input.provenance.scope.history
	input.provenance.scope.reads
}

paths contains witness if {
	p := input.provenance
	p.score_right != null
	some read in p.reads
	source := p.versions[read.version].fields.threshold.origin
	source.principal == p.producer.principal
	witness := [
		p.producer.principal, p.score_right, p.producer.event, read.version,
		"surviving", source.grant, source.event, p.binding.id, read.id,
	]
}

paths contains witness if {
	p := input.provenance
	p.score_right != null
	some read in p.reads
	some right in p.rights
	right.principal == p.producer.principal
	right.channel == "threshold"
	p.heads[right.target] == read.version
	not endswith(read.version, "@2")
	witness := [
		p.producer.principal, p.score_right, p.producer.event, read.version,
		"potential", right.event, p.binding.id, read.id,
	]
}
