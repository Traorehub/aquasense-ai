"""Audit notebook execution status across the project."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOTS = [
    ROOT / "notebooks",
]
COLAB_ARCHIVE_ROOTS = [
    ROOT / "AquaSense_S4_Colab" / "notebooks",
    ROOT / "result",
]


def audit(nb_path: Path) -> dict:
    nb = json.loads(nb_path.read_text(encoding="utf-8"))
    code_cells = [c for c in nb["cells"] if c["cell_type"] == "code"]
    n_code = len(code_cells)
    n_exec = sum(1 for c in code_cells if c.get("execution_count") is not None)
    n_null = n_code - n_exec
    errors: list[tuple[int, str, str]] = []
    for i, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                errors.append((i, out.get("ename", "?"), (out.get("evalue") or "")[:150]))
    has_outputs = sum(1 for c in code_cells if c.get("outputs"))
    return {
        "n_code": n_code,
        "n_exec": n_exec,
        "n_null": n_null,
        "errors": errors,
        "has_outputs": has_outputs,
    }


def status(row: dict) -> str:
    if "broken" in row:
        return f"BROKEN JSON: {row['broken']}"
    n_code, n_exec, n_null = row["n_code"], row["n_exec"], row["n_null"]
    errors = row["errors"]
    if errors:
        return f"ERREUR ({len(errors)} cellule(s))"
    if n_code == 0:
        return "markdown only"
    if n_null == n_code and row["has_outputs"] == 0:
        return "NON EXECUTE"
    if n_null == n_code and row["has_outputs"] > 0:
        return f"OUTPUTS sans execution_count ({row['has_outputs']} cell.)"
    if n_null > 0:
        return f"PARTIEL ({n_exec}/{n_code} executees)"
    return f"OK ({n_exec}/{n_code} executees)"


def main() -> None:
    rows: list[dict] = []
    def scan(root: Path, label: str) -> None:
        if not root.exists():
            return
        for p in sorted(root.glob("*.ipynb")):
            if p.name == "Untitled5.ipynb":
                continue
            try:
                r = audit(p)
                r["path"] = str(p.relative_to(ROOT))
                r["name"] = p.name
                r["label"] = label
                rows.append(r)
            except Exception as exc:
                rows.append({
                    "path": str(p.relative_to(ROOT)),
                    "name": p.name,
                    "label": label,
                    "broken": str(exc),
                })

    for root in ROOTS:
        scan(root, "livrable")
    for root in COLAB_ARCHIVE_ROOTS:
        scan(root, "archive")

    print("AUDIT NOTEBOOKS AquaSense_AI (dossier notebooks/ = livrable prof)")
    print("=" * 88)
    for row in rows:
        print(f"{row['path']:50} {status(row)}")
        for i, ename, eval_ in row.get("errors", []):
            safe = eval_.encode("ascii", "replace").decode("ascii")
            print(f"    cellule {i}: {ename}: {safe}")

    livrable = [r for r in rows if r.get("label") == "livrable"]
    ok = sum(1 for r in livrable if status(r).startswith("OK"))
    err = sum(1 for r in livrable if "ERREUR" in status(r))
    partial = sum(1 for r in livrable if "PARTIEL" in status(r))
    not_run = sum(1 for r in livrable if status(r) == "NON EXECUTE")
    print("=" * 88)
    print(
        f"Livrable notebooks/: {len(livrable)} | OK: {ok} | Partiel: {partial} | "
        f"Non execute: {not_run} | Erreur: {err}"
    )


if __name__ == "__main__":
    main()
