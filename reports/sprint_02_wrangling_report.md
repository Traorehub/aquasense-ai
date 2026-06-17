# Rapport Sprint 2 — Wrangling & Feature Engineering

**Projet :** AquaSense AI · Maintenance prédictive forages & points d'eau · **Contexte Maroc**  
**Sprint :** S2 — Wrangling & Feature Engineering  
**Date :** 2026-06-17  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4

---

## 1. Objectif du sprint

Transformer le dataset proxy **Pump It Up** (59 400 pompes × 40 colonnes) en jeu propre et réutilisable par tous les modèles. Le pipeline est **valide pour le contexte Maroc** (mêmes types de features : âge, GPS, gestion, extraction…) — aucune refonte nécessaire après le cadrage Maroc.

**Livrables produits :**
- `src/preprocessing.py` — pipeline reproductible (`fit` / `transform`)
- `notebooks/02_wrangling.ipynb` — exploration et validation
- `data/cleaned/train_clean.csv` — 59 400 × 37 colonnes
- `data/cleaned/test_clean.csv` — 14 850 × 36 colonnes
- `tests/test_preprocessing.py` — 13 tests unitaires

**Critères d'acceptation atteints :**
- 0 NaN dans les 26 features finales utilisées par les modèles
- 8 nouvelles features créées
- Module importable et testable isolément

---

## 2. Anomalies identifiées dans les données brutes

Avant tout traitement, voici ce que le dataset révèle :

| Anomalie | Volume | % du dataset |
|----------|--------|--------------|
| `longitude = 0` (GPS invalide) | 1 812 | 3,0 % |
| `construction_year = 0` (année inconnue) | 20 709 | 34,9 % |
| `gps_height < 0` (valeur aberrante) | 1 496 | 2,5 % |
| `amount_tsh = 0` | 41 639 | 70,1 % |
| Cardinalité `funder` | 1 896 catégories | — |
| Cardinalité `installer` | 2 145 catégories | — |

Ces chiffres motivent directement chaque décision de nettoyage ci-dessous.

---

## 3. Architecture du pipeline — pourquoi `fit` / `transform` ?

### Choix : classe `PumpPreprocessor` avec pattern sklearn

```python
prep = PumpPreprocessor()
prep.fit(train_values)          # apprend les statistiques sur le TRAIN uniquement
train_clean = prep.transform(train_values)
test_clean = prep.transform(test_values)   # applique les mêmes règles au TEST
```

**Motivation :**
- **Éviter le data leakage** : les médianes, centroïdes GPS et top-20 funder/installer sont calculés uniquement sur le train. Le test ne doit jamais influencer le preprocessing.
- **Reproductibilité** : même pipeline utilisable en entraînement, en inférence MQTT (S6) et en production.
- **Convention sklearn** : compatible avec `Pipeline` et `GridSearchCV` au Sprint 3.

**Alternative rejetée :** fonctions ad hoc sans `fit` → risque d'utiliser des statistiques globales incluant le test set.

---

## 4. Nettoyage des données — choix et motivations

### 4.1 GPS invalides (`longitude = 0`)

| | |
|---|---|
| **Problème** | 1 812 pompes ont `longitude = 0`, ce qui place la pompe en mer (Golfe de Guinée). Ce n'est pas une coordonnée réelle en Tanzanie. |
| **Choix retenu** | Remplacer par le **centroïde du basin** (médiane lat/lon des pompes valides du même basin). Si le basin est inconnu → centroïde de la **région**. Sinon → médiane globale. |
| **Motivation** | Conserver l'information géographique approximative plutôt que supprimer 3 % des lignes. Le basin est un regroupement hydrologique cohérent : une pompe sans GPS précis est probablement quelque part dans ce bassin versant. |
| **Alternative rejetée** | Supprimer les lignes → perte de 1 812 observations. Mettre (0, 0) → fausse la géographie et fausse `dist_to_basin_center`. |

**Seuil retenu :** `|longitude| < 0.01` ou `|latitude| < 0.01` (pas seulement le couple exact `(0, 0)`) car certaines entrées peuvent avoir une latitude valide mais longitude nulle.

---

### 4.2 `construction_year = 0`

| | |
|---|---|
| **Problème** | 34,9 % des pompes ont `construction_year = 0` — code signifiant *« année inconnue »*, pas une pompe construite en l'an 0. |
| **Choix retenu** | 1. Créer un **flag binaire** `year_unknown = 1` si year = 0. 2. Imputer par la **médiane du basin** (fallback : médiane globale ≈ 1998). |
| **Motivation** | L'information *« on ne sait pas quand la pompe a été construite »* est elle-même prédictive : les pompes sans date sont souvent plus anciennes ou mal documentées. Le flag préserve cette signal. L'imputation par basin est plus fine qu'une médiane globale car les régions ont des profils d'installation différents. |
| **Alternative rejetée** | Laisser 0 tel quel → `pump_age = 2024` (absurde). Supprimer les lignes → perte de 35 % du dataset. |

---

### 4.3 `gps_height` négatif

| | |
|---|---|
| **Problème** | 1 496 valeurs négatives (ex. -21 m). L'altitude ne peut pas être négative au-dessus du niveau de référence. |
| **Choix retenu** | Remplacer par `NaN`, puis imputer par la **médiane du basin** (fallback : médiane globale). |
| **Motivation** | Les valeurs négatives sont des erreurs de saisie ou de capteur GPS, pas des altitudes réelles. La médiane régionale est un estimateur robuste aux outliers (contrairement à la moyenne). |
| **Alternative rejetée** | Mettre 0 → confond avec une altitude réelle basse. Clipper à 0 → perd l'information d'altitude relative entre bassins. |

---

### 4.4 `funder` et `installer` — haute cardinalité

| | |
|---|---|
| **Problème** | 1 896 funders et 2 145 installers uniques. Beaucoup n'apparaissent qu'une ou deux fois → bruit pour les modèles. |
| **Choix retenu** | 1. Normaliser : lowercase + strip + `"unknown"` pour les NaN. 2. Garder les **top-20** les plus fréquents. 3. Regrouper le reste en `"other"`. |
| **Motivation** | Réduire la cardinalité de ~2000 à ~21 catégories sans perdre les acteurs majeurs (Gouvernement, Danida, World Vision…). Les funders rares n'ont pas assez d'occurrences pour être appris de façon fiable. Top-20 est un compromis standard dans la littérature Pump It Up. |
| **Alternative rejetée** | One-hot sur 2000 catégories → matrice creuse énorme, overfitting garanti. Supprimer les colonnes → perte d'information sur le financement, fort prédicteur du statut de la pompe. |

---

### 4.5 `amount_tsh = 0` (Total Static Head)

| | |
|---|---|
| **Problème** | 70,1 % des pompes ont `amount_tsh = 0`. Ambiguïté : vrai zéro (pompe gravitaire sans réservoir) ou donnée manquante codée à 0 ? |
| **Choix retenu** | 1. Créer **`tsh_is_zero = 1`** avant toute modification. 2. Imputer les zéros par la **médiane des valeurs strictement positives**. |
| **Motivation** | Le flag distingue les deux cas sémantiques. Une pompe gravitaire (*gravity-fed*) a légitimement TSH = 0 — c'est une information métier. Imputer la médiane (~25 m) pour les modèles qui ne gèrent pas bien le 0 massif, tout en laissant le flag porter le signal. |
| **Alternative rejetée** | Traiter tous les 0 comme manquants sans flag → perte de l'information gravitaire. Laisser 70 % de zéros → biaise les modèles linéaires et les distances (KNN). |

---

### 4.6 Suppression de colonnes redondantes

| Colonne supprimée | Raison |
|-------------------|--------|
| `quantity_group` | 100 % identique à `quantity` |
| `extraction_type_group` | 95,8 % identique à `extraction_type` |
| `waterpoint_type_group` | 89,7 % identique à `waterpoint_type` |
| `quality_group` | Quasi-duplicata de `water_quality` |
| `region_code`, `district_code` | Encodages numériques de `region` / districts — redondants avec les colonnes texte |
| `recorded_by` | Quasi-constant ("GeoData Institute Ltd") |
| `scheme_name` | >90 % vide |
| `wpt_name`, `subvillage`, `ward`, `lga` | Cardinalité extrême (milliers de valeurs uniques), identifiants locaux non généralisables |

**Motivation globale :** réduire la dimensionnalité, éliminer le multicollinearity (problème pour LR) et éviter que le modèle mémorise des identifiants locaux (= overfitting).

**Colonnes conservées volontairement :**
- `source` vs `source_type` (62 % identiques) → conservées car `source_class` apporte une granularité différente
- `payment` vs `payment_type` (58 % identiques) → conservées, encodage différencié au Sprint 3

---

## 5. Feature Engineering — choix et motivations

### 5.1 Features temporelles

| Feature | Formule | Motivation |
|---------|---------|------------|
| `year_recorded` | extraite de `date_recorded` | Capture l'évolution des enquêtes dans le temps (2011–2013) |
| `month_recorded` | extraite de `date_recorded` | Saisonnalité : période sèche (juin–sept) — pertinente aussi au **Maroc** |
| `day_of_year` | extraite de `date_recorded` | Granularité saisonnière pour les modèles sensibles au cycle annuel |

**Pourquoi décomposer la date ?** Les modèles tree-based ne parsent pas nativement une string `"2013-03-15"`. La décomposition en entiers exploitables est standard.

---

### 5.2 `pump_age` et `age_at_recording`

| Feature | Formule | Motivation |
|---------|---------|------------|
| `pump_age` | `2024 - construction_year` | Âge de la pompe *aujourd'hui* — proxy direct de l'usure |
| `age_at_recording` | `year_recorded - construction_year` | Âge *au moment du survey* — plus précis historiquement |

**Pourquoi les deux ?**
- `pump_age` est utile pour le déploiement (inférence sur pompes actuelles).
- `age_at_recording` est plus correct pour l'entraînement car il correspond au moment où le label a été observé — évite un léger anachronisme.

**Motivation métier :** une pompe de 30 ans a statistiquement plus de chances d'être `non functional` ou `needs repair` qu'une pompe de 5 ans. C'est l'une des features les plus prédictives du dataset.

---

### 5.3 `dist_to_basin_center`

| | |
|---|---|
| **Formule** | Distance Haversine (km) entre la pompe et le centroïde de son basin |
| **Motivation** | Proxy d'**isolement géographique**. Les pompes éloignées du centre du bassin versant sont souvent plus difficiles à maintenir (accès, logistique). Distance moyenne observée : **128,5 km**. |
| **Alternative rejetée** | Distance euclidienne en degrés lat/lon → fausse aux latitudes tropicale (1° lon ≠ 1° lat en km). Haversine est géographiquement correcte. |

---

### 5.4 Flags binaires (`year_unknown`, `tsh_is_zero`)

| Feature | Motivation |
|---------|------------|
| `year_unknown` | *« Donnée manquante informative »* — le fait qu'on ne connaisse pas l'année est corrélé au statut de la pompe |
| `tsh_is_zero` | Distingue pompe gravitaire (TSH légitime = 0) de donnée manquante imputée |

**Principe :** ne jamais imputer silencieusement — toujours laisser une trace binaire de l'anomalie originale.

---

## 6. Encodage catégoriel — stratégie différenciée

Le pipeline `build_encoder()` propose 3 configurations selon le modèle :

| Type de feature | Colonnes | Encodage | Modèles |
|-----------------|----------|----------|---------|
| Faible cardinalité | `basin`, `water_quality`, `payment`, `source_type`, `management` | **OneHotEncoder** | Tous |
| Haute cardinalité | `funder`, `installer`, `extraction_type`, `region` | **OrdinalEncoder** | RF, XGBoost |
| Numériques | 15 features + 2 binaires | Variable selon modèle | Voir ci-dessous |

**Normalisation numérique différenciée :**

| Scaler | Modèles | Motivation |
|--------|---------|------------|
| `StandardScaler` (μ=0, σ=1) | LR, KNN | Sensibles à l'échelle des features |
| `none` (brut) | RF, XGBoost | Tree-based : invariant à l'échelle |
| `MinMaxScaler` ([0,1]) | MLP / Deep Learning (S4) | Réseaux de neurones convergent mieux avec des entrées bornées |

**Motivation OneHot vs Ordinal :**
- OneHot pour faible cardinalité (5–15 catégories) → pas de fausse relation d'ordre.
- Ordinal pour haute cardinalité déjà réduite à ~21 → évite l'explosion dimensionnelle du one-hot (21 × 4 = 84 colonnes supplémentaires).

**Note :** l'encodage n'est **pas** appliqué dans les CSV sauvegardés — il reste dans `build_encoder()` pour être branché au moment de l'entraînement (Sprint 3). Les CSV conservent les catégories en texte pour la flexibilité.

---

## 7. Ordre des opérations dans le pipeline

```
Données brutes
    │
    ▼
1. _fix_gps              ← avant tout calcul géographique
    │
    ▼
2. _fix_construction_year ← crée year_unknown, puis impute
    │
    ▼
3. _fix_gps_height
    │
    ▼
4. _fix_funder_installer
    │
    ▼
5. _fix_amount_tsh        ← crée tsh_is_zero, puis impute
    │
    ▼
6. _engineer_features     ← pump_age, temporal, dist_to_basin_center
    │
    ▼
7. _encode_binary         ← public_meeting, permit → 0/1
    │
    ▼
8. _drop_columns          ← en dernier pour ne pas supprimer des colonnes utiles au calcul
```

**Motivation de l'ordre :** GPS corrigé *avant* le calcul de `dist_to_basin_center`. `year_unknown` créé *avant* l'imputation de `construction_year`. Flags créés *avant* l'imputation des valeurs qu'ils documentent.

---

## 8. Résultats finaux

| Métrique | Valeur |
|----------|--------|
| Lignes train | 59 400 |
| Colonnes train (avec `status_group`) | 37 |
| Colonnes test | 36 |
| Features modèle | 26 |
| NaN restants | **0** |
| Tests unitaires | **13 / 13 passants** |
| `year_unknown = 1` | 20 709 pompes (34,9 %) |
| `tsh_is_zero = 1` | 41 639 pompes (70,1 %) |
| `pump_age` moyen | 26,6 ans |
| `dist_to_basin_center` moyen | 128,5 km |

---

## 9. Limites connues et pistes d'amélioration

| Limite | Impact | Piste S3+ |
|--------|--------|-----------|
| Imputation par médiane basin ignore la variance | Légère sous-estimation de l'incertitude | Tester KNN imputer ou MICE |
| Top-20 funder/installer arbitraire | Catégories 21–50 rares perdues | GridSearch sur `top_n` (10, 20, 30) |
| `pump_age` avec `reference_year=2024` fixe | Décalage si inférence en 2025+ | Paramétrer `reference_year` dynamiquement |
| OrdinalEncoder sur haute cardinalité | Fausses relations d'ordre pour LR | Target encoding au Sprint 3 si LR underperforme |
| Pas de gestion explicite de l'imbalance ici | 54% / 7% / 39% | `class_weight`, SMOTE au Sprint 3 |

---

## 10. Fichiers produits

```
src/preprocessing.py          ← Pipeline principal
notebooks/02_wrangling.ipynb  ← Notebook de validation
data/cleaned/train_clean.csv  ← Dataset train nettoyé
data/cleaned/test_clean.csv   ← Dataset test nettoyé
tests/test_preprocessing.py   ← 13 tests (GPS, year, TSH, features…)
reports/sprint_02_wrangling_report.md  ← Ce rapport
```

**Commande de reproduction :**
```bash
python src/preprocessing.py
pytest tests/test_preprocessing.py -v
```

---

## 11. Prochain sprint

**Sprint 3 — Baseline ML** : entraîner LR, KNN, Random Forest et XGBoost. Pipeline S2 **conservé** — valide pour le contexte Maroc.

**Cadrage :** [choix_dataset_maroc.md](./choix_dataset_maroc.md)

---

*Rapport généré dans le cadre du projet AquaSense AI · EHTP MIG S4 · Dr. Rym Nassih*
