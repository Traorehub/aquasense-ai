# Contexte Maroc & choix du dataset — AquaSense AI

> **Document de référence** — À lire en premier pour comprendre le cadrage du projet.  
> **Équipe :** TRAORE Fanogo Mohamed · NADAHE Mohamed · EHTP MIG S4  
> **Dernière mise à jour :** 2026-06-17

---

## 1. Problème réel visé (Maroc)

**AquaSense AI** vise la **maintenance prédictive des forages et points d'eau** en contexte marocain :

- Stress hydrique et sécheresse récurrente
- Vieillissement des installations en zones rurales et agricoles
- Coût élevé des inspections terrain et des réparations tardives
- Besoin de **prioriser** les interventions sur les pompes « à risque »

**Question métier :** *Cette installation (forage + pompe + contexte local) est-elle fonctionnelle, dégradée, ou hors service ?*

Ce n'est **pas** (dans ce projet) une modélisation hydrogéologique du niveau de nappe — c'est la **prédiction de l'état opérationnel** d'un point d'eau à partir de caractéristiques observables.

---

## 2. Pourquoi le dataset est en Tanzanie

| Critère | Données Maroc (ONEE, ABH) | Pump It Up (Tanzanie) |
|---------|---------------------------|------------------------|
| Volume labellisé | Fragmenté, sur demande | **59 400** pompes |
| Accès | Institutionnel, souvent payant | **Open data** (DrivenData) |
| Label `functional` / `needs repair` / `non functional` | Rarement public | ✅ Inclus |
| Reproductibilité académique | Difficile | ✅ Script `download_data.py` |
| Structure (forage, pompe, gestion, GPS) | Analogue | ✅ Compatible |

**Décision retenue :** entraîner et valider le pipeline ML sur **Pump It Up**, en motivant le projet par le **contexte marocain** et en documentant les **limites de transfert** dans le rapport final (S9).

---

## 3. Ce qui ne change pas (paradigme & technique)

| Élément | Statut |
|---------|--------|
| Paradigme : classification prédictive 3 classes | ✅ Conservé |
| Cible `status_group` | ✅ Conservé |
| Pipeline S2 `preprocessing.py` | ✅ Conservé — features universelles |
| Métriques F1-Macro ≥ 0,72 · Recall needs repair ≥ 0,65 | ✅ Conservé |
| Simulation MQTT + dashboard | ✅ Conservé — démo opérationnelle |

Les sprints S0–S2 **ne sont pas à refaire**. Le wrangling reste valide : âge, GPS, gestion, financement, type d'extraction sont pertinents au Maroc comme en Tanzanie.

---

## 4. Ce qui change (cadrage & livrables)

| Zone | Adaptation |
|------|------------|
| Problem Statement | Contexte **Maroc** en introduction |
| Rapport S9 | Section « Choix méthodologique & limites » |
| Dashboard S7 | Présentation orientée **Maroc** (carte, KPIs, scénarios) |
| Simulation S6 | Saison sèche **juin–sept** (cohérent Maroc) |
| EDA S1 | Données Tanzanie + note « proxy dataset » |

---

## 5. Analogie Maroc ↔ dataset Tanzanie

| Concept | Maroc | Pump It Up |
|---------|-------|------------|
| Point d'eau rural | Douar, commune rurale | Village tanzanien |
| Forage / source | Nappe, borehole ONEE/ABH | `waterpoint_type`, `source_type` |
| Pompe | Manuelle, motorisée, solaire | `extraction_type` |
| Gestion | Association, commune, ABH | `management`, `payment` |
| Financement | État, coopérative, ONG | `funder`, `installer` |
| Usure | Âge, population desservie | `pump_age`, `population` |

---

## 6. Limites à assumer dans le rapport final

1. **Géographie :** modèle entraîné sur coordonnées tanzaniennes — transfert Maroc nécessite ré-entraînement ou fine-tuning.
2. **Nappe vs pompe :** le dataset ne mesure pas directement le niveau piézométrique ni la salinité — enjeux majeurs au Maroc.
3. **Données institutionnelles :** ONEE (~1 800 forages) et ABH ne sont pas intégrées — perspective future (SNIE).
4. **Capteurs IoT :** la partie MQTT est **simulée** ; l'entraînement repose sur des fiches d'enquête, pas sur pression/vibration réelles.

---

## 7. Perspectives Maroc (hors scope actuel)

- Partenariat ABH / ONEE pour données piézométriques ou fiches points d'eau
- Intégration au **SNIE** (Système national d'information sur l'eau)
- Capteurs réels : débit, pression, niveau, conductivité (salinité)
- Ré-entraînement du modèle champion sur données nationales

---

## 8. Phrase pour le rapport académique

> *AquaSense AI répond à la problématique marocaine de maintenance des forages et points d'eau en zone rurale. Le pipeline prédictif est développé et benchmarké sur le jeu international Pump It Up, retenu pour sa richesse, ses labels et sa reproductibilité, en vue d'un déploiement futur sur des données nationales (ONEE, ABH, SNIE).*

---

## 9. Documents à lire (ordre recommandé)

1. **Ce fichier** — `choix_dataset_maroc.md` (cadrage)
2. **Guide dataset** — `guide_dataset_et_wrangling.md` (contenu des données)
3. **Vue globale** — `PROJECT_OVERVIEW.md` (roadmap + journal)
4. **Rapports sprint** — `sprint_00` → `sprint_02` (détail technique)

---

*AquaSense AI · EHTP MIG S4 · Dr. Rym Nassih*
