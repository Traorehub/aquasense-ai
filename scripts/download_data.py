"""
Télécharge le dataset proxy Pump It Up (Tanzanie) depuis DrivenData.

Benchmark d'entraînement pour le pipeline AquaSense AI (contexte Maroc).
Voir reports/choix_dataset_maroc.md pour la justification.

Usage:
    python scripts/download_data.py
"""

from pathlib import Path
import sys

import requests
from tqdm import tqdm

DATA_URLS = {
    "train_values.csv": (
        "http://s3.amazonaws.com/drivendata/data/7/public/"
        "4910797b-ee55-40a7-8668-10efd5c1b960.csv"
    ),
    "train_labels.csv": (
        "http://s3.amazonaws.com/drivendata/data/7/public/"
        "0bf8bc6e-30d0-4c50-956a-603fc693d966.csv"
    ),
    "test_values.csv": (
        "http://s3.amazonaws.com/drivendata/data/7/public/"
        "702ddfc5-68cd-4d1d-a0de-f5f566f76d91.csv"
    ),
}

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def download_file(url: str, dest: Path) -> None:
    """Télécharge un fichier avec barre de progression."""
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()
    total = int(response.headers.get("content-length", 0))

    with open(dest, "wb") as f, tqdm(
        total=total,
        unit="B",
        unit_scale=True,
        desc=dest.name,
    ) as bar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Dossier cible : {RAW_DIR}\n")

    for filename, url in DATA_URLS.items():
        dest = RAW_DIR / filename
        if dest.exists():
            size_mb = dest.stat().st_size / (1024 * 1024)
            print(f"[SKIP] {filename} déjà présent ({size_mb:.1f} Mo)")
            continue
        print(f"[DL]   {filename} ...")
        download_file(url, dest)
        size_mb = dest.stat().st_size / (1024 * 1024)
        print(f"[OK]   {filename} ({size_mb:.1f} Mo)\n")

    print("Téléchargement terminé.")


if __name__ == "__main__":
    try:
        main()
    except requests.RequestException as e:
        print(f"Erreur réseau : {e}", file=sys.stderr)
        sys.exit(1)
