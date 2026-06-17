# AquaSense AI — Sprint 4 Colab

## Setup (3 cellules)

**1. GPU** : Runtime → Change runtime type → T4 GPU

**2. Drive**
```python
from google.colab import drive
drive.mount("/content/drive")
```

**3. Dézip + pip minimal**
```python
!unzip -o -q "/content/drive/MyDrive/AquaSense_S4_Colab.zip" -d /content/
%pip install -q imbalanced-learn
%cd /content/AquaSense_S4_Colab
```

Les warnings pip (pandas/numpy versions) sont **normaux sur Colab** — ignorer pour S4.

**4.** Ouvrir **`notebooks/05_dl_colab_tune.ipynb`** (recommandé — tuning MLP complet)  
   ou `notebooks/04_dl_mlp.ipynb` (baseline simple seulement).

## Notebook tuning (recommandé)

`notebooks/05_dl_colab_tune.ipynb` — upload direct sur Colab :
1. Runtime GPU T4
2. Cellules setup → vérification GPU → `python -m src.train_dl tune`
3. Copie auto vers `MyDrive/AquaSense_DL_results/`

Durée : ~45–90 min.

## Headless
```python
%cd /content/AquaSense_S4_Colab
!python -m src.train_dl
```

## Ramener sur PC
- `models/mlp_best_v1.keras`, `models/best_dl_model.keras`
- `reports/sprint_04_metrics.json`
