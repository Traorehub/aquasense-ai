# AquaSense AI — Présentation

**Maintenance prédictive des forages & points d'eau · Maroc**  
TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4 · Dr. Rym Nassih

---

## Slide 1 — Titre

# AquaSense AI
### Maintenance prédictive des forages et points d'eau
**Contexte Maroc · Pipeline ML + IoT simulé + Dashboard**

TRAORE Fanogo Mohamed · NADAHE Mohamed  
EHTP — Master Ingénierie Géomatique S4 · Juin 2026

---

## Slide 2 — Problématique

- Stress hydrique & sécheresse au **Maroc**
- Milliers de forages en zones **rurales**
- Inspections terrain **coûteuses** et **tardives**
- Pannes = privation d'eau pour des **douars entiers**

> *Comment prioriser les réparations avant la panne ?*

---

## Slide 3 — Objectif du projet

Classifier l'état d'un point d'eau en **3 classes** :

| Classe | Signification |
|--------|---------------|
| ✅ Functional | Opérationnel |
| ⚠️ Needs repair | Dégradé — intervention requise |
| ❌ Non functional | Hors service |

**Priorité métier :** détecter *needs repair* (recall ≥ 65 %)

---

## Slide 4 — Choix du dataset

| | Maroc (ONEE/ABH) | Pump It Up (Tanzanie) |
|---|---|---|
| Volume labellisé | Fragmenté | **59 400** |
| Accès | Institutionnel | **Open data** |
| Labels 3 classes | Rare | ✅ |

**Décision :** proxy Tanzanie + cadrage Maroc + limites documentées

---

## Slide 5 — Pipeline global

```
Données → Preprocessing → ML/DL → Champion → MQTT → Dashboard
```

- **S0–S2 :** Setup, EDA, 26 features
- **S3–S5 :** ML classique, DL, arbitrage
- **S6–S8 :** MQTT, dashboard, tests

---

## Slide 6 — Feature engineering (S2)

`PumpPreprocessor` — 8 features dérivées :
- `pump_age`, `dist_to_basin_center`
- GPS anomaly flag, ratios population
- Encodage catégoriel (40 → 26 colonnes)

**59 400 pompes** · split 80/20 stratifié

---

## Slide 7 — Résultats ML (S3)

| Modèle | F1-Macro | Recall needs repair |
|--------|----------|---------------------|
| Random Forest | 0,666 | 0,484 |
| XGBoost tuned | 0,657 | 0,642 |
| **XGB SMOTE+seuil** | 0,630 | **0,685** ✅ |

Recall boost : SMOTE + seuil calibré 0,17

---

## Slide 8 — ML vs Deep Learning (S4)

| Type | Meilleur F1 |
|------|-------------|
| **ML** Voting RF+XGB | **0,679** |
| DL MLP tuned | 0,541 |

**Verdict :** le DL ne bat pas le ML sur données tabulaires  
→ preuve expérimentale rigoureuse, pas un échec

---

## Slide 9 — Modèles champions (S5)

| Usage | Modèle | Métrique |
|-------|--------|----------|
| **Alertes production** | XGB SMOTE+seuil | Recall **0,685** |
| Analytics F1 | Voting RF+XGB | F1 **0,679** |

Fichier déployé : `champion_production_v1.joblib`

---

## Slide 10 — Simulation IoT MQTT (S6)

```
Simulateur (50 pompes) → Mosquitto → Consumer ML → SQLite
```

- 3 scénarios : healthy · degradation · failure
- Saison sèche juin–sept (Maroc)
- Latence inférence : **22–70 ms**

---

## Slide 11 — Dashboard Streamlit (S7)

5 pages · auto-refresh 10 s :
1. Vue d'ensemble + **carte Maroc**
2. Alertes maintenance
3. Détail pompe (télémétrie + prédiction)
4. Comparaison modèles
5. À propos

![Dashboard](image/Capture%20d'écran%202026-06-19%20145330.png)

---

## Slide 12 — Tests & validation (S8)

**37 tests pytest · 100 % réussite**

- 35 tests offline (preprocessing, consumer, simulateur, dashboard)
- 2 tests intégration MQTT live

Scénarios : 50 pompes, dégradation 14 j, panne < 5 s

---

## Slide 13 — Limites & transfert Maroc

1. Modèle entraîné sur **Tanzanie** — ré-entraînement Maroc nécessaire
2. Pas de piézométrie / salinité (enjeux marocains)
3. IoT **simulé** — pas de capteurs réels
4. Carte dashboard = **positions démo** Maroc

---

## Slide 14 — Perspectives

- Partenariat **ONEE / ABH** / SNIE
- Capteurs réels : débit, pression, conductivité
- Fine-tuning sur données nationales
- Pilote terrain dans un bassin hydraulique

---

## Slide 15 — Conclusion

✅ Pipeline complet A → Z démontré  
✅ Recall maintenance **0,685** (cible atteinte)  
✅ ML > DL sur ce problème tabulaire  
✅ MQTT + dashboard opérationnels  
✅ 37/37 tests validés  

> *Prêt pour un déploiement pilote dès l'accès aux données nationales.*

**Merci — Questions ?**

---

*Export PDF : ouvrir ce fichier dans VS Code + extension Marp, ou copier dans PowerPoint / Google Slides.*
