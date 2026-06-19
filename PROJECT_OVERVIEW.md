# AquaSense AI — Vue Globale du Projet (A → Z)

> **Fichier de référence central** — Retourne ici à chaque session pour reprendre le fil.
> **Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · **EHTP MIG S4**
> **Dernière mise à jour :** 2026-06-19

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
| **S3** | Baseline ML | 3–4j | ✅ Terminé | LR, KNN, RF, XGBoost, GridSearch, recall boost |
| **S4** | Deep Learning | 3–4j | ✅ Terminé | 6 archi DL Colab ; F1 max 0.54 — ML reste champion → S5 |
| **S5** | Comparaison finale | 2j | ✅ Terminé | Voting F1=0.679 ; recall champ 0.685 ; `model_card.md` |
| **S6** | Simulation IoT MQTT | 2j | ✅ Terminé | Mosquitto Windows + simulator + consumer + SQLite |
| **S7** | Dashboard Streamlit (vue Maroc) | 2–3j | ✅ Terminé | `dashboard/app.py` — KPIs, carte, alertes, auto-refresh |
| **S8** | Tests simulation | 2j | ✅ Terminé | pytest 37/37 — offline + intégration MQTT |
| **S9** | Rapport & Livrables | 1–2j | 🟡 En cours | `AquaSense_AI_Report.md` rédigé · PDF à exporter |

**Légende :** ⬜ À faire · 🟡 En cours · ✅ Terminé (S3 : recall métier ✅, F1 cible 0.72 reporté au S4/S5)

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
python -m src.train                    # S3 baselines
python -m src.train recall             # S3 recall boost (SMOTE + seuil)
python -m src.train_dl                 # S4 DL (MLP + Residual + CNN)
python -m src.train_dl tune            # S4 + grid search + TFLite
python -m src.train final              # S5 arbitrage + voting RF+XGB
py -3.10 -m src.mqtt_consumer           # S6 consumer inférence MQTT
py -3.10 -m src.simulator                # S6 simulateur 50 pompes
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

### 📅 2026-06-17 — Session 5 : Sprint 3 (Baseline ML)

**Actions :** `src/train.py` (4 baselines + GridSearch RF/XGB), `XGBStringLabelPipeline`, notebook `03_ml_baseline.ipynb`, modèles joblib, métriques JSON/CSV, rapport S3.

**Résultats :**
- Champion F1-Macro : **RF tuned** (0.6658) — cible 0.72 non atteinte
- Meilleur recall needs repair : **XGB tuned** (0.6419) — cible 0.65 quasi atteinte
- Livrables techniques : ✅ · Objectifs métriques : partiels

**Prochaine étape :** Sprint 4 — Deep Learning.

---

### 📅 2026-06-17 — Session 6 : Recall boost (SMOTE + seuil)

**Commande :** `python -m src.train recall`

**Résultat :** recall needs repair **0.6952** ✅ (cible 0.65) avec `xgboost_smote_threshold` (seuil 0.16).  
F1-Macro recall champion : 0.6289 — compromis recall / précision attendu.

**Modèles :** `champion_recall_v1.joblib`, `xgb_smote_threshold_v1.joblib`

**Prochaine étape :** Sprint 4 — Deep Learning (Colab GPU **optionnel**, pas obligatoire).

---

### 📅 2026-06-19 — Session 7 : Notebook S3 + rapport final

**Actions :** notebook `03_ml_baseline.ipynb` exécuté (comparatif, confusion matrices, feature importance, critères §6). Rapport `sprint_03_ml_report.md` complété (captures terminal, PNG notebook, recall boost).

**Confirmé :** entraînements S3 **terminés** en local CPU — modèles `.joblib` + PNG sur disque. Pas besoin de Colab pour S3.

**Prochaine étape :** Sprint 4 DL — local ou Colab si tuning long.

---

### 📅 2026-06-19 — Session 8 : MLP Colab (S4)

**Actions :** exécution `04_dl_mlp.ipynb` sur Colab (GPU T4). Résultats intégrés : `models/mlp_best_v1.keras`, `notebooks/04_dl_mlp_colab_run.ipynb`, rapport **`reports/sprint_04_dl_report.md`** + PNG + JSON.

**Métriques test (MLP baseline) :** F1-Macro **0.5297**, Recall needs repair **0.6037**, Accuracy **0.5950** — sous les baselines ML (RF F1 0.67, XGB recall 0.70). Verdict : sprint S4 en cours, projet globalement sain.

**Prochaine étape :** `python -m src.train_dl tune` sur Colab.

---

### 📅 2026-06-19 — Session 9 : Tuning DL Colab (fin S4)

**Actions :** `05_dl_colab_tune.ipynb` exécuté — `python -m src.train_dl tune` (MLP + Residual + CNN + grid 9 configs).

**Résultats :** meilleur DL **mlp_l2_0.001** F1=**0.5410** ; champion script **mlp_baseline** 0.5297. Toujours **sous ML** (RF 0.67, XGB recall 0.70). Rapport `sprint_04_dl_report.md` finalisé.

**Verdict S4 :** DL ne bat pas le ML sur Pump It Up — **champion = ML** pour S5.

**Prochaine étape :** Sprint 5 — Voting RF+XGB, `model_card.md`.

---

### 📅 2026-06-19 — Session 10 : Sprint 5 terminé

**Actions :** `python -m src.train final` — Soft Voting RF+XGB, recall champion, tableau ML+DL.

**Résultats :** F1 champion **voting_rf_xgb_soft = 0.6787** (+0.02 vs XGB seul). Recall métier **0.6848** (XGB SMOTE+seuil). DL exclu prod.

**Livrables :** `model_card.md`, `sprint_05_arbitration_report.md`, `voting_rf_xgb_v1.joblib`, `champion_production_v1.joblib`.

**Prochaine étape :** Sprint 6 — simulation MQTT + inférence temps réel.

---

### 📅 2026-06-19 — Session 11 : Sprint 6 terminé

**Actions :** pipeline MQTT 100 % Windows — Mosquitto local, `simulator.py`, `mqtt_consumer.py`, SQLite, profils 50 pompes.

**Architecture :** broker `127.0.0.1:1883` · topics `aquasense/{id}/telemetry|prediction` · modèle `champion_production_v1.joblib`.

**Résultats test 50 pompes :** latence **22–70 ms** · 5 alertes `needs repair` · persistance `data/mqtt/aquasense.db`.

**Livrables :** `reports/sprint_06_mqtt_report.md`, `sprint_06_metrics.json`, `.env.example`, `scripts/test_mqtt_e2e.py`.

**Prochaine étape :** Sprint 7 — dashboard Streamlit Maroc.

---

### 📅 2026-06-19 — Session 12 : Sprint 7 terminé

**Actions :** `dashboard/app.py` + `dashboard/data.py` — KPIs, carte Plotly, alertes, détail pompe, comparaison modèles, auto-refresh 10 s SQLite.

**Commande :** `streamlit run dashboard/app.py`

**Prochaine étape :** Sprint 8 — tests simulation E2E.

---

### 📅 2026-06-19 — Session 13 : Sprint 9 (rapport académique)

**Actions :** rédaction `reports/AquaSense_AI_Report.md` (synthèse S0–S8), `reports/presentation.md` (15 slides), `reports/sprint_09_final_report.md`.

**Contenu rapport :** contexte Maroc, dataset proxy, ML/DL, MQTT, dashboard, tests 37/37, limites transfert, annexes.

**Reste S9 :** export PDF (`AquaSense_AI_Report.pdf`, `presentation.pdf`), tag `v1.0.0`, test reproductibilité clone frais.

---

## 8. Décisions techniques prises

| Date | Décision | Raison |
|------|----------|--------|
| 2026-06-16 | Python 3.10+ | Compatibilité TensorFlow + scikit-learn |
| 2026-06-16 | `data/raw/` exclu de Git | CSV volumineux (~50 Mo) |
| 2026-06-17 | `PumpPreprocessor` fit/transform | Évite data leakage |
| 2026-06-17 | Pump It Up conservé | Pas de dataset Maroc ouvert équivalent |
| 2026-06-17 | Problème = Maroc · données = proxy Tanzanie | Même paradigme ML, cadrage local |
| 2026-06-17 | `sample_weight` balanced pour XGBoost | Classe minoritaire needs repair (~7 %) |
| 2026-06-17 | `XGBStringLabelPipeline` | XGBoost 3.x + labels string + sample_weight |
| 2026-06-17 | Champion recall = XGB SMOTE+seuil (0.70) | Recall needs repair ≥ 0.65 atteint ; F1 recall champion 0.63 |
| 2026-06-19 | MQTT 100 % Windows local (pas VM/Cloudflared) | Reproductible en TP ; Mosquitto winget + port 1883 |
| 2026-06-19 | Profils ML + télémétrie simulée (hybride) | Modèle tabulaire S5 ; capteurs pour démo IoT + health_index |

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
