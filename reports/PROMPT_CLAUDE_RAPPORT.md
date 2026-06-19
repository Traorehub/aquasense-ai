# PROMPT À COPIER-COLLER DANS CLAUDE

---

Tu es un assistant mise en forme de rapport académique. Je t'envoie un zip contenant :

- `AquaSense_AI_Report.md` : rapport complet (~1145 lignes), contenu FINAL à ne pas réécrire
- `images/` : captures et figures référencées dans le markdown
- ce fichier de consignes

## Ta mission (UNE SEULE)

Produire un **fichier LaTeX `main.tex` compilable sur Overleaf** (pdfLaTeX) OU un **document Word (.docx)** avec **mise en page professionnelle** et **couleurs**, à partir du markdown **sans changer le fond** (chiffres, conclusions, structure des chapitres).

**Interdit :**
- Réécrire le contenu scientifique
- Ajouter des emojis, watermarks IA, tirets longs décoratifs
- Inventer des résultats ou modifier les métriques (F1-Macro 0,679, recall 0,685, 37/37 pytest, etc.)
- Supprimer des sections

**Autorisé :**
- Mise en page, couleurs, typographie, page de garde, en-têtes/pieds de page
- Conversion Markdown → LaTeX propre
- Corriger uniquement la forme (tableaux, figures, sauts de page)

---

## Charte couleurs (thème EHTP / rapport ingénieur — eau & géomatique)

| Rôle | Code | Usage |
|------|------|--------|
| **Primaire** | `#1B4F72` | Titres chapitres, bandeau page de garde, numéros de section |
| **Secondaire** | `#2874A6` | Sous-titres, liens, encadrés |
| **Accent** | `#17A589` | Lignes de séparation, puces, highlights métriques clés |
| **Texte** | `#2C3E50` | Corps de texte |
| **Fond clair** | `#F4F7F9` | Encadrés « résultat », résumé exécutif |
| **Tableau header** | `#D6EAF8` | Fond en-têtes de tableaux |
| **Alerte / critique** | `#C0392B` | Classe « needs repair » uniquement (avec parcimonie) |

Police recommandée : **Latin Modern** ou **Helvetica Neue** (LaTeX : `lmodern` + `helvet` pour sans-serif titres).

---

## Page de garde (obligatoire)

```
École Hassania des Travaux Publics (EHTP)
Projet Machine Learning

AquaSense AI
Maintenance prédictive des forages et points d'eau
en contexte marocain

Rapport de projet

Équipe :
- TRAORE Fanogo Mohamed
- NADAHE Mohamed

Encadrement : Dr. Rym Nassih

Juin 2026
```

Bandeau supérieur couleur primaire `#1B4F72`, titre en blanc, sous-titre accent `#17A589`.

---

## Structure du document (respecter l'ordre du .md)

1. Page de garde
2. Résumé exécutif (+ mots-clés)
3. Table des matières
4. Chapitres 1 à 16 (Introduction → Références)
5. Pas d'annexe inventée

Chapitre 2 (métriques) et §2.10 (origine des seuils 0,72 / 0,65) : **conserver intégralement**.

---

## Figures

Chemins dans le markdown :
- `sprint_03_*.png`, `sprint_04_*.png` → dossier `images/`
- `image/Capture...` → dossier `images/` (renommer en ASCII si besoin : `fig_dashboard_01.png`, etc.)

Chaque figure : légende + numérotation (Figure 1, Figure 2…).

---

## Format de sortie attendu

**Option A (préférée) :** un zip avec :
```
main.tex
images/ (toutes les png)
```

Compatible Overleaf, compilateur **pdfLaTeX**, packages : `babel[french]`, `graphicx`, `grffile`, `hyperref`, `booktabs`, `longtable`, `xcolor`, `geometry`, `titlesec`.

**Option B :** fichier `.docx` avec styles titres 1/2/3 et couleurs ci-dessus.

---

## Rappels projet (ne pas contredire)

- Dataset : Pump It Up (Tanzanie), proxy pour le Maroc
- Champion production alertes : XGBoost SMOTE + seuil 0,17 (recall 0,685)
- Champion F1 analytics : Soft Voting RF+XGB (F1-Macro 0,679)
- DL max F1 : 0,541 — non retenu pour production
- 37 tests pytest, 100 % OK
- Pas de norme ONEE ni loi IA imposant 0,72 / 0,65 : critères projet S1/S3/S5

---

## Livrable

Réponds avec le fichier prêt à compiler. Si LaTeX, donne `main.tex` complet + liste des images. Signale toute image manquante dans le zip.
