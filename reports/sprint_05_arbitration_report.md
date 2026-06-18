# Rapport Sprint 5 — Arbitrage champion & comparaison finale

**Projet :** AquaSense AI · Maintenance prédictive forages & points d'eau · **Contexte Maroc**  
**Sprint :** S5 — Optimisation finale & sélection modèle de production  
**Date :** 2026-06-19  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4  
**Statut :** ✅ **Terminé**

---

## 1. Objectif

Sélectionner le **modèle de production** après comparaison ML (S3) + DL (S4), tester un **ensemble Voting RF+XGB**, et produire la **Model Card**.

**Commande :** `python -m src.train final`  
**Runtime :** **CPU local** (`.venv`, Python 3.10) — pas de GPU requis.

---

## 2. Capture terminal — exécution locale

![Résultats terminal — Sprint 5 final](image/Capture%20d'écran%202026-06-19%20035916.png)

*Entraînement RF + XGB + recall champion + voting. Durée ~1–2 min sur CPU. Seuil calibré : 0.17.*

---

## 3. Critères d'acceptation

| Critère | Cible | Résultat | Statut |
|---------|-------|----------|--------|
| Tableau comparatif ML + DL | Oui | `sprint_05_final_comparison.csv` | ✅ |
| Voting ensemble RF + XGB | Oui | F1 = **0.6787** | ✅ |
| Champion sélectionné + justification | Oui | 2 champions (F1 + recall) | ✅ |
| Model Card | Oui | `reports/model_card.md` | ✅ |
| F1-Macro ≥ 0.72 | 0.72 | **0.6787** (voting) | ❌ |
| Recall needs repair ≥ 0.65 | 0.65 | **0.6848** (XGB seuil) | ✅ |

Le sprint est **livré**. La cible F1 0.72 reste hors de portée sur Pump It Up ; le recall métier Maroc est **atteint**.

---

## 4. Nouveauté Sprint 5 — Soft Voting RF + XGB

Moyenne des probabilités (`SoftVotingEnsemble`) de :
- `random_forest_tuned` (params GridSearch S3)
- `xgboost_tuned` (params GridSearch S3)

| Modèle | F1-Macro | Recall needs repair | Accuracy | ROC-AUC |
|--------|----------|---------------------|----------|---------|
| RF tuned (seul) | 0.6537 | 0.315 | 0.772 | 0.872 |
| XGB tuned (seul) | 0.6570 | 0.642 | 0.734 | 0.877 |
| **Voting RF+XGB** 🏆 F1 | **0.6787** | 0.486 | 0.770 | **0.887** |
| XGB SMOTE + seuil 0.17 🏆 recall | 0.6295 | **0.6848** | 0.705 | 0.870 |

**Gain voting vs meilleur modèle seul :** +0.022 F1-Macro vs XGB (0.657 → 0.679).

Le voting **améliore le F1** sans atteindre 0.72, et **n'atteint pas** le recall métier seul (0.49 vs 0.68).

---

## 5. Tableau comparatif global (extrait)

| Modèle | Type | F1-Macro | Recall NR | Accuracy |
|--------|------|----------|-----------|----------|
| **voting_rf_xgb_soft** | ML S5 | **0.6787** | 0.486 | 0.770 |
| random_forest_tuned | ML S3 | 0.6658 | 0.484 | 0.759 |
| xgboost_tuned | ML S3 | 0.6570 | 0.642 | 0.734 |
| xgboost_smote_threshold | ML S3/S5 | 0.6295 | **0.6848** | 0.705 |
| mlp_l2_0.001 | DL S4 | 0.5410 | 0.603 | 0.610 |
| cnn1d | DL S4 | 0.4113 | 0.226 | 0.507 |

Tableau complet : `reports/sprint_05_final_comparison.csv`

---

## 6. Arbitrage — décision de production

### Contexte Maroc : quelle métrique prioriser ?

| Priorité métier | Modèle retenu | Fichier |
|-----------------|---------------|---------|
| **Ne pas rater une pompe à réparer** | XGB SMOTE + seuil | `champion_recall_v1.joblib` |
| **Équilibre global 3 classes** | Voting RF + XGB | `voting_rf_xgb_v1.joblib` |

### Décision documentée

1. **Dashboard & alertes terrain (S7)** → `champion_production_v1.joblib` (= recall champion).
2. **Page analytics / comparaison modèles** → afficher voting comme meilleur F1.
3. **Deep Learning** → exclu de la production (F1 max 0.54).

### Pourquoi pas un seul modèle ?

Conflit métrique documenté depuis S3 :
- Maximiser F1-Macro **sous-détecte** `needs repair` (classe 7 %).
- Maximiser recall **augmente les faux positifs** (précision needs repair ~0.29).

Deux modèles = deux usages légitimes, pas un échec de méthode.

---

## 7. Verdict DL vs ML (rappel S4)

| | Meilleur score | Verdict |
|--|--------------|---------|
| ML (voting) | F1 **0.679** | ✅ Production |
| DL (mlp_l2) | F1 **0.541** | ❌ Référence rapport uniquement |

> Le Deep Learning a été testé sérieusement (6 architectures, grid search Colab). Il **ne justifie pas** un déploiement sur ce dataset tabulaire.

---

## 8. Fichiers générés

```
models/
├── champion_ml_v1.joblib          # RF tuned (alias historique S3)
├── champion_recall_v1.joblib      # XGB SMOTE + seuil — ALERTES
├── champion_production_v1.joblib  # = recall champion (dashboard)
├── voting_rf_xgb_v1.joblib        # Champion F1 — NOUVEAU S5
├── rf_best_v1.joblib
└── xgb_best_v1.joblib

reports/
├── model_card.md                  # Fiche modèle
├── sprint_05_arbitration_report.md
├── sprint_05_metrics.json
└── sprint_05_final_comparison.csv
```

**Reproduction :**
```powershell
py -3.10 -m pip install pandas numpy scikit-learn xgboost imbalanced-learn joblib
py -3.10 -m src.train final
```

---

## 9. Prochaine étape — Sprint 6

| Tâche | Description |
|-------|-------------|
| S6-01 | Broker Mosquitto local |
| S6-02 | `src/simulator.py` — télémetrie simulée |
| S6-06 | `src/mqtt_consumer.py` — inférence avec `champion_production_v1.joblib` |
| S7 | Dashboard Streamlit Maroc |

---

*Rapport Sprint 5 — exécution locale `python -m src.train final`, 19/06/2026.*
