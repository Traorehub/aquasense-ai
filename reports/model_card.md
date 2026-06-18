# Model Card — AquaSense AI

**Projet :** Maintenance prédictive forages & points d'eau · Contexte **Maroc**  
**Dataset d'entraînement :** Pump It Up (Tanzanie, DrivenData) — proxy structurel  
**Date :** 2026-06-19 · Sprint 5  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4

---

## 1. Modèles retenus pour la production

Deux modèles complémentaires selon l'objectif métier :

| Rôle | Modèle | Fichier | Métrique clé |
|------|--------|---------|--------------|
| **Alertes « needs repair »** (priorité Maroc) | XGBoost SMOTE + seuil 0.17 | `champion_recall_v1.joblib` | Recall **0.685** |
| **F1-Macro global / analytics** | Soft Voting RF + XGB | `voting_rf_xgb_v1.joblib` | F1-Macro **0.679** |

Fichier alias déploiement dashboard : `champion_production_v1.joblib` (= recall champion).

---

## 2. Intended use (cas d'usage)

### Modèle alertes — `champion_recall_v1.joblib`

- **Usage :** détecter les pompes **dégradées nécessitant une intervention** avant panne complète.
- **Utilisateurs :** techniciens maintenance, opérateurs réseau eau rural Maroc.
- **Sortie :** `functional` · `functional needs repair` · `non functional`.
- **Recommandé pour :** dashboard Streamlit (S7), file d'alertes, priorisation terrain.

### Modèle F1 — `voting_rf_xgb_v1.joblib`

- **Usage :** classification équilibrée sur les 3 classes, rapports KPI, comparaison scientifique.
- **Non recommandé seul** si la priorité est uniquement la détection `needs repair` (recall inférieur au champion alertes).

---

## 3. Données d'entraînement

| Paramètre | Valeur |
|-----------|--------|
| Source | `data/cleaned/train_clean.csv` |
| Lignes | 59 400 pompes |
| Features | 26 (pipeline `PumpPreprocessor`) |
| Cible | `status_group` (3 classes) |
| Split | 80/20 stratifié, `random_state=42` |
| Test | 11 880 pompes |

### Distribution des classes

| Classe | ~% |
|--------|-----|
| functional | 54 % |
| functional needs repair | 7 % |
| non functional | 39 % |

---

## 4. Performances (jeu de test)

### Champion alertes — XGB SMOTE + seuil

| Métrique | Valeur | Cible |
|----------|--------|-------|
| Recall `needs repair` | **0.6848** | ≥ 0.65 ✅ |
| F1-Macro | 0.6295 | ≥ 0.72 ❌ |
| F1 `needs repair` | 0.394 | — |
| Accuracy | 0.705 | — |
| ROC-AUC macro OvR | 0.870 | — |
| Latence | ~0.02 ms/échantillon | — |

### Champion F1 — Voting RF + XGB (soft)

| Métrique | Valeur | Cible |
|----------|--------|-------|
| F1-Macro | **0.6787** | ≥ 0.72 ❌ |
| Recall `needs repair` | 0.4855 | ≥ 0.65 ❌ |
| F1 `needs repair` | 0.446 | — |
| Accuracy | 0.770 | — |
| ROC-AUC macro OvR | 0.887 | — |
| Latence | ~0.035 ms/échantillon | — |

### Deep Learning (référence — non déployé)

Meilleur DL (S4) : MLP L2=0.001, F1=**0.541** — inférieur au ML.

---

## 5. Facteurs influents (interprétation)

D'après feature importance S3 (RF / XGB) :

- `age_years`, `amount_tsh` — vieillissement et hydraulique
- `longitude`, `latitude` — contexte géographique
- `installer`, `funder`, `wpt_name` — gestion et maintenance historique
- `extraction_type`, `management` — type d'installation

---

## 6. Biais et limites connus

| Limite | Impact | Mitigation |
|--------|--------|------------|
| Données **Tanzanie**, pas Maroc | Transfert domaine imparfait | Cadrage explicite dans le rapport ; dashboard présenté Maroc |
| Classe `needs repair` minoritaire (7 %) | Conflit F1 vs recall | Deux modèles selon l'objectif |
| F1 cible 0.72 non atteint | 0.679 max (voting) | Documenté ; plafond dataset Pump It Up |
| DL sous-performe le ML | Pas de gain réseau de neurones | ML retenu après S4 |
| Features catégorielles haute cardinalité | Top-20 funder/installer | Wrangling S2 documenté |
| Pas de capteurs IoT réels en entrée | Modèle tabulaire statique | Simulation MQTT prévue S6 |

---

## 7. Risques d'utilisation inappropriée

- **Ne pas** utiliser le modèle DL Colab en production (F1 ~0.54).
- **Ne pas** attendre une précision élevée sur `needs repair` avec le champion recall (précision ~0.29–0.40) — privilégier le **rappel** pour ne pas manquer de pompes à risque.
- **Ne pas** déployer sans re-calibrer le seuil si la distribution des classes change (nouveau pays / nouvelle campagne de mesure).

---

## 8. Reproduction

```powershell
# Entraînement Sprint 5 (voting + arbitrage)
py -3.10 -m src.train final

# Recall boost seul (si besoin)
py -3.10 -m src.train recall
```

**Fichiers associés :**
- `reports/sprint_05_metrics.json`
- `reports/sprint_05_final_comparison.csv`
- `reports/sprint_05_arbitration_report.md`

---

## 9. Décision Sprint 5

| Question | Décision |
|----------|----------|
| Champion production alertes Maroc ? | **XGB SMOTE + seuil** (`champion_recall_v1.joblib`) |
| Champion F1 / rapport scientifique ? | **Voting RF+XGB** (`voting_rf_xgb_v1.joblib`) |
| Deep Learning en production ? | **Non** |
| Prochaine étape ? | Sprint 6 — simulation MQTT + inférence temps réel |

---

*Model Card alignée sur `python -m src.train final` — 19/06/2026.*
