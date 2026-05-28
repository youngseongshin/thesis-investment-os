from __future__ import annotations

from pathlib import Path
from typing import Any


class VaultWriter:
    """Small markdown vault writer with YAML-like frontmatter."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def ensure_layout(self) -> None:
        for name in ("evidence", "theses", "decisions", "feedback", "jobs", "screeners", "wiki", "ssot"):
            (self.root / name).mkdir(parents=True, exist_ok=True)

    def write_note(self, relative_path: str | Path, title: str, body: str, frontmatter: dict[str, Any] | None = None) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        fm = frontmatter or {}
        lines = ["---"]
        for key, value in fm.items():
            lines.append(f"{key}: {self._format_frontmatter_value(value)}")
        lines.extend(["---", "", f"# {title}", "", body.rstrip(), ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _format_frontmatter_value(value: Any) -> str:
        if isinstance(value, list):
            return "[" + ", ".join(str(item) for item in value) + "]"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
