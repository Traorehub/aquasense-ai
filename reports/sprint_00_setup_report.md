# Rapport Sprint 0 — Setup & Environnement

**Projet :** AquaSense AI · Maintenance prédictive forages & points d'eau · **Contexte Maroc**  
**Sprint :** S0 — Setup & Environnement  
**Date :** 2026-06-16  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4

---

## 1. Objectif du sprint

Mettre en place un environnement de travail **reproductible** avant toute modélisation :
- Structure du dépôt
- Environnement Python et dépendances
- Accès au dataset proxy **Pump It Up** (benchmark pour pipeline orienté Maroc)
- Validation initiale des données

**Cadrage :** le problème visé est marocain ; le dataset d'entraînement est international (voir [choix_dataset_maroc.md](./choix_dataset_maroc.md)).

**Durée prévue :** 1 jour

---

## 2. Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Structure du projet | Dossiers `data/`, `src/`, `notebooks/`, etc. | ✅ |
| Dépendances Python | `requirements.txt` | ✅ |
| Exclusion Git | `.gitignore` | ✅ |
| Exclusion indexation Cursor | `.cursorignore` | ✅ |
| Instructions | `README.md` | ✅ |
| Vue globale projet | `PROJECT_OVERVIEW.md` | ✅ |
| Téléchargement dataset | `scripts/download_data.py` | ✅ |
| Audit initial | `notebooks/00_setup.ipynb` | ✅ |
| Backlog détaillé | `AquaSense_AI_Sprints_Backlog.md` | ✅ (préexistant) |

---

## 3. Choix d'architecture — structure du dépôt

```
AquaSense_AI/
├── data/raw/          ← Données brutes (NON versionnées)
├── data/cleaned/      ← Données nettoyées (S2+)
├── notebooks/         ← Analyses Jupyter (00 → 07)
├── src/               ← Code réutilisable (preprocessing, train, MQTT…)
├── models/            ← Modèles sauvegardés
├── dashboard/         ← App Streamlit (S7)
├── reports/           ← Rapports par sprint
├── tests/             ← Tests pytest
└── scripts/           ← Utilitaires (download_data.py)
```

### Motivation

| Choix | Pourquoi |
|-------|----------|
| Séparer `data/raw/` du code | Fichiers CSV volumineux (~25 Mo) — inadaptés à Git |
| Dossier `src/` pour le code métier | Importable depuis notebooks et scripts (`from src.preprocessing import …`) |
| `notebooks/` numérotés 00→07 | Alignés sur les sprints — progression claire |
| `PROJECT_OVERVIEW.md` central | Reprise de session sans relire tout le backlog |
| `reports/` par sprint | Traçabilité académique des décisions |

---

## 4. Environnement Python

### Choix : `requirements.txt` avec versions pinnées

```
pandas, numpy, scikit-learn, xgboost, tensorflow, streamlit,
paho-mqtt, matplotlib, seaborn, plotly, pytest, jupyter…
```

**Motivation :**
- **Reproductibilité** : même environnement sur les deux machines de l'équipe et pour le correcteur
- **Versions pinnées** : évite qu'une mise à jour de scikit-learn ou TensorFlow casse le pipeline entre deux sprints

**Commande de setup :**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## 5. Dataset — Pump It Up (DrivenData)

### Source

- **Compétition :** [Pump It Up — Data Mining the Water Table](https://www.drivendata.org/competitions/7/)
- **Origine des données :** Taarifa + Tanzanian Ministry of Water
- **Téléchargement :** script automatisé depuis les URLs S3 publiques DrivenData

### Fichiers téléchargés

| Fichier | Taille | Rôle |
|---------|--------|------|
| `train_values.csv` | 19,1 Mo | Features des 59 400 pompes d'entraînement |
| `train_labels.csv` | 1,1 Mo | Labels (`status_group`) |
| `test_values.csv` | 4,8 Mo | Features du set de test (14 850 pompes) |

### Choix : script `download_data.py` plutôt que commit Git

**Motivation :**
- Les CSV bruts ne doivent pas être versionnés (taille + licence compétition)
- Pump It Up sert de **proxy** faute de dataset Maroc ouvert labellisé à grande échelle (ONEE/ABH sur demande)
- Un script permet de reconstruire `data/raw/` en une commande

---

## 6. Audit initial du dataset (`00_setup.ipynb`)

### Dimensions validées

| Dataset | Shape attendue | Shape obtenue | Statut |
|---------|---------------|---------------|--------|
| `train_values` | (59 400, 40) | (59 400, 40) | ✅ |
| `train_labels` | (59 400, 2) | (59 400, 2) | ✅ |
| `test_values` | (14 850, 40) | (14 850, 40) | ✅ |

### Types de colonnes

| Type | Nombre de colonnes |
|------|-------------------|
| Texte (string) | 28 |
| Entier (int64) | 7 |
| Float (float64) | 3 |
| Objet mixte | 2 |

### Distribution de la cible (`status_group`)

| Classe | Count | % |
|--------|-------|---|
| `functional` | 32 259 | 54,3 % |
| `non functional` | 22 824 | 38,4 % |
| `functional needs repair` | 4 317 | **7,3 %** |

**Observation clé dès le S0 :** forte imbalance — la classe `needs repair` (la plus critique métier) est minoritaire à 7,3 %. Cela guidera les choix de `class_weight` / SMOTE au Sprint 3.

### Valeurs manquantes (top)

| Colonne | NaN |
|---------|-----|
| `scheme_name` | 28 810 (48,5 %) |
| `scheme_management` | 3 878 |
| `installer` | 3 655 |
| `funder` | 3 637 |
| `public_meeting` | 3 334 |

→ Ces chiffres alimentent directement les décisions de nettoyage du Sprint 2.

---

## 7. Fichiers `.gitignore` et `.cursorignore`

### `.gitignore` — exclut de Git

- `data/raw/` et `data/cleaned/*.csv`
- `.venv/`
- `models/*.joblib`, `*.keras`, `*.tflite`
- `.env`, caches Python, checkpoints Jupyter

### `.cursorignore` — exclut de l'indexation Cursor

Même logique + fichiers binaires lourds.

**Motivation :** accélérer l'indexation de l'IDE et éviter que l'agent IA charge 25 Mo de CSV inutilement.

---

## 8. Critères d'acceptation

| Critère | Statut |
|---------|--------|
| `pip install -r requirements.txt` sans erreur | ⚠️ Partiel (core installé, TensorFlow/XGBoost à valider sur machine fraîche) |
| Dataset chargé : 59 400 × 40 | ✅ |
| Premier commit GitHub | ⏳ À faire par l'équipe en fin de projet |

---

## 9. Décisions reportées aux sprints suivants

| Observation S0 | Sprint concerné |
|----------------|-----------------|
| Imbalance 54% / 7% / 39% | S3 — `class_weight`, SMOTE |
| 28 810 NaN dans `scheme_name` | S2 — colonne supprimée (quasi-vide) |
| 3 637 NaN dans `funder` | S2 — imputation + top-20 |
| Pas d'EDA graphique poussée | **S1 — non réalisé, voir note ci-dessous** |

---

## 10. Limites de ce sprint

- L'audit du S0 est **fonctionnel** (dimensions, types, cible) mais pas une EDA complète — celle-ci était prévue au **Sprint 1** (graphiques, corrélations, cartographie).
- Le Sprint 1 n'a pas été implémenté avant le Sprint 2 : les anomalies ont été traitées directement dans `preprocessing.py` en s'appuyant sur la littérature Pump It Up et un audit minimal.

---

## 11. Fichiers produits

```
PROJECT_OVERVIEW.md
README.md
requirements.txt
.gitignore / .cursorignore
scripts/download_data.py
notebooks/00_setup.ipynb
data/raw/train_values.csv
data/raw/train_labels.csv
data/raw/test_values.csv
reports/sprint_00_setup_report.md   ← Ce rapport
```

---

## 12. Prochain sprint

**Sprint 1 (EDA)** — exploratio n graphique complète *(non encore réalisé)*  
**Sprint 2 (Wrangling)** — ✅ réalisé ensuite directement

---

*Rapport généré dans le cadre du projet AquaSense AI · EHTP MIG S4 · Dr. Rym Nassih*
