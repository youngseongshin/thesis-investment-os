from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def terminal_frame(lines: list[str], cursor: bool = False) -> Image.Image:
    width, height = 1120, 640
    img = Image.new("RGB", (width, height), "#0f172a")
    draw = ImageDraw.Draw(img)
    font = load_font(22)
    small = load_font(16)

    draw.rounded_rectangle((20, 20, width - 20, height - 20), radius=22, fill="#111827", outline="#334155", width=2)
    for i, color in enumerate(["#ef4444", "#f59e0b", "#22c55e"]):
        draw.ellipse((48 + i * 28, 48, 62 + i * 28, 62), fill=color)
    draw.text((142, 45), "Thesis OS quick demo", fill="#cbd5e1", font=small)

    y = 96
    for line in lines:
        color = "#e5e7eb"
        if line.startswith("$"):
            color = "#5eead4"
        elif line.startswith("{") or line.startswith("}") or line.strip().startswith('"'):
            color = "#bfdbfe"
        elif line.startswith("✓"):
            color = "#86efac"
        elif line.startswith("#"):
            color = "#94a3b8"
        draw.text((54, y), line, fill=color, font=font)
        y += 34

    if cursor:
        draw.rectangle((54, y + 4, 68, y + 28), fill="#5eead4")
    return img


def render_terminal_demo() -> Path:
    frames_text = [
        [
            "$ thesis-os arki init --workspace ./workspace",
            "{",
            '  "workspace": "./workspace",',
            '  "initialized": true',
            "}",
            "",
            "# Arki creates the local operating surface.",
        ],
        [
            "$ thesis-os alpha sample-collect --workspace ./workspace",
            "{",
            '  "workspace": "./workspace",',
            '  "evidence_count": 2',
            "}",
            "",
            "# Alpha writes evidence into DB + vault.",
        ],
        [
            "$ thesis-os lattice build-thesis --workspace ./workspace",
            "{",
            '  "thesis_id": "THESIS-SAMPLE-AI-INFRA-001",',
            '  "path": "vault/theses/THESIS-SAMPLE-AI-INFRA-001.md"',
            "}",
            "",
            "# Lattice converts evidence into an explicit thesis.",
        ],
        [
            "$ thesis-os lattice predict --workspace ./workspace \\",
            '  --prediction "The basket should outperform" \\',
            "  --direction relative_outperform --horizon 1m",
            "{",
            '  "id": "PRED-SAMPLE",',
            '  "direction": "relative_outperform"',
            "}",
            "",
            "# Prediction is registered before the outcome.",
        ],
        [
            "$ thesis-os arki health --workspace ./workspace",
            "{",
            '  "ok": true,',
            '  "evidence_notes": 2,',
            '  "thesis_notes": 1,',
            '  "prediction_ledger": true',
            "}",
            "",
            "✓ thesis loop is auditable and reproducible",
        ],
    ]
    frames = [terminal_frame(lines, cursor=i == len(frames_text) - 1) for i, lines in enumerate(frames_text)]
    path = ASSETS / "terminal-demo.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=1450, loop=0, optimize=True)
    return path


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    path = render_terminal_demo()
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

