from __future__ import annotations

from thesis_os.models import Evidence, Thesis, utc_now


def build_sample_thesis(evidence: list[Evidence]) -> Thesis:
    evidence_ids = [item.id for item in evidence]
    return Thesis(
        id="THESIS-SAMPLE-AI-INFRA-001",
        entity="AI Infrastructure Basket",
        status="active",
        claim="AI infrastructure demand remains investable only if evidence confirms both demand persistence and market under-reaction.",
        assumptions=[
            "Demand indicators are not merely inventory build.",
            "Consensus has not fully absorbed the evidence.",
            "The relevant value-chain companies can convert demand into earnings.",
        ],
        evidence_ids=evidence_ids,
        risks=[
            "The thesis can be right but already priced in.",
            "Supplier benefits may be diluted by ASP pressure or capacity constraints.",
        ],
        invalidation=[
            "Two consecutive evidence updates weaken demand persistence.",
            "Price and consensus already reflect the positive scenario.",
        ],
        updated_at=utc_now(),
        tags=["sample", "ai-infra", "thesis-os"],
        thesis_type="cycle_rerating",
        native_horizon="6m",
        measurement_note="Short-term price feedback checks timing. Thesis quality should be reviewed over 3m/6m/1y evidence and outcome windows.",
    )


def thesis_markdown(thesis: Thesis) -> str:
    return "\n".join(
        [
            f"**Entity:** {thesis.entity}",
            f"**Status:** {thesis.status}",
            f"**Type:** {thesis.thesis_type}",
            f"**Native horizon:** {thesis.native_horizon}",
            "",
            "## Claim",
            thesis.claim,
            "",
            "## Assumptions",
            *[f"- {item}" for item in thesis.assumptions],
            "",
            "## Evidence",
            *[f"- `{item}`" for item in thesis.evidence_ids],
            "",
            "## Risks",
            *[f"- {item}" for item in thesis.risks],
            "",
            "## Invalidation",
            *[f"- {item}" for item in thesis.invalidation],
            "",
            "## Measurement Note",
            thesis.measurement_note or "Evaluate this thesis on its native horizon. Short-term return feedback is timing evidence, not final thesis proof.",
        ]
    )
