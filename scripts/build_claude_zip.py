"""Zip minimal pour Claude : markdown + images referencees + prompt."""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
OUT = REPORTS / "claude_zip.zip"

MD = REPORTS / "AquaSense_AI_Report.md"
PROMPT = REPORTS / "PROMPT_CLAUDE_RAPPORT.md"

SPRINT_FIGS = [
    "sprint_03_confusion_matrices.png",
    "sprint_03_feature_importance.png",
    "sprint_04_training_history.png",
    "sprint_04_confusion_matrix.png",
]


def images_in_md(text: str) -> set[str]:
    paths = set()
    for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", text):
        p = m.group(1).replace("%20", " ")
        paths.add(p)
    return paths


def main() -> None:
    md_text = MD.read_text(encoding="utf-8")
    refs = images_in_md(md_text)

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(MD, "AquaSense_AI_Report.md")
        if PROMPT.exists():
            zf.write(PROMPT, "PROMPT_CLAUDE_RAPPORT.md")

        for name in SPRINT_FIGS:
            p = REPORTS / name
            if p.exists():
                zf.write(p, f"images/{name}")

        for ref in sorted(refs):
            if ref.startswith("image/"):
                src = REPORTS / ref
                if src.exists():
                    zf.write(src, f"images/{Path(ref).name}")

        zf.writestr(
            "LISEZMOI.txt",
            "Contenu : rapport Markdown + images + PROMPT_CLAUDE_RAPPORT.md\n"
            "Ouvrir le prompt en premier, puis joindre ce zip a Claude.\n",
        )

    print(f"OK  {OUT} ({OUT.stat().st_size / 1024 / 1024:.2f} Mo)")


if __name__ == "__main__":
    main()
