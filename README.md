# AquaSense AI

**Maintenance prédictive des forages & points d'eau · Contexte Maroc · EHTP MIG S4**

Système de prédiction de l'état des installations d'eau (`functional`, `functional needs repair`, `non functional`) motivé par le **contexte marocain**, avec pipeline ML entraîné sur le benchmark international **Pump It Up** (proxy reproductible).

## Équipe

- TRAORE Fanogo Mohamed
- NADAHE Mohamed

## Documents essentiels (à lire en premier)

| Document | Contenu |
|----------|---------|
| [reports/choix_dataset_maroc.md](./reports/choix_dataset_maroc.md) | Pourquoi Maroc + pourquoi Pump It Up |
| [reports/guide_dataset_et_wrangling.md](./reports/guide_dataset_et_wrangling.md) | Dataset, features, logique métier |
| [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) | Roadmap, journal, commandes |

## Démarrage rapide

```bash
git clone <url-du-repo>
cd AquaSense_AI
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python scripts/download_data.py
jupyter notebook notebooks/00_setup.ipynb
```

## Structure du projet

```
data/raw/          → Pump It Up (proxy, non versionné)
data/cleaned/      → Dataset après preprocessing
notebooks/         → Analyses (00 → 07)
src/               → preprocessing, train, MQTT
models/            → Modèles entraînés
dashboard/         → Streamlit (vue Maroc)
reports/           → Rapports sprint + cadrage Maroc
tests/             → pytest
```

## Dataset d'entraînement (proxy)

- **Jeu :** [Pump It Up — DrivenData](https://www.drivendata.org/competitions/7/) (Tanzanie, 2011–2013)
- **Rôle :** benchmark méthodologique — structure analogue aux points d'eau ruraux marocains
- **Fichiers :** `train_values.csv`, `train_labels.csv`, `test_values.csv`
- **Dimensions :** 59 400 lignes × 40 colonnes (train_values)

## Objectifs métriques

| Métrique | Cible |
|----------|-------|
| F1-Macro | ≥ 0.72 |
| Recall `needs repair` | ≥ 0.65 |

## Cadrage

| Couche | Périmètre |
|--------|-----------|
| Problème & rapport | Maroc |
| Entraînement ML | Pump It Up (proxy) |
| Dashboard & MQTT | Présentation Maroc |

## Licence

Projet académique — EHTP MIG S4 · Dr. Rym Nassih
