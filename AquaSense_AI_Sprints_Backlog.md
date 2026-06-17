# AquaSense AI — Sprints & Product Backlog Détaillé
**Maintenance prédictive des forages & points d'eau · Contexte Maroc · EHTP MIG S4**
**Équipe : TRAORE Fanogo Mohamed · NADAHE Mohamed**

---

> **Cadrage du projet**
> - **Problème visé :** maintenance prédictive des forages et points d'eau en **contexte marocain**
> - **Données d'entraînement :** benchmark **Pump It Up** (Tanzanie) — proxy ouvert et reproductible
> - **Justification :** voir [reports/choix_dataset_maroc.md](./reports/choix_dataset_maroc.md)
> - **Paradigme :** inchangé — classification 3 classes (`functional` / `needs repair` / `non functional`)
> - **S0–S2 :** conservés tels quels (pipeline technique valide pour les deux contextes)

> **Priorités du projet (ordre décroissant)**
> 1. 🧠 **Modèle ML + Deep Learning** — cœur du projet, priorité maximale
> 2. 🚀 **Déploiement & Application** — dashboard Maroc + simulation MQTT
> 3. ~~Implémentation terrain réelle~~ — hors scope académique

---

## Vue d'ensemble des Sprints

| Sprint | Thème | Durée | Priorité |
|--------|-------|-------|----------|
| S0 | Setup & Environnement | 1 jour | Fondation |
| S1 | Acquisition & EDA | 2–3 jours | Phase 1 |
| S2 | Wrangling & Feature Engineering | 3 jours | Phase 2 |
| S3 | Baseline ML — Classifieurs classiques | 3–4 jours | ⭐ Modèle |
| S4 | Deep Learning (Ajout) | 3–4 jours | ⭐ Modèle |
| S5 | Optimisation & Comparaison finale | 2 jours | ⭐ Modèle |
| S6 | Simulation IoT Mosquitto | 2 jours | 🚀 Déploiement |
| S7 | Dashboard & Application | 2–3 jours | 🚀 Déploiement |
| S8 | Tests de simulation & Validation | 2 jours | 🚀 Déploiement |
| S9 | Rapport & Livrables finaux | 1–2 jours | Finalisation |

---

## Sprint 0 — Setup & Environnement
**Durée : 1 jour**

### Objectif
Mettre en place un environnement reproductible, le dépôt Git, et valider l'accès aux données avant de toucher au moindre modèle.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S0-01 | Créer le dépôt GitHub | Structure de dossiers exacte du proposal (`/data/raw`, `/notebooks`, `/src`, `/models`, `/dashboard`, etc.) | Repo public avec README |
| S0-02 | Setup environnement Python | `python -m venv .venv`, `requirements.txt` avec versions pinnées : pandas, numpy, scikit-learn, xgboost, tensorflow/keras, paho-mqtt, streamlit, matplotlib, seaborn, plotly, joblib, faker | `requirements.txt` validé |
| S0-03 | Télécharger le dataset proxy | Pump It Up (Tanzanie) depuis drivendata.org → `train_values.csv`, `train_labels.csv`, `test_values.csv` dans `/data/raw/` — proxy pour pipeline Maroc | Fichiers présents, taille vérifiée |
| S0-04 | Valider la structure du dataset | `df.shape`, `df.dtypes`, `df.head()`, target distribution dans un notebook `00_setup.ipynb` | Audit initial documenté |
| S0-05 | `.gitignore` | Exclure `/data/raw`, `__pycache__`, `.env`, fichiers `.joblib` lourds | `.gitignore` fonctionnel |

### Critères d'acceptation
- [ ] `pip install -r requirements.txt` tourne sans erreur sur machine fraîche
- [ ] Le dataset est chargé : 59 400 lignes × 40 colonnes confirmées
- [ ] Premier commit poussé sur GitHub

---

## Sprint 1 — Acquisition & EDA (Exploratory Data Analysis)
**Durée : 2–3 jours · Phase 1 du projet**

### Objectif
Comprendre profondément le dataset proxy Pump It Up, documenter toutes les anomalies, produire les visualisations qui guideront le feature engineering, et rédiger le **Problem Statement** avec le **contexte marocain** comme motivation.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S1-01 | Merge train_values + train_labels | Jointure sur `id`, vérifier absence de doublons | DataFrame unifié `df_train` |
| S1-02 | Audit des valeurs manquantes | Carte de chaleur de nullité, comptage par colonne, % de NaN | Heatmap + tableau récapitulatif |
| S1-03 | Distribution de la cible | Barplot + pie chart de `status_group` (functional 54%, needs repair 7%, non-functional 39%) — quantifier l'imbalance | Graphique + texte d'analyse |
| S1-04 | Analyse des variables numériques | Histogrammes + boxplots pour `amount_tsh`, `gps_height`, `population`, `construction_year` — identifier les outliers et valeurs aberrantes (GPS 0.0, year=0) | 6+ graphiques |
| S1-05 | Analyse des variables catégorielles | Barplots de fréquences pour `basin`, `extraction_type`, `management`, `water_quality`, `payment` | 5+ graphiques |
| S1-06 | Analyse géographique | Scatter plot lat/lon coloré par statut, identifier les clusters de pompes non-fonctionnelles par région | Carte scatter matplotlib |
| S1-07 | Matrice de corrélation | Heatmap de corrélation sur features numériques, identifier les features redondantes | Heatmap corrélation |
| S1-08 | Analyse temporelle | Distribution de `date_recorded` et `construction_year` valides, age moyen par statut | Graphique temporel |
| S1-09 | Problem Statement écrit | Contexte **Maroc** (stress hydrique, forages ruraux) + formulation technique + critères métier | Section markdown dans notebook |
| S1-10 | AI Context Note | Connexion avec l'histoire IA (MYCIN, rule-based vs statistical learning) | Section rédigée |
| S1-11 | Justification dataset proxy | Documenter pourquoi Pump It Up (Tanzanie) et pas de données Maroc ouvertes — voir `choix_dataset_maroc.md` | `reports/choix_dataset_maroc.md` |

### Critères d'acceptation
- [ ] Notebook `01_eda.ipynb` complet avec toutes les visualisations
- [ ] Minimum 8 graphiques documentés avec analyse textuelle
- [ ] Toutes les anomalies du dataset cataloguées (NaN, GPS invalides, year=0, outliers)
- [ ] Distribution de la cible confirmée et stratégie d'imbalance définie

---

## Sprint 2 — Wrangling & Feature Engineering
**Durée : 3 jours · Phase 2 du projet**

### Objectif
Transformer les données brutes en features propres et riches utilisables par tous les modèles (classiques ET deep learning).

### Backlog

#### 2A — Nettoyage des données

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S2-01 | Traitement GPS invalides | Remplacer les (0.0, 0.0) par le centroïde régional correspondant (`basin` ou `region`) | `longitude`/`latitude` propres |
| S2-02 | Traitement `construction_year = 0` | Flag binaire `year_unknown`, remplacer 0 par la médiane par `basin` ou `extraction_type` | Colonne `construction_year` propre + flag |
| S2-03 | Traitement `gps_height` négatif | Remplacer valeurs < 0 par NaN puis imputer par médiane régionale | `gps_height` sans négatifs |
| S2-04 | Imputation `funder` et `installer` | Normaliser la casse (lowercase, strip), grouper les top-20, le reste → "Other" | Cardinalité réduite à ~21 catégories |
| S2-05 | Traitement `amount_tsh` zéros | Distinguer vrais zéros (gravity-fed) des manquants — créer flag `tsh_is_zero` | Feature `tsh_is_zero` + `amount_tsh` imputé |
| S2-06 | Supprimer colonnes redondantes | Identifier et supprimer les colonnes quasi-dupliquées (`quantity_group` ≈ `quantity`, `source` ≈ `source_type`, etc.) | DataFrame réduit et propre |

#### 2B — Feature Engineering

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S2-07 | `pump_age` | `pump_age = 2024 - construction_year` (NaN si year=0 avant imputation) | Feature `pump_age` |
| S2-08 | Décomposition temporelle | `year_recorded`, `month_recorded`, `day_of_year` depuis `date_recorded` | 3 nouvelles features |
| S2-09 | `age_at_recording` | `year_recorded - construction_year` — âge réel de la pompe au moment du survey | Feature `age_at_recording` |
| S2-10 | Distance au centre régional | Distance euclidienne (lat, lon) vers le centroïde de chaque `basin` — proxy d'isolement géographique | Feature `dist_to_basin_center` |
| S2-11 | Encodage catégoriel | OrdinalEncoder pour features à haute cardinalité résiduelles, OneHotEncoder pour features à faible cardinalité (basin, water_quality, payment) | Features encodées |
| S2-12 | Normalisation features numériques | StandardScaler pour LR et KNN, laisser brut pour RF/XGBoost, MinMaxScaler pour le réseau de neurones | Pipelines de normalisation différenciés |
| S2-13 | Sauvegarde dataset nettoyé | Export vers `/data/cleaned/train_clean.csv` + `/data/cleaned/test_clean.csv` | Fichiers CSV propres versionnés |
| S2-14 | Pipeline `preprocessing.py` | Regrouper toutes les transformations dans un module src/preprocessing.py réutilisable (classe ou fonction) | Module importable |

### Critères d'acceptation
- [ ] Notebook `02_wrangling.ipynb` documenté
- [ ] 0 NaN dans les features finales utilisées par les modèles
- [ ] Dataset sauvegardé dans `/data/cleaned/`
- [ ] `src/preprocessing.py` importable et testable isolément
- [ ] Au moins 5 nouvelles features créées (feature engineering documenté)

---

## Sprint 3 — Baseline ML — Classifieurs Classiques
**Durée : 3–4 jours · ⭐ PRIORITÉ MAXIMALE**

### Objectif
Entraîner, évaluer et comparer les 4 algorithmes classiques du proposal. Établir une baseline solide avant le deep learning. Obtenir F1-Macro ≥ 0.72.

### Backlog

#### 3A — Préparation expérimentale

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S3-01 | Train/test split stratifié | `train_test_split(stratify=y)` avec ratio 80/20, reproductible avec `random_state=42` | X_train, X_test, y_train, y_test |
| S3-02 | Gestion de l'imbalance | Tester `class_weight='balanced'` pour RF/LR, `scale_pos_weight` pour XGBoost, SMOTE comme option | Stratégie d'imbalance documentée |
| S3-03 | Fonction d'évaluation commune | Fonction `evaluate_model(model, X_test, y_test)` → F1-Macro, F1 par classe, Accuracy, ROC-AUC OvR, matrice de confusion, temps d'inférence | Fonction dans `src/train.py` |

#### 3B — Entraînement des modèles

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S3-04 | Logistic Regression | Pipeline : StandardScaler → LR(max_iter=1000, class_weight='balanced'). Baseline interprétable. | Modèle + métriques |
| S3-05 | K-Nearest Neighbors | Pipeline : StandardScaler → KNN(n_neighbors=5, metric='euclidean'). Explorer l'effet de lat/lon. | Modèle + métriques |
| S3-06 | Random Forest | `RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)`. Feature importance. | Modèle + métriques + feature importance plot |
| S3-07 | XGBoost | `XGBClassifier(n_estimators=300, scale_pos_weight=..., eval_metric='mlogloss')`. Courbes d'apprentissage. | Modèle + métriques |

#### 3C — Optimisation hyperparamètres

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S3-08 | GridSearchCV — Random Forest | Tuner `max_depth`, `min_samples_leaf`, `max_features`. Cross-validation 5-fold stratifiée. | Meilleurs hyperparamètres RF |
| S3-09 | GridSearchCV — XGBoost | Tuner `learning_rate`, `max_depth`, `subsample`, `colsample_bytree`. | Meilleurs hyperparamètres XGB |
| S3-10 | Cross-validation finale | 5-fold stratifiée sur le meilleur modèle de chaque famille. Rapport mean ± std F1-Macro. | Tableau de résultats comparatif |

#### 3D — Interprétabilité

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S3-11 | Feature importance RF & XGBoost | Barplot top-20 features les plus importantes | Graphique interprétabilité |
| S3-12 | Matrices de confusion | Heatmap normalisée pour chaque modèle — identifier où chaque modèle confond les classes | 4 matrices de confusion |
| S3-13 | Sauvegarder les modèles | `joblib.dump()` pour RF et XGBoost (meilleurs) dans `/models/` avec versioning | `rf_best_v1.joblib`, `xgb_best_v1.joblib` |

### Critères d'acceptation
- [ ] 4 modèles entraînés et évalués avec métriques standardisées
- [ ] Tableau comparatif F1-Macro / Recall "needs repair" / latence d'inférence
- [ ] Meilleur modèle classique atteint F1-Macro ≥ 0.72
- [ ] Recall classe "needs repair" ≥ 0.65 sur au moins un modèle
- [ ] Modèles sauvegardés dans `/models/`

---

## Sprint 4 — Deep Learning (Ajout au projet)
**Durée : 3–4 jours · ⭐ PRIORITÉ MAXIMALE**

### Objectif
Implémenter des approches deep learning pour dépasser les performances des classifieurs classiques sur ce dataset tabulaire. Comparer honnêtement avec les baselines ML.

### Architecture proposée
Deux approches DL à implémenter et comparer :
- **MLP (Multilayer Perceptron)** — réseau feed-forward pour données tabulaires
- **TabNet** ou **1D-CNN** — architectures adaptées aux données structurées

### Backlog

#### 4A — MLP Tabulaire (TensorFlow/Keras)

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S4-01 | Préparation données pour DL | OneHotEncoding complet des catégorielles, MinMaxScaler sur numériques, LabelEncoder sur la cible → arrays numpy | Arrays X_train_dl, X_test_dl |
| S4-02 | Architecture MLP de base | `Input → Dense(256, relu) → BatchNorm → Dropout(0.3) → Dense(128, relu) → BatchNorm → Dropout(0.3) → Dense(64, relu) → Dense(3, softmax)` | Modèle Keras défini |
| S4-03 | Configuration entraînement | `Adam(lr=1e-3)`, `CategoricalCrossentropy`, `class_weight` pour imbalance, `EarlyStopping(patience=10)`, `ReduceLROnPlateau` | Config d'entraînement |
| S4-04 | Entraînement MLP | `model.fit(X_train, y_train, epochs=100, batch_size=512, validation_split=0.2)` | Historique d'entraînement |
| S4-05 | Courbes d'apprentissage MLP | Plot loss/val_loss et accuracy/val_accuracy — détecter overfitting/underfitting | Graphique courbes |
| S4-06 | Évaluation MLP | Appliquer la même `evaluate_model()` que Sprint 3 — comparaison directe | Métriques MLP |

#### 4B — Architecture améliorée : Residual MLP ou 1D-CNN

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S4-07 | Residual MLP (Skip connections) | Ajouter des connexions résiduelles : `x = Dense(128)(x); x = Add()([x, skip])` — aide sur données tabulaires profondes | Modèle ResidualMLP |
| S4-08 | 1D-CNN sur features ordonnées | Reshaper features en séquence → `Conv1D(64, 3) → GlobalMaxPool → Dense(64) → Dense(3)` — capte des motifs locaux entre features | Modèle 1D-CNN |
| S4-09 | Comparaison MLP vs ResidualMLP vs 1D-CNN | Tableau comparatif F1-Macro sur les 3 architectures DL | Tableau comparatif DL |

#### 4C — Optimisation DL

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S4-10 | Tuning hyperparamètres | Tester dropout rates (0.2, 0.3, 0.5), learning rates (1e-2, 1e-3, 1e-4), batch sizes (256, 512, 1024) — au minimum 9 combinaisons | Tableau de tuning |
| S4-11 | Regularisation L2 | Ajouter `kernel_regularizer=l2(0.001)` sur les couches Dense — comparer avec/sans | Impact régularisation |
| S4-12 | Weighted loss custom | Implémenter `class_weight` proportionnel à l'inverse de la fréquence de classe pour forcer l'apprentissage de "needs repair" | Weighted loss fonctionnelle |
| S4-13 | Sauvegarder le meilleur modèle DL | `model.save('/models/best_dl_model.keras')` + export en `.tflite` pour edge deployment future | `best_dl_model.keras` + `.tflite` |

#### 4D — Explication DL

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S4-14 | Analyse des features DL | Permutation importance sur le meilleur réseau — comparer avec feature importance RF/XGBoost | Comparaison d'importance features ML vs DL |
| S4-15 | Justification théorique | Section dans le rapport : pourquoi le DL aide (ou pas) sur des données tabulaires vs images/texte | Texte académique ~500 mots |

### Critères d'acceptation
- [ ] Au moins 2 architectures DL implémentées et évaluées
- [ ] Entraînement stable (courbes convergentes, pas d'explosion de gradient)
- [ ] Le meilleur modèle DL comparé directement aux modèles classiques dans un tableau unifié
- [ ] Modèle Keras sauvegardé + export TFLite
- [ ] Justification de l'apport (ou limite) du DL sur ce dataset

---

## Sprint 5 — Optimisation Finale & Comparaison Tous Modèles
**Durée : 2 jours · ⭐ PRIORITÉ MAXIMALE**

### Objectif
Sélectionner le meilleur modèle global, explorer les ensembles, et produire le tableau de comparaison final qui constitue le cœur scientifique du projet.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S5-01 | Tableau comparatif final | F1-Macro, F1 "needs repair", F1 "non-functional", Accuracy, ROC-AUC, Temps inférence (ms/pompe) pour : LR, KNN, RF, XGBoost, MLP, ResidualMLP/1D-CNN | Tableau markdown + CSV |
| S5-02 | Voting Ensemble | `VotingClassifier([rf_best, xgb_best, mlp_best], voting='soft')` — souvent +1 à +2% F1 | Métriques ensemble |
| S5-03 | Stacking Ensemble | `StackingClassifier` avec méta-modèle LR — si le voting ne suffit pas | Métriques stacking (optionnel) |
| S5-04 | Seuil de décision ajusté | Pour la classe "needs repair" (la plus critique), tester des seuils de classification 0.3–0.5 — arbitrage précision/rappel | Courbe Precision-Recall + seuil optimal |
| S5-05 | Model Card | Fiche modèle : performances, données d'entraînement, biais connus, cas d'usage recommandé, limites | `reports/model_card.md` |
| S5-06 | Sélection du modèle de production | Choisir et justifier le modèle final déployé dans le dashboard | Décision documentée |

### Critères d'acceptation
- [ ] Tableau comparatif complet avec tous les modèles (ML + DL)
- [ ] Un modèle champion sélectionné avec justification rigoureuse
- [ ] F1-Macro champion ≥ 0.72, Recall "needs repair" ≥ 0.65
- [ ] Model Card rédigée

---

## Sprint 6 — Simulation IoT Mosquitto
**Durée : 2 jours · 🚀 Déploiement**

### Objectif
Implémenter le simulateur de capteurs et le pipeline MQTT complet qui alimente le modèle avec des données temps-réel simulées.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S6-01 | Installation Mosquitto | `sudo apt install mosquitto mosquitto-clients` ou Docker. Configurer broker local port 1883. | Broker MQTT opérationnel |
| S6-02 | Simulateur de pompes saines | Script `src/simulator.py` : publisher paho-mqtt qui génère `pressure = N(4.2, 0.1)`, `vibration = N(0.05, 0.01)`, `flow = N(12, 0.5)` sur topic `aquasense/{pump_id}/telemetry` toutes les 5 secondes | Script simulateur fonctionnel |
| S6-03 | Simulateur de dégradation | Modèle de dégradation progressive : pression −0.3 bar/jour, vibration +0.02g/jour, flow −0.5 L/min/jour sur 14 jours avant failure simulée | Scénario de dégradation |
| S6-04 | Simulateur de pompe défaillante | pressure=0, flow=0, vibration=spikes aléatoires | Scénario failure |
| S6-05 | Effets saisonniers Maroc | Réduire flow de 15% en période sèche (juin–septembre, Maroc) via paramètre `month` du simulateur | Saisonnalité implémentée |
| S6-06 | Subscriber + inférence temps-réel | Script `src/mqtt_consumer.py` : subscribe à tous les topics `aquasense/+/telemetry`, agrège les 30 derniers messages, construit le feature vector, appelle `model.predict()`, publie résultat sur `aquasense/{pump_id}/prediction` | Pipeline inference MQTT |
| S6-07 | Persistance InfluxDB ou SQLite | Stocker chaque message MQTT reçu en base avec timestamp — structure `(pump_id, timestamp, pressure, vibration, flow, prediction)` | Base de données temps-série |
| S6-08 | Test end-to-end simulation | Lancer simulateur + consumer + vérifier les prédictions dans la base — scénario complet de 50 pompes | Test E2E documenté |

### Critères d'acceptation
- [ ] Broker Mosquitto opérationnel en local
- [ ] Simulateur génère des données pour 50 pompes avec les 3 scénarios (saine, dégradation, failure)
- [ ] Le consumer reçoit, infère et publie en < 5s (latence MQTT-to-prediction)
- [ ] Données persistées en base et requêtables

---

## Sprint 7 — Dashboard & Application Web
**Durée : 2–3 jours · 🚀 Déploiement**

### Objectif
Construire le dashboard Streamlit interactif orienté **déploiement Maroc** : visualiser les prédictions, prioriser les interventions sur forages/points d'eau, carte et KPIs contextualisés (modèle entraîné sur Pump It Up).

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S7-01 | Structure de l'application | `dashboard/app.py` avec navigation multi-pages Streamlit : Carte, Alertes, Analyse, À propos | Squelette app Streamlit |
| S7-02 | Carte interactive (vue Maroc) | Scatter map Plotly/Mapbox — pompes colorées par statut, présentation contextualisée Maroc (données entraînement = proxy Tanzanie, démo = Maroc) | Carte interactive |
| S7-03 | Indicateurs clés (KPIs) | En haut de page : nombre de pompes par statut, % en risque, alertes critiques du jour | Section KPIs |
| S7-04 | Panel d'alerte temps-réel | Liste des pompes prédites "needs repair" dans les 30 prochains jours. Tri par score de risque. Bouton "Assigner un technicien". | Panel alertes |
| S7-05 | Page détail pompe | Click sur une pompe → page avec : historique des métriques (graphiques pressure/vibration/flow), prédiction avec score de confiance, historique des interventions | Page détail |
| S7-06 | Mise à jour auto MQTT | Streamlit polling du broker MQTT toutes les 10s — mise à jour des statuts en temps quasi-réel | Auto-refresh |
| S7-07 | Comparaison des modèles | Page "Modèles" : tableau comparatif F1 de tous les modèles entraînés, graphique radar des performances | Page analyse |
| S7-08 | Export rapport PDF | Bouton "Générer rapport" → PDF avec liste des pompes critiques, carte, métriques | Export PDF (optionnel) |

### Critères d'acceptation
- [ ] Dashboard tourne avec `streamlit run dashboard/app.py`
- [ ] Carte avec les 59 400 pompes colorées par statut chargée en < 3s
- [ ] Panel alertes affiche correctement les prédictions du modèle
- [ ] Mise à jour visible depuis le simulateur MQTT en < 10s

---

## Sprint 8 — Tests de Simulation & Validation
**Durée : 2 jours · 🚀 Déploiement**

### Objectif
Valider que le système complet (modèle + MQTT + dashboard) se comporte correctement sur les scénarios de simulation. Tests fonctionnels et de performance.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S8-01 | Test scénario "pompe saine" | Simuler 14 jours de données saines → vérifier que le modèle prédit systématiquement "functional" | Test documenté + taux correct |
| S8-02 | Test scénario "dégradation progressive" | Simuler 14 jours de dégradation → vérifier que la prédiction bascule de "functional" vers "needs repair" avant J14 | Test prédictif validé |
| S8-03 | Test scénario "failure soudaine" | Simuler une panne instantanée → vérifier délai de détection < 5s via MQTT | Latence mesurée |
| S8-04 | Test de charge MQTT | Simuler 50 pompes en parallèle → vérifier que le consumer traite tous les messages sans perte ni retard > 5s | Benchmark 50 pompes |
| S8-05 | Test d'imbalance — classe "needs repair" | Vérifier que le modèle détecte correctement les pompes en dégradation (Recall ≥ 0.65 sur données simulées) | Recall mesuré sur simulation |
| S8-06 | Test latence d'inférence | Mesurer le temps de prédiction pour 1 pompe et pour 50 pompes simultanées — objectif < 500ms/pompe | Benchmark latence |
| S8-07 | Test reproductibilité pipeline | Exécuter `python src/train.py` depuis zéro sur machine fraîche → résultats identiques (même random seed) | Rapport de reproductibilité |
| S8-08 | Tests unitaires | `pytest` sur les fonctions de preprocessing, feature engineering, et simulation — couvrir les cas aux limites (NaN, GPS=0, year=0) | Fichier `tests/test_preprocessing.py` avec ≥ 10 tests |

### Critères d'acceptation
- [ ] Les 3 scénarios de simulation passent avec comportement attendu
- [ ] 50 pompes simulées en parallèle sans crash ni perte de message
- [ ] Latence MQTT-to-prediction < 5s confirmée
- [ ] Tests unitaires : ≥ 80% de passage

---

## Sprint 9 — Rapport & Livrables Finaux
**Durée : 1–2 jours · Finalisation**

### Objectif
Documenter, packager et soumettre tous les livrables académiques et techniques.

### Backlog

| # | Tâche | Description | Livrable |
|---|-------|-------------|----------|
| S9-01 | README complet | Instructions de reproduction en une commande, prérequis, dataset URL, architecture du projet | `README.md` |
| S9-02 | Notebooks finaux nettoyés | Relire et nettoyer les 7 notebooks (`00_setup` → `07_report`), outputs clairs, markdown explicatif | Notebooks propres |
| S9-03 | Rapport académique | PDF : contexte **Maroc**, choix dataset proxy, EDA, Wrangling, ML, DL, limites transfert, Simulation IoT, Conclusion | `reports/AquaSense_AI_Report.pdf` |
| S9-04 | Model Card | Fiche modèle du champion : performances, données, biais, recommandations | `reports/model_card.md` |
| S9-05 | Diapositives de présentation | 10–15 slides : problème, dataset, pipeline, résultats ML vs DL, démo dashboard, conclusion | `reports/presentation.pdf` |
| S9-06 | Tag Git final | `git tag v1.0.0` sur le commit de soumission | Tag sur GitHub |
| S9-07 | Vérification reproductibilité | Test final : clone repo → pip install → python train.py → streamlit run → tout fonctionne | ✅ Reproductible |

### Critères d'acceptation
- [ ] Tout le code tourne depuis un clone frais en < 10 minutes de setup
- [ ] Rapport PDF soumis avant deadline (12 juin 2025)
- [ ] GitHub public, commit history propre et lisible
- [ ] Tous les livrables dans `/reports/`

---

## Récapitulatif — Tableau de Bord Global

```
S0  ██░░░░░░░░░░░░░░░░░░  Setup            [1j]
S1  ████░░░░░░░░░░░░░░░░  EDA              [2-3j]
S2  ██████░░░░░░░░░░░░░░  Wrangling        [3j]
S3  ████████░░░░░░░░░░░░  ML Classique  ⭐ [3-4j]
S4  ████████░░░░░░░░░░░░  Deep Learning ⭐ [3-4j]
S5  ████░░░░░░░░░░░░░░░░  Comparaison   ⭐ [2j]
S6  ████░░░░░░░░░░░░░░░░  MQTT Sim      🚀 [2j]
S7  ██████░░░░░░░░░░░░░░  Dashboard     🚀 [2-3j]
S8  ████░░░░░░░░░░░░░░░░  Tests Sim     🚀 [2j]
S9  ████░░░░░░░░░░░░░░░░  Rapport          [1-2j]
```

**Durée totale estimée : ~22–28 jours de travail équipe (2 personnes)**

---

## Stack Technique par Sprint

| Couche | Technologies | Sprints |
|--------|-------------|---------|
| Data | pandas, numpy, sqlite3 | S1, S2, S3 |
| ML Classique | scikit-learn, XGBoost, joblib | S3, S5 |
| Deep Learning | TensorFlow/Keras, numpy | S4, S5 |
| IoT Simulation | paho-mqtt, Mosquitto, Faker | S6 |
| Dashboard | Streamlit, Plotly/Mapbox | S7 |
| Tests | pytest, time | S8 |
| Rapport | LaTeX/Word, markdown | S9 |

---

*AquaSense AI · EHTP MIG S4 · Dr. Rym Nassih*
