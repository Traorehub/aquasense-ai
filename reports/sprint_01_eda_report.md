# Rapport Sprint 1 — Acquisition & EDA

**Projet :** AquaSense AI · Maintenance prédictive forages & points d'eau · **Contexte Maroc**  
**Sprint :** S1 — Exploratory Data Analysis (EDA)  
**Date :** 2026-06-17  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4

---

## 1. Objectif du sprint

Comprendre en profondeur le dataset proxy **Pump It Up** avant la modélisation :
- Fusion train_values + train_labels
- Visualisations guidant le feature engineering
- Catalogue des anomalies et stratégie d'imbalance
- **Problem Statement** avec contexte **Maroc** + justification du dataset proxy
- AI Context Note pour le rapport académique

**Note :** les graphiques géographiques portent sur la Tanzanie (origine des données) ; la motivation du projet reste le **Maroc**.

**Durée prévue :** 2–3 jours

---

## 2. Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Notebook EDA complet | `notebooks/01_eda.ipynb` | ✅ |
| Merge train + labels | Section 1 du notebook | ✅ |
| Heatmap nullité + tableau | Section 2 | ✅ |
| Distribution cible + stratégie imbalance | Section 3 | ✅ |
| Analyse numérique (histo + boxplots) | Section 4 | ✅ |
| Analyse catégorielle (5 barplots + crosstab basin) | Section 5 | ✅ |
| Carte géographique lat/lon | Section 6 | ✅ |
| Matrice de corrélation | Section 7 | ✅ |
| Analyse temporelle | Section 8 | ✅ |
| Problem Statement | Section 9 | ✅ |
| AI Context Note (MYCIN, rule-based vs ML) | Section 10 | ✅ |
| Justification dataset proxy Maroc | `choix_dataset_maroc.md` | ✅ |
| Catalogue anomalies → actions S2/S3 | Section 11 | ✅ |

---

## 3. Données clés confirmées par l'EDA

| Élément | Valeur |
|---------|--------|
| Shape train unifié | 59 400 × 41 (40 features + status_group) |
| `functional` | 54,3 % |
| `functional needs repair` | 7,3 % |
| `non functional` | 38,4 % |
| GPS invalides (longitude = 0) | 1 812 (3,0 %) |
| `construction_year = 0` | 20 709 (34,9 %) |
| `gps_height < 0` | 1 496 (2,5 %) |
| `amount_tsh = 0` | 41 639 (70,1 %) |
| NaN `scheme_name` | 28 810 (48,5 %) |

---

## 4. Visualisations produites (12+ graphiques)

1. Heatmap de nullité (colonnes les plus affectées)
2. Barplot distribution cible
3. Pie chart distribution cible
4. 6 histogrammes (amount_tsh, gps_height, population, construction_year, lon, lat)
5. 4 boxplots numériques par statut
6. 5 barplots catégoriels (top 10)
7. Barplot empilé statut par basin
8. Scatter map lat/lon coloré par statut
9. Heatmap corrélation numérique
10. Barplot enquêtes par année
11. Barplot année construction moyenne par statut
12. Histogramme âge pompe au survey par statut

Chaque graphique est accompagné d'une **analyse textuelle** dans le notebook.

---

## 5. Stratégie d'imbalance (décision S1 → S3)

| Approche | Usage prévu |
|----------|-------------|
| `class_weight='balanced'` | Logistic Regression, Random Forest |
| Poids de classe / `scale_pos_weight` | XGBoost |
| SMOTE (option) | Si recall « needs repair » < 0,65 |
| Métriques prioritaires | F1-Macro ≥ 0,72 · Recall needs repair ≥ 0,65 |

**Justification :** la classe `needs repair` (7,3 %) est la plus coûteuse à rater métier ; l'accuracy seule est trompeuse (~54 % en prédisant toujours « functional »).

---

## 6. Lien avec le Sprint 2 (déjà réalisé)

L'EDA formalise les anomalies que `src/preprocessing.py` traite déjà :

| Anomalie EDA | Traitement S2 |
|--------------|---------------|
| GPS = 0 | Centroïde basin/région |
| construction_year = 0 | `year_unknown` + imputation médiane basin |
| gps_height < 0 | Imputation médiane basin |
| amount_tsh = 0 | `tsh_is_zero` + imputation |
| funder/installer haute cardinalité | Top-20 + « other » |
| Colonnes redondantes | Suppression (quantity_group, etc.) |

Le S1 complète rétroactivement la **justification visuelle** des choix S2 pour le rapport académique.

---

## 7. Critères d'acceptation

| Critère | Statut |
|---------|--------|
| Notebook `01_eda.ipynb` complet | ✅ |
| 8+ graphiques documentés | ✅ |
| Anomalies cataloguées | ✅ |
| Stratégie imbalance définie | ✅ |
| Problem Statement rédigé | ✅ |
| AI Context Note rédigée | ✅ |

---

## 8. Commande de reproduction

```bash
python scripts/download_data.py
jupyter notebook notebooks/01_eda.ipynb
```

---

## 9. Prochain sprint

**Sprint 3 — Baseline ML** : LR, KNN, Random Forest, XGBoost sur `data/cleaned/train_clean.csv`.

**Documents de cadrage :** [choix_dataset_maroc.md](./choix_dataset_maroc.md) · [guide_dataset_et_wrangling.md](./guide_dataset_et_wrangling.md)

---

*Rapport généré dans le cadre du projet AquaSense AI · EHTP MIG S4 · Dr. Rym Nassih*
