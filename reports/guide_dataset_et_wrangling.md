# Guide du dataset & du wrangling — AquaSense AI

> **Pour qui ?** Lecture rapide si tu n'es pas hydraulicien.  
> **Cadrage :** problème **Maroc** · données d'entraînement **Pump It Up** (proxy)  
> **Voir aussi :** [choix_dataset_maroc.md](./choix_dataset_maroc.md)  
> **Objectif :** comprendre ce qu'il y a dans les données, ce qu'on nettoie, et ce que le modèle essaie de prédire.

---

## 1. Le problème en une phrase

Au **Maroc**, des milliers de **forages et points d'eau** desservent douars et zones rurales. Sous stress hydrique, une pompe en panne ou dégradée peut priver des centaines de personnes d'eau potable. On veut **prédire l'état d'une installation** à partir d'informations d'enquête pour **prioriser les réparations**.

Le pipeline est **entraîné** sur le benchmark **Pump It Up** (Tanzanie) — structure analogue, données ouvertes. Voir [choix_dataset_maroc.md](./choix_dataset_maroc.md).

---

## 2. Ce qu'on prédit (la cible)

Chaque pompe reçoit une étiquette `status_group` :

| Classe | Signification simple | ~Part du dataset |
|--------|----------------------|------------------|
| `functional` | La pompe marche normalement | 54 % |
| `functional needs repair` | Elle marche encore, mais il faut intervenir bientôt | **7 %** |
| `non functional` | Elle ne marche plus | 39 % |

**Pourquoi c'est difficile :** la classe la plus importante métier (`needs repair`) est la plus rare. Un modèle qui dit toujours « ça marche » aurait ~54 % de précision mais raterait toutes les pompes à réparer.

**Objectifs du modèle :**
- F1-Macro ≥ **0,72** (performance équilibrée sur les 3 classes)
- Recall `needs repair` ≥ **0,65** (ne pas rater les pompes dégradées)

---

## 3. D'où viennent les données ?

- **Problème cible :** forages & points d'eau — **contexte Maroc**
- **Dataset d'entraînement :** [Pump It Up — DrivenData](https://www.drivendata.org/competitions/7/) (Tanzanie, 2011–2013)
- **Rôle du jeu :** proxy reproductible — pas de dataset Maroc ouvert équivalent (59k lignes labellisées)
- **Collecte :** Taarifa + Tanzanian Ministry of Water (même type d'enquêtes terrain qu'au Maroc)
- **Fichiers :**
  - `train_values.csv` — 59 400 pompes × 40 colonnes
  - `train_labels.csv` — état `status_group`
  - `test_values.csv` — 14 850 pompes sans label

Ce ne sont **pas** des mesures de pression/vibration en direct. Ce sont des **fiches d'enquête** : localisation, type de pompe, gestion, financement, âge…

---

## 4. Les 40 colonnes brutes — regroupées par thème

### Identité & admin
| Colonne | En clair |
|---------|----------|
| `id` | Identifiant unique de la pompe |
| `wpt_name`, `scheme_name` | Noms locaux du point d'eau / du projet |
| `recorded_by` | Qui a fait l'enquête |

### Géographie
| Colonne | En clair |
|---------|----------|
| `latitude`, `longitude` | Position GPS |
| `gps_height` | Altitude (m) |
| `basin` | Bassin versant (ex. Lake Victoria, Rufiji…) |
| `region`, `lga`, `ward`, `subvillage` | Découpage administratif |
| `region_code`, `district_code` | Codes numériques des régions |

### Technique de la pompe
| Colonne | En clair |
|---------|----------|
| `amount_tsh` | **TSH** = hauteur d'eau disponible pour alimenter la pompe (m). Zéro peut signifier pompe gravitaire ou donnée manquante |
| `extraction_type` | Mode d'extraction (handpump, gravity, motorised…) |
| `extraction_type_group` | Regroupement simplifié (quasi-doublon) |
| `waterpoint_type` | Type de point d'eau (borehole, spring…) |
| `waterpoint_type_group` | Regroupement (quasi-doublon) |
| `construction_year` | Année d'installation. **0 = « on ne sait pas »** |
| `quantity` | Suffisance d'eau perçue (enough, insufficient…) |
| `quantity_group` | Doublon de `quantity` |

### Eau & qualité
| Colonne | En clair |
|---------|----------|
| `source`, `source_type`, `source_class` | D'où vient l'eau (borehole, spring…) |
| `water_quality` | Qualité perçue (soft, salty, milky…) |
| `quality_group` | Doublon de `water_quality` |

### Gestion & financement
| Colonne | En clair |
|---------|----------|
| `funder` | Qui a financé (gouvernement, ONG…) |
| `installer` | Qui a installé |
| `management` | Qui gère au quotidien (vwc, wug…) |
| `management_group` | Regroupement |
| `payment`, `payment_type` | Les usagers paient-ils ? Comment ? |
| `permit` | Permis d'exploitation ? |
| `public_meeting` | Réunion publique tenue ? |

### Contexte local
| Colonne | En clair |
|---------|----------|
| `population` | Population desservie (estimation) |
| `num_private` | Nombre de points privés liés |
| `date_recorded` | Date de l'enquête |

---

## 5. Anomalies connues (pourquoi le wrangling est indispensable)

| Problème | Volume ~ | Ce que ça veut dire |
|----------|----------|---------------------|
| `longitude = 0` ou `latitude = 0` | 3 % | GPS invalide (coordonnée aberrante dans le jeu) |
| `construction_year = 0` | 35 % | Année inconnue, pas « construite en l'an 0 » |
| `gps_height < 0` | 2,5 % | Erreur de saisie |
| `amount_tsh = 0` | 70 % | Ambigu : vraie pompe gravitaire ou donnée manquante |
| `scheme_name` vide | 48 % | Colonne inutilisable |
| `funder` / `installer` | ~2 000 valeurs uniques | Trop de catégories rares pour le modèle |

Sans nettoyage, le modèle apprendrait du **bruit** (coordonnées fausses, âges absurdes, etc.).

---

## 6. Le wrangling — est-ce cohérent ?

**Oui, globalement.** Le pipeline `src/preprocessing.py` suit une logique saine :

```
Données brutes
  → corriger GPS
  → traiter année inconnue (flag + imputation)
  → corriger altitude négative
  → réduire funder/installer (top 20)
  → traiter TSH = 0 (flag + imputation)
  → créer nouvelles features (âge, date, distance)
  → encoder oui/non (permit, public_meeting)
  → supprimer colonnes redondantes
  → CSV nettoyé
```

### Principes respectés

| Principe | Comment c'est fait |
|----------|-------------------|
| Pas de fuite de données | `fit()` sur le **train** uniquement ; le test reçoit les mêmes règles |
| Traçabilité des anomalies | Flags `year_unknown` et `tsh_is_zero` avant imputation |
| Ordre logique | GPS corrigé **avant** le calcul de distance au centre du basin |
| Tests automatisés | 13 tests pytest (GPS, année, TSH, features…) |
| 0 NaN en sortie | Sur les 26 features utilisées par le modèle |

### Choix de nettoyage — résumé

| Anomalie | Action |
|----------|--------|
| GPS invalide | Remplacé par le centre du `basin` (ou `region`) |
| `construction_year = 0` | Flag `year_unknown=1` + médiane du basin |
| `gps_height < 0` | Médiane du basin |
| `amount_tsh = 0` | Flag `tsh_is_zero=1` + médiane des valeurs > 0 |
| `funder` / `installer` | Top 20 + catégorie `other` |
| Colonnes doublons | Supprimées (`quantity_group`, `extraction_type_group`, etc.) |

### Point d'attention (mineur)

Le CSV nettoyé garde quelques colonnes **hors des 26 features modèle** (`quantity`, `source`, `waterpoint_type`, `payment_type`, `management_group`). C'est volontaire pour garder de la flexibilité, mais le modèle S3 n'utilisera que les 26 colonnes listées dans `get_feature_columns()`.

---

## 7. Les 26 features que le modèle utilisera

### Numériques & dérivées (15)
| Feature | Logique métier |
|---------|----------------|
| `amount_tsh` | Ressource en eau disponible pour la pompe |
| `gps_height` | Altitude — influence technique et accessibilité |
| `longitude`, `latitude` | Localisation — entretien et climat varient par zone |
| `population` | Plus d'usagers = plus d'usure |
| `construction_year` | Année d'installation (imputée si inconnue) |
| `pump_age` | Âge aujourd'hui → proxy d'usure |
| `age_at_recording` | Âge au moment de l'enquête (plus précis pour l'entraînement) |
| `year_recorded`, `month_recorded`, `day_of_year` | Quand l'enquête a eu lieu (saison, période) |
| `dist_to_basin_center` | Éloignement du centre du bassin → isolement, logistique |
| `year_unknown` | « On ne connaît pas l'année » — signal en soi |
| `tsh_is_zero` | Pompe gravitaire ou donnée manquante ? |
| `num_private` | Contexte du village |

### Catégorielles faible cardinalité (5) — one-hot au S3
`basin`, `water_quality`, `payment`, `source_type`, `management`

### Catégorielles haute cardinalité (4) — encodage ordinal au S3
`funder`, `installer`, `extraction_type`, `region`

### Binaires (2)
`public_meeting`, `permit`

---

## 8. La logique métier — sans être hydraulicien

Imagine chaque pompe comme une **voiture** :

| Idée voiture | Équivalent pompe |
|--------------|------------------|
| Année de mise en service | `construction_year` / `pump_age` |
| Kilométrage / usure | Âge + population desservie |
| Marque et garage | `installer`, `funder` |
| Qui paie l'entretien | `payment`, `management` |
| Où elle est garée | GPS, `basin`, `region` |
| Type de moteur | `extraction_type` (manuelle, gravitaire, motorisée) |
| État constaté | **`status_group`** (cible) |

**Ce que le modèle apprend :** des **combinaisons de signaux** du type :
- pompe vieille + management faible + bassin isolé → plus souvent `non functional`
- financement solide + type d'extraction adapté + entretien payant → plus souvent `functional`
- signaux intermédiaires → `needs repair`

On ne simule pas la physique de l'eau. On utilise des **proxies observables sur le terrain** que les enquêteurs ont notés.

---

## 9. Pipeline global du projet

```
Contexte Maroc — maintenance forages & points d'eau
        ↓
Dataset proxy Pump It Up (enquêtes terrain, 2011–2013)
        ↓
   EDA (S1) — comprendre les données
        ↓
   Wrangling (S2) — preprocessing.py
        ↓
   Modèle ML/DL (S3–S5) — prédire status_group
        ↓
   Simulation MQTT + Dashboard Maroc (S6–S7)
        ↓
   Rapport S9 — limites transfert Maroc ↔ proxy
```

La partie MQTT (S6) **simulera** pression/vibration/flow pour la démo. L'entraînement repose sur les **features d'enquête**. Les enjeux nappe/salinité (spécifiques Maroc) sont hors scope de ce dataset — voir [choix_dataset_maroc.md](./choix_dataset_maroc.md).

---

## 10. Commandes utiles

```bash
# Télécharger les données
python scripts/download_data.py

# Explorer visuellement
jupyter notebook notebooks/01_eda.ipynb

# Regénérer les données nettoyées
python src/preprocessing.py

# Vérifier le pipeline
pytest tests/test_preprocessing.py -v
```

---

*AquaSense AI · EHTP MIG S4 · Dernière mise à jour : 2026-06-17*
