"""Execute notebooks via nbclient (plus fiable que nbconvert sous Windows)."""

from __future__ import annotations



import sys

from pathlib import Path



import nbformat

from nbclient import NotebookClient

from nbclient.exceptions import CellExecutionError



ROOT = Path(__file__).resolve().parents[1]

NB_DIR = ROOT / "notebooks"



NOTEBOOKS = [

    "04_dl_advanced.ipynb",

    "04_dl_tuning_export.ipynb",

    "05_comparison_final.ipynb",

    "03_ml_baseline.ipynb",

    "06_mqtt_test.ipynb",

]





def run_one(name: str) -> bool:

    path = NB_DIR / name

    print(f"\n=== {name} ===", flush=True)

    nb = nbformat.read(path, as_version=4)

    client = NotebookClient(

        nb,

        timeout=1200,

        kernel_name="python3",

        resources={"metadata": {"path": str(NB_DIR)}},

    )

    try:

        client.execute()

        nbformat.write(nb, path)

        print(f"OK  {name}", flush=True)

        return True

    except CellExecutionError as exc:

        print(f"ECHEC {name}: {exc}", flush=True)

        nbformat.write(nb, path)

        return False





def main() -> None:

    failed = []

    for name in NOTEBOOKS:

        if not run_one(name):

            failed.append(name)

    print("\n--- Resume ---")

    print(f"Reussis: {len(NOTEBOOKS) - len(failed)}/{len(NOTEBOOKS)}")

    if failed:

        print("Echecs:", ", ".join(failed))

        sys.exit(1)





if __name__ == "__main__":

    main()


