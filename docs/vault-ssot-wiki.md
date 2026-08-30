# Vault, SSOT, And Compiled LLM Wiki

The vault is durable human-readable memory. The LLM Wiki is a compiled
retrieval view over canonical objects.

```text
structured records + owner-domain notes
  -> policy and integrity checks
  -> aliases, links, summaries, and freshness
  -> compiled wiki
  -> retrieval event
  -> decision citation and outcome
```

## Canonical Objects

- source and evidence records;
- screener and research candidates;
- living theses and counter-theses;
- actions, explicit non-actions, and predictions;
- feedback and outcome reviews;
- workflow, run, effect, and system records where the deployment supports
  them.

The structured store is canonical for IDs, metrics, state, and joins. The
owner-domain vault note is canonical for durable narrative. Generated wiki,
dashboard, and digest files are projections.

## Why SSOT Matters

Without a single-source policy, agents create duplicate folders, conflicting
summaries, and stale parallel memories. Each document type therefore needs:

- a canonical owner and path;
- a stable identity and aliases;
- source and freshness metadata;
- supersession and retention rules;
- a validator before write or publication.

## Policy-Backed Writes

```text
document type + owner + context
  -> vault policy resolver
  -> canonical path
  -> ownership and frontmatter checks
  -> write
  -> wiki compile
```

Generators should not hardcode new folder taxonomies. A generated page should
be repaired at its source serializer or resolver, not edited as an independent
truth.

## Compilation Rules

A useful wiki page contains:

- stable entity and thesis aliases;
- current status and native horizon;
- latest evidence date and confidence;
- supporting and disconfirming claims;
- open fact gaps and action queue;
- invalidation conditions;
- source links and superseded-object pointers;
- recent outcome and process lessons.

It should not contain raw dumps, unsupported conclusions, duplicate full-text
copies, or a summary without provenance.

## Quality And Influence

Search success, ranking quality, and latency test retrieval mechanics. They do
not show that the wiki improved a decision.

A mature deployment also records:

- retrieved memory or document IDs;
- decision or artifact influenced;
- accepted, corrected, or rejected status;
- later outcome and lesson;
- replay, revision, or retirement decision.

## Retention

Canonical theses, actions, predictions, and feedback remain durable. Wiki pages
are regenerated. Raw capture, cache, intermediate versions, and duplicate
renderings use bounded retention after their canonical references and required
audit hashes are preserved.

Filename similarity alone is not enough to delete a version. The system must
know that files belong to the same deliverable lineage and that a valid final
artifact exists.

## Public Example

See [sample_vault_policy.yaml](../examples/sample_vault_policy.yaml) and run:

```bash
python -m thesis_os arki build-wiki-index --workspace ./workspace
```

Private deployments may add embedding search or knowledge graphs, but markdown
provenance and canonical source pointers remain intact.
