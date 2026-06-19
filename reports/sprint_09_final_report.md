# Rapport Sprint 9 — Rapport académique & livrables finaux

**Projet :** AquaSense AI · Maintenance prédictive forages & points d'eau · **Contexte Maroc**  
**Sprint :** S9 — Documentation finale, rapport PDF, présentation  
**Date :** 2026-06-19  
**Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4  
**Statut :** 🟡 **En cours** (rapport rédigé — export PDF à finaliser)

---

## 1. Objectif

Consolider les livrables académiques du projet AquaSense AI :

1. Rapport académique synthétisant S0–S8
2. Section limites transfert Maroc
3. Diapositives de présentation (10–15 slides)
4. Préparation tag `v1.0.0`

---

## 2. Livrables produits

| # | Tâche backlog | Fichier | Statut |
|---|---------------|---------|--------|
| S9-03 | Rapport académique | `reports/AquaSense_AI_Report.md` | ✅ Rédigé |
| S9-05 | Présentation slides | `reports/presentation.md` | ✅ Rédigé (15 slides) |
| S9-04 | Model Card | `reports/model_card.md` | ✅ (S5) |
| S9-03 | Export PDF | `reports/AquaSense_AI_Report.pdf` | ⬜ À exporter |
| S9-05 | Export PDF slides | `reports/presentation.pdf` | ⬜ À exporter |
| S9-06 | Tag Git `v1.0.0` | — | ⬜ À faire |
| S9-07 | Test reproductibilité clone frais | — | ⬜ À valider |

---

## 3. Contenu du rapport académique

Le fichier `AquaSense_AI_Report.md` couvre :

| Section | Source sprint |
|---------|---------------|
| Introduction & problématique Maroc | S1, choix_dataset_maroc |
| Choix dataset proxy | choix_dataset_maroc.md |
| Architecture A → Z | PROJECT_OVERVIEW |
| EDA | S1 |
| Wrangling & features | S2 |
| ML classique + recall boost | S3 |
| Deep Learning & verdict | S4 |
| Arbitrage champions | S5, model_card |
| Simulation MQTT | S6 |
| Dashboard Streamlit | S7 |
| Tests pytest 37/37 | S8 |
| Limites & perspectives Maroc | choix_dataset_maroc §6–7 |
| Annexes & reproduction | README |

---

## 4. Export PDF — instructions

### Option A — VS Code / Cursor (recommandé)

1. Installer l'extension **Markdown PDF** ou **Marp for VS Code**
2. Ouvrir `reports/AquaSense_AI_Report.md`
3. Clic droit → **Markdown PDF: Export (pdf)**
4. Enregistrer sous `reports/AquaSense_AI_Report.pdf`

Pour les slides : ouvrir `reports/presentation.md` avec **Marp** → Export PDF.

### Option B — Pandoc (si installé)

```powershell
cd reports
pandoc AquaSense_AI_Report.md -o AquaSense_AI_Report.pdf --pdf-engine=xelatex -V geometry:margin=2.5cm -V lang=fr
```

### Option C — Word / Google Docs

1. Copier le contenu de `AquaSense_AI_Report.md` dans Word ou Google Docs
2. Ajuster titres, table des matières automatique
3. Exporter en PDF

### Option C — Impression navigateur

1. Prévisualiser le markdown (extension Markdown Preview)
2. Imprimer → Enregistrer en PDF

---

## 5. Critères d'acceptation S9

| Critère | Statut |
|---------|--------|
| Rapport PDF avec section limites Maroc | 🟡 MD prêt, PDF à exporter |
| Présentation 10–15 slides | ✅ 15 slides (`presentation.md`) |
| Model Card | ✅ |
| Tous livrables dans `/reports/` | ✅ |
| Tag `v1.0.0` | ⬜ |
| Reproductibilité clone frais < 10 min | ⬜ |

---

## 6. Prochaines actions

1. **Exporter** `AquaSense_AI_Report.pdf` et `presentation.pdf`
2. **Relire** le rapport (orthographe, noms, captures)
3. **Tagger** `git tag v1.0.0` sur le commit de soumission
4. **Vérifier** reproductibilité depuis un clone frais

---

*Rapport Sprint 9 · EHTP MIG S4 · 2026-06-19*
