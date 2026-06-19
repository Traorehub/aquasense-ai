"""Execute les notebooks locaux et sauvegarde les sorties in-place."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
NB_DIR = ROOT / "notebooks"

LOCAL_NOTEBOOKS = [
    "00_setup.ipynb",
    "01_eda.ipynb",
    "02_wrangling.ipynb",
    "03_ml_baseline.ipynb",
    "04_dl_advanced.ipynb",
    "04_dl_tuning_export.ipynb",
    "05_comparison_final.ipynb",
    "06_mqtt_test.ipynb",
]


def run_one(name: str) -> int:
    path = NB_DIR / name
    cmd = [
        str(VENV_PYTHON),
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        "--inplace",
        f"--ExecutePreprocessor.timeout=1200",
        str(path),
    ]
    print(f"\n=== Execution {name} ===")
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[-2000:])
    if result.returncode != 0:
        print("STDERR:", result.stderr[-3000:])
    return result.returncode


def main() -> None:
    failed = []
    for name in LOCAL_NOTEBOOKS:
        code = run_one(name)
        status = "OK" if code == 0 else f"ECHEC ({code})"
        print(f"{name}: {status}")
        if code != 0:
            failed.append(name)
    print("\nResume:")
    print(f"  Reussis: {len(LOCAL_NOTEBOOKS) - len(failed)}/{len(LOCAL_NOTEBOOKS)}")
    if failed:
        print(f"  Echecs: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
