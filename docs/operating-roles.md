# Operating Roles

Thesis OS separates ownership before it adds agents. A role exists to preserve
a decision boundary, not to create another voice in a group chat.

## Core Public Roles

The executable public core uses three roles.

### Alpha: Evidence

Alpha collects, normalizes, verifies, and ranks evidence. It owns source
freshness, structured market data, screener candidates, and research packets.
It does not own final portfolio judgment.

### Lattice / 격자: Judgment

Lattice maintains public-market theses, counterarguments, action gates,
predictions, and outcome interpretation. It cannot silently turn a screener or
secondary source into a capital action.

### Arki / 아키: Control Plane

Arki owns schemas, workflow contracts, adapters, permissions, canonical paths,
runtime health, migrations, retention, and public/private boundaries. It does
not make investment calls.

## Deployment Extension Roles

Larger deployments can add roles without changing the object model.

### Gwajang / 과장: VC Desk

Gwajang owns private-company theses, diligence packets, IC materials,
portfolio-company monitoring, and sector intelligence. Confidentiality and
evidence provenance take priority over cross-domain reuse.

### Claw / 클로: Personal Context

Claw owns reflection, preferences, commitments, and personal context. It may
help the user notice patterns, but it cannot alter investment theses, system
policy, or external commitments without the owning role and human approval.

## Optional Worker Roles

Red-team, specialist, compiler, and source-verification workers should be
bounded task roles. They do not need persistent identities or standing chat
channels. Their output returns to the owning role through a typed contract.

## Ownership Matrix

| Artifact or decision | Producer | Decision owner | Control owner |
|---|---|---|---|
| source event, market snapshot, screener candidate | Alpha | Lattice when promoted | Arki |
| public-market thesis and action gate | Lattice | human investor | Arki |
| VC thesis and IC recommendation | Gwajang | human investment committee | Arki |
| reflection and commitment memory | Claw | user | Arki |
| schema, workflow, permission, retention policy | Arki | human system owner | Arki |

`producer`, `data_owner`, `decision_owner`, `delivery_target`, and
`control_owner` should be separate fields. A historical nickname or agent ID
must not carry all five meanings.

## Handoff Contract

Every cross-role handoff should state:

- the decision being supported;
- bounded input references and freshness;
- facts, assumptions, and unresolved gaps;
- requested output and owner;
- prohibited effects;
- completion and escalation conditions.

This keeps multi-agent work collaborative without requiring agents to remain in
an expensive, always-on conversation.
