# Memory Management

Thesis OS depends on memory, but memory is useful only when it is curated.

The goal is not to remember everything. The goal is to preserve the objects that improve future judgment:

- evidence
- thesis changes
- decisions
- predictions
- feedback
- process lessons
- source and collector health

## Memory Layers

| Layer | Purpose | Typical Owner |
|---|---|---|
| Working memory | Short-lived context for the current task or run | Any agent |
| Local database | Structured, queryable facts and events | Alpha / Arki |
| Vault canonical notes | Human-readable durable research objects | Owning domain role |
| Compiled LLM Wiki | Compact retrieval projection over canonical notes | Arki |
| Prediction and feedback memory | Pre-registered judgments and evaluated outcomes | Lattice |
| Private-company memory | Diligence, IC, and monitoring history inside its confidentiality boundary | Gwajang extension |
| Personal context memory | Source-linked reflections, preferences, and commitments | Claw extension |
| System memory | Schemas, policies, migrations, health, recurring jobs | Arki |

## Memory Lifecycle

```text
capture
  -> normalize
  -> classify
  -> promote or discard
  -> link to canonical object
  -> summarize for retrieval
  -> record retrieval and decision influence
  -> evaluate outcome
  -> replay, revise, or retire
```

## 1. Capture

Agents capture raw or semi-raw inputs from data adapters, source collectors, screeners, and user requests.

Capture should preserve:

- timestamp
- source type
- source confidence
- entity or theme
- owning agent
- collection status

Capture should avoid storing private raw data in public artifacts.

## 2. Normalize

Raw inputs become structured objects:

- evidence records
- market snapshots
- screener candidates
- intraday alerts
- thesis update candidates
- action records
- prediction records
- feedback reports

Normalization separates facts from interpretation.

## 3. Classify

Each memory item should be classified:

| Class | Meaning |
|---|---|
| evidence | A source-grounded fact or observation |
| thesis | A living investment argument |
| action | A judgment with possible portfolio implication |
| prediction | A measurable statement before outcome |
| feedback | Outcome review after a horizon matures |
| system | Schema, job, policy, or health memory |
| archive | Historical but not retrieval-priority |
| discard | Noise, duplicate, or unsupported item |

## 4. Promote Or Discard

Not every captured item deserves long-term memory.

Promote when:

- it changes a thesis
- it changes a decision
- it affects risk, timing, or invalidation
- it explains a feedback result
- it documents a recurring failure
- it improves future retrieval

Discard or quarantine when:

- it is duplicate noise
- it is raw social chatter with no evidence grade
- it is stale and superseded
- it cannot be linked to an entity, thesis, or process
- it would expose private data

## 5. Link To Canonical Objects

Durable memory should link to at least one canonical object:

- evidence ID
- thesis ID
- candidate ID
- action ID
- prediction ID
- feedback ID
- workflow and run ID
- source pointer or digest

Unlinked notes are hard for agents to retrieve and easy to forget.

## 6. Summarize For Retrieval

The LLM wiki should not duplicate every note. It should summarize current state and point to canonical objects.

Good retrieval memory includes:

- current thesis status
- latest evidence date
- open action queue
- invalidation conditions
- recent feedback lessons
- stale or missing data flags

Bad retrieval memory includes:

- raw dumps
- ungraded social chatter
- duplicate folders
- obsolete summaries without timestamps
- conclusions with no evidence link

Compaction summaries and wiki pages are projections. They require source
pointers and must not outrank the canonical source or an immutable prediction.

## 7. Evaluate And Update

Feedback memory is what makes Thesis OS compound.

After a horizon matures, Lattice should evaluate:

- did the prediction work?
- did the screener candidate outperform?
- did portfolio inclusion make sense?
- was the error data, interpretation, timing, crowding, or execution?
- should the thesis, screener rule, or process change?

Retrieval itself should also be evaluated:

- which memory ID or source changed the decision?
- was the retrieved item accepted, corrected, or rejected?
- did the influence prevent an error or create one?
- should the item be replayed, revised, superseded, or retired?

Silence is not positive feedback. A mature deployment links explicit user or
decision outcomes to memory promotion.

## Agent Responsibilities

### Alpha

Alpha owns evidence memory:

- market snapshots
- collector status
- screener candidates
- qualitative signal summaries
- intraday alerts
- source freshness

Alpha should not rewrite Lattice's decisions.

### Lattice

Lattice owns judgment memory:

- thesis cards
- decision cards
- action queue
- prediction ledger
- roundtable notes
- feedback interpretations
- process lessons from judgment outcomes

Lattice should not change old predictions after outcomes are known.

### Gwajang

Gwajang owns private-company thesis, diligence, IC, and monitoring memory. It
keeps confidential source material inside the owning boundary and promotes only
the minimum reusable sector knowledge.

### Claw

Claw owns personal context, reflection, preference, and commitment memory. It
preserves corrections and source links, and cannot write investment or system
policy memory.

### Arki

Arki owns system memory:

- schemas
- vault layout
- SSOT policies
- wiki index
- recurring job manifest
- health reports
- migration notes
- public/private boundary checks

Arki should not make investment calls.

## Retention Policy

| Memory Type | Default Treatment |
|---|---|
| Canonical thesis, action, prediction, feedback | Keep |
| Local DB structured records | Keep unless superseded by explicit migration |
| Wiki index | Regenerate |
| Temporary raw collector files | Delete after synthesis or archive privately |
| Duplicate or superseded generated views | Regenerate, merge, or discard after canonical-reference check |
| Failed collector logs | Keep compact failure record |
| Private raw messages or credentials | Never publish |

## Minimum Memory Contract

Every durable memory object should answer:

1. What is this?
2. Who produced it?
3. What source or evidence supports it?
4. What canonical object does it update?
5. How fresh is it?
6. What should an agent do with it later?
7. Should it be kept, summarized, archived, or discarded?
8. Which retrieval, decision, run, or outcome can show that it was useful?
