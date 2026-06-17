# AquaSense AI — Vue Globale du Projet (A → Z)

> **Fichier de référence central** — Retourne ici à chaque session pour reprendre le fil.
> **Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · **EHTP MIG S4**
> **Dernière mise à jour :** 2026-06-17

---

## 1. Qu'est-ce que ce projet ?

**AquaSense AI** est un système de **maintenance prédictive des forages et points d'eau** motivé par le **contexte marocain** (stress hydrique, zones rurales, vieillissement des installations).

Le pipeline ML est entraîné sur le benchmark international **Pump It Up** (Tanzanie, DrivenData) — jeu ouvert, labellisé et reproductible, structure analogue aux points d'eau ruraux marocains. Voir **[reports/choix_dataset_maroc.md](./reports/choix_dataset_maroc.md)** pour la justification complète.

| Classe cible | Signification | ~Distribution |
|--------------|---------------|---------------|
| `functional` | Pompe opérationnelle | ~54 % |
| `functional needs repair` | Dégradée, réparation nécessaire | ~7 % |
| `non functional` | Hors service | ~39 % |

**Objectifs métriques clés :**
- F1-Macro ≥ 0.72
- Recall classe `needs repair` ≥ 0.65

**Priorités (ordre décroissant) :**
1. Modèle ML + Deep Learning (Sprints 3–5)
2. Déploiement : simulation MQTT + dashboard Streamlit orienté Maroc (Sprints 6–8)
3. ~~Implémentation terrain réelle~~ — hors scope académique

**Cadrage géographique :**
| Couche | Périmètre |
|--------|-----------|
| Problème & rapport | **Maroc** |
| Données d'entraînement | **Pump It Up** (Tanzanie, proxy) |
| Dashboard & simulation | Présentation **Maroc** |

---

## 2. Architecture du dépôt

```
AquaSense_AI/
├── PROJECT_OVERVIEW.md              ← CE FICHIER (vue globale + journal)
├── AquaSense_AI_Sprints_Backlog.md  ← Backlog détaillé par sprint
├── README.md                        ← Instructions de reproduction
├── requirements.txt
│
├── reports/
│   ├── choix_dataset_maroc.md       ← Cadrage Maroc + justification dataset ★
│   ├── guide_dataset_et_wrangling.md← Guide pédagogique données & features ★
│   ├── sprint_XX_*.md               ← Rapports par sprint
│   └── model_card.md                ← (S5) Fiche modèle champion
│
├── data/
│   ├── raw/                         ← Pump It Up (NON versionné Git)
│   └── cleaned/                     ← Après preprocessing (S2)
│
├── notebooks/                       ← 00_setup → 07_report
├── src/                             ← preprocessing, train, simulator, mqtt_consumer
├── models/                          ← Modèles sauvegardés
├── dashboard/                       ← Streamlit (S7)
└── tests/                           ← pytest
```

**Documents à lire en priorité :**
1. [choix_dataset_maroc.md](./reports/choix_dataset_maroc.md)
2. [guide_dataset_et_wrangling.md](./reports/guide_dataset_et_wrangling.md)

---

## 3. Stack technique

| Couche | Technologies | Sprints |
|--------|-------------|---------|
| Data | pandas, numpy | S1, S2 |
| ML classique | scikit-learn, XGBoost, joblib | S3, S5 |
| Deep Learning | TensorFlow/Keras | S4, S5 |
| IoT Simulation | paho-mqtt, Mosquitto, Faker | S6 |
| Dashboard | Streamlit, Plotly | S7 |
| Tests | pytest | S8 |

---

## 4. Roadmap des sprints — Statut

| Sprint | Thème | Durée | Statut | Livrables clés |
|--------|-------|-------|--------|----------------|
| **S0** | Setup & Environnement | 1j | ✅ Terminé | structure, requirements, dataset, 00_setup.ipynb |
| **S1** | Acquisition & EDA | 2–3j | ✅ Terminé | 01_eda.ipynb, 8+ graphiques, cadrage Maroc |
| **S2** | Wrangling & Feature Engineering | 3j | ✅ Terminé | preprocessing.py, train_clean.csv |
| **S3** | Baseline ML | 3–4j | ⬜ À faire | LR, KNN, RF, XGBoost, F1 ≥ 0.72 |
| **S4** | Deep Learning | 3–4j | ⬜ À faire | MLP, ResidualMLP/1D-CNN, .keras + .tflite |
| **S5** | Comparaison finale | 2j | ⬜ À faire | Tableau comparatif, model_card.md |
| **S6** | Simulation IoT Mosquitto | 2j | ⬜ À faire | simulator.py, mqtt_consumer.py |
| **S7** | Dashboard Streamlit (vue Maroc) | 2–3j | ⬜ À faire | dashboard/app.py |
| **S8** | Tests simulation | 2j | ⬜ À faire | pytest, scénarios E2E |
| **S9** | Rapport & Livrables | 1–2j | ⬜ À faire | PDF, section choix dataset Maroc |

**Légende :** ⬜ À faire · 🟡 En cours · ✅ Terminé

---

## 5. Pipeline de bout en bout (vision A → Z)

```
[Contexte Maroc — maintenance forages & points d'eau]
        │
        ▼
[Dataset proxy : Pump It Up — 59 400 pompes labellisées]
        │
        ▼
  S0 Setup ──► data/raw/*.csv
        │
        ▼
  S1 EDA ──► Anomalies, imbalance, Problem Statement (cadrage Maroc)
        │
        ▼
  S2 Wrangling ──► src/preprocessing.py ──► data/cleaned/
        │
        ├──────────────────┐
        ▼                  ▼
  S3 ML Classique    S4 Deep Learning
        │                  │
        └────────┬─────────┘
                 ▼
  S5 Comparaison ──► Modèle champion + model_card.md
                 │
                 ▼
  S6 MQTT Sim ──► Scénarios saison sèche (juin–sept, Maroc)
                 │
                 ▼
  S7 Dashboard ──► Carte & KPIs (présentation Maroc)
                 │
                 ▼
  S8 Tests ──► pytest + 50 pompes simulées
                 │
                 ▼
  S9 Rapport ──► PDF + section limites transfert Maroc
```

---

## 6. Commandes utiles (mémo rapide)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_data.py
jupyter notebook notebooks/00_setup.ipynb
python src/preprocessing.py
pytest tests/ -v
python src/train.py                    # S3
streamlit run dashboard/app.py         # S7
```

---

## 7. Journal des sessions

---

### 📅 2026-06-16 — Session 1 : Sprint 0 (Setup)

**Actions :** structure dépôt, requirements, download_data.py, 00_setup.ipynb, rapports S0.

**Critères S0 :** 59 400 × 40 confirmé · distribution cible validée.

---

### 📅 2026-06-17 — Session 2 : Sprint 2 (Wrangling)

**Actions :** `preprocessing.py`, `PumpPreprocessor`, 8 features, 13 tests pytest, train_clean.csv.

**Prochaine étape :** Sprint 3 ML.

---

### 📅 2026-06-17 — Session 3 : Sprint 1 (EDA — rattrapage)

**Actions :** `01_eda.ipynb`, 12+ graphiques, Problem Statement, AI Context Note, rapport S1.

---

### 📅 2026-06-17 — Session 4 : Cadrage Maroc & documentation

**Objectif :** Aligner la documentation sur le focus Maroc tout en conservant Pump It Up comme dataset d'entraînement.

**Décision :** pas de changement de paradigme ni de refonte S0–S2. Adaptation narrative + rapport final.

**Actions réalisées :**
- [x] `reports/choix_dataset_maroc.md` — justification dataset + limites
- [x] Mise à jour `PROJECT_OVERVIEW.md`, `AquaSense_AI_Sprints_Backlog.md`, `README.md`
- [x] Mise à jour rapports sprint S0–S2 et `guide_dataset_et_wrangling.md`
- [x] Mise à jour Problem Statement dans `01_eda.ipynb`

**Prochaine étape :** Sprint 3 — Baseline ML.

---

## 8. Décisions techniques prises

| Date | Décision | Raison |
|------|----------|--------|
| 2026-06-16 | Python 3.10+ | Compatibilité TensorFlow + scikit-learn |
| 2026-06-16 | `data/raw/` exclu de Git | CSV volumineux (~50 Mo) |
| 2026-06-17 | `PumpPreprocessor` fit/transform | Évite data leakage |
| 2026-06-17 | Pump It Up conservé | Pas de dataset Maroc ouvert équivalent |
| 2026-06-17 | Problème = Maroc · données = proxy Tanzanie | Même paradigme ML, cadrage local |
| 2026-06-17 | S0–S2 non refaits | Pipeline et features universellement valides |

---

## 9. Liens & ressources

- **Cadrage Maroc :** [reports/choix_dataset_maroc.md](./reports/choix_dataset_maroc.md)
- **Guide dataset :** [reports/guide_dataset_et_wrangling.md](./reports/guide_dataset_et_wrangling.md)
- **Compétition DrivenData :** https://www.drivendata.org/competitions/7/
- **Backlog :** [AquaSense_AI_Sprints_Backlog.md](./AquaSense_AI_Sprints_Backlog.md)
- **Open data Maroc (eau) :** https://www.data.gov.ma/data/fr/dataset/?tags=eau
- **Repo GitHub :** https://github.com/Traorehub/aquasense-ai

---

*Commence par la section 7 (Journal) et [choix_dataset_maroc.md](./reports/choix_dataset_maroc.md) pour reprendre le fil.*
