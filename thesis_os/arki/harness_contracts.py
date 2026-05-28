from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from thesis_os.arki.vault_writer import VaultWriter
from thesis_os.models import utc_now


REQUIRED_CONTRACT_FIELDS = {
    "id",
    "owner_agent",
    "purpose",
    "trigger",
    "command",
    "inputs",
    "outputs",
    "delivery",
}

VALID_OWNERS = {"alpha", "lattice", "arki"}


def validate_harness_contracts(input_json: str | Path, workspace: str | Path | None = None) -> dict[str, object]:
    path = Path(input_json)
    data = json.loads(path.read_text(encoding="utf-8"))
    contracts = data.get("contracts", [])
    if not isinstance(contracts, list):
        raise ValueError("harness contract manifest must contain a `contracts` list")

    findings: list[dict[str, str]] = []
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(contracts):
        subject = f"contracts[{index}]"
        if not isinstance(raw, dict):
            findings.append({"severity": "error", "subject": subject, "detail": "contract is not an object"})
            continue
        normalized.append(raw)
        missing = sorted(REQUIRED_CONTRACT_FIELDS - set(raw))
        if missing:
            findings.append({"severity": "error", "subject": str(raw.get("id", subject)), "detail": f"missing fields: {', '.join(missing)}"})
        owner = str(raw.get("owner_agent", "")).strip()
        if owner not in VALID_OWNERS:
            findings.append({"severity": "error", "subject": str(raw.get("id", subject)), "detail": f"invalid owner_agent: {owner}"})
        for list_field in ("inputs", "outputs", "delivery"):
            if list_field in raw and not isinstance(raw[list_field], list):
                findings.append({"severity": "error", "subject": str(raw.get("id", subject)), "detail": f"{list_field} must be a list"})
        if "model_policy" in raw and not isinstance(raw["model_policy"], dict):
            findings.append({"severity": "warning", "subject": str(raw.get("id", subject)), "detail": "model_policy should be an object"})

    result = {
        "input": str(path),
        "contract_count": len(normalized),
        "error_count": sum(1 for item in findings if item["severity"] == "error"),
        "warning_count": sum(1 for item in findings if item["severity"] == "warning"),
        "findings": findings,
    }

    if workspace is not None:
        vault = VaultWriter(Path(workspace) / "vault")
        vault.ensure_layout()
        note_path = vault.write_note(
            "jobs/harness-contract-validation.md",
            title="Harness Contract Validation",
            body=harness_contracts_markdown(normalized, result),
            frontmatter={
                "generated_at": utc_now(),
                "type": "harness_contract_validation",
                "contract_count": len(normalized),
                "error_count": result["error_count"],
                "warning_count": result["warning_count"],
            },
        )
        result["path"] = str(note_path)
    return result


def harness_contracts_markdown(contracts: list[dict[str, Any]], result: dict[str, object]) -> str:
    lines = [
        "Harness contracts define how recurring or event-driven jobs execute, what they read, what they write, and how outputs are delivered.",
        "",
        "## Summary",
        f"- Contracts: {result['contract_count']}",
        f"- Errors: {result['error_count']}",
        f"- Warnings: {result['warning_count']}",
        "",
        "## Contracts",
        "| ID | Owner | Trigger | Outputs | Delivery |",
        "|---|---|---|---|---|",
    ]
    for item in contracts:
        outputs = ", ".join(str(value) for value in item.get("outputs", []))
        delivery = ", ".join(str(value) for value in item.get("delivery", []))
        lines.append(f"| `{item.get('id', '')}` | {item.get('owner_agent', '')} | {item.get('trigger', '')} | {outputs} | {delivery} |")
    findings = result.get("findings", [])
    if findings:
        lines.extend(["", "## Findings", "| Severity | Subject | Detail |", "|---|---|---|"])
        for finding in findings:
            if isinstance(finding, dict):
                lines.append(f"| {finding.get('severity', '')} | `{finding.get('subject', '')}` | {finding.get('detail', '')} |")
    lines.extend(
        [
            "",
            "## Rule",
            "A harness contract is valid only when ownership, input, output, delivery, and failure behavior are explicit.",
        ]
    )
    return "\n".join(lines)
