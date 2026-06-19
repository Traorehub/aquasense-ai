"""Re-execute un notebook en supprimant les sorties d'erreur."""
from __future__ import annotations

import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

ROOT = Path(__file__).resolve().parents[1]


def execute(name: str) -> int:
    path = ROOT / "notebooks" / name
    nb = nbformat.read(path, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = [o for o in cell.outputs if o.get("output_type") != "error"]
    client = NotebookClient(
        nb,
        timeout=1200,
        startup_timeout=180,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    try:
        client.execute()
        nbformat.write(nb, path)
        print(f"OK {name}")
        return 0
    except CellExecutionError as exc:
        nbformat.write(nb, path)
        print(f"ECHEC {name}: {exc}")
        return 1


if __name__ == "__main__":
    names = sys.argv[1:] or ["05_comparison_final.ipynb"]
    code = 0
    for n in names:
        code = max(code, execute(n))
    sys.exit(code)
