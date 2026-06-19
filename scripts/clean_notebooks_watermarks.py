"""Nettoie les watermarks LLM et conflits Git dans tous les notebooks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIRS = [
    ROOT / "notebooks",
    ROOT / "AquaSense_S4_Colab" / "notebooks",
    ROOT / "result",
]

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\u2600-\u27BF"
    "\uFE0F"
    "]+",
    flags=re.UNICODE,
)

REPLACEMENTS = [
    ("AI Context Note", "Contexte methodologique"),
    ("ai context note", "contexte methodologique"),
    ("proxy structurel", "jeu de reference"),
    ("—", " : "),
    ("–", "-"),
    ("·", " - "),
    ("→", " -> "),
    ("⚠️", "Note :"),
    ("⚠", "Note :"),
    ("✅", "Oui"),
    ("❌", "Non"),
]


def resolve_git_conflicts(text: str) -> str:
    pattern = re.compile(
        r"<<<<<<< HEAD\n.*?\n=======\n(.*?)\n>>>>>>> [0-9a-f]+\n",
        re.DOTALL,
    )
    return pattern.sub(lambda m: m.group(1), text)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return EMOJI_RE.sub("", text)


def clean_source_line(line: str) -> str:
    leading = len(line) - len(line.lstrip(" "))
    prefix = line[:leading]
    rest = line[leading:]
    return prefix + clean_text(rest)


def clean_outputs(outputs: list) -> None:
    for out in outputs:
        if out.get("output_type") == "stream":
            if isinstance(out.get("text"), list):
                out["text"] = [clean_text(t) for t in out["text"]]
            elif isinstance(out.get("text"), str):
                out["text"] = clean_text(out["text"])
        elif out.get("output_type") in ("execute_result", "display_data"):
            data = out.get("data", {})
            for key in ("text/plain", "text/html", "text/markdown"):
                if key in data:
                    if isinstance(data[key], list):
                        data[key] = [clean_text(t) for t in data[key]]
                    else:
                        data[key] = clean_text(data[key])
        elif out.get("output_type") == "error":
            for field in ("evalue", "traceback"):
                if field in out:
                    if isinstance(out[field], list):
                        out[field] = [clean_text(t) for t in out[field]]
                    else:
                        out[field] = clean_text(out[field])


def clean_cell_sources(nb: dict) -> None:
    for cell in nb.get("cells", []):
        src = cell.get("source", [])
        if isinstance(src, str):
            lines = [src]
        else:
            lines = src
        cleaned = [clean_source_line(ln) for ln in lines]
        cell["source"] = cleaned
        if cell.get("cell_type") == "code" and cell.get("outputs"):
            clean_outputs(cell["outputs"])


def load_notebook(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    raw = resolve_git_conflicts(raw)
    return json.loads(raw)


def save_notebook(path: Path, nb: dict) -> None:
    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    count = 0
    for folder in NOTEBOOK_DIRS:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.ipynb")):
            if path.name == "Untitled5.ipynb":
                continue
            try:
                nb = load_notebook(path)
                clean_cell_sources(nb)
                save_notebook(path, nb)
                count += 1
                print(f"OK  {path.relative_to(ROOT)}")
            except Exception as exc:
                print(f"ERR {path.relative_to(ROOT)}: {exc}")
    print(f"\n{count} notebook(s) nettoye(s).")


if __name__ == "__main__":
    main()
