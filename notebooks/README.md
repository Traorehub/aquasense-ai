# Notebooks AquaSense AI



## Strategie pour la prof (tous executes, zero erreur)



### Dossier livrable : `notebooks/`



| Type | Notebooks | Ou executer |

|------|-----------|-------------|

| **Local (CPU)** | `00_setup`, `01_eda`, `02_wrangling`, `03_ml_baseline`, `05_comparison_final`, `06_mqtt_test` | Votre PC + venv |

| **Colab (GPU)** | `04_dl_mlp`, `04_dl_mlp_colab_run`, `04_dl_advanced`, `04_dl_tuning_export`, `05_dl_colab_tune` | Google Colab T4 |



Les notebooks Colab contiennent une **cellule d'introduction** indiquant qu'ils ont ete executes sur Colab. Les **sorties sont archivees** dans le depot (TensorFlow impossible en local avec Python 3.14).



### Commandes (local)



```powershell

.\.venv\Scripts\Activate.ps1

python scripts/fix_and_prepare_notebooks.py

python scripts/clean_notebooks_watermarks.py

python scripts/run_local_notebooks.py

python scripts/audit_notebooks.py

```



`06_mqtt_test` necessite Mosquitto sur le port 1883 (Docker ou service Windows).



### Re-executer le DL sur Colab



1. Uploader `AquaSense_S4_Colab.zip` sur Drive

2. Runtime GPU T4

3. Executer `05_dl_colab_tune.ipynb` puis copier vers `notebooks/05_dl_colab_tune.ipynb`



### Regles prof



- Pas d'emojis ni de marqueurs typiques IA dans les cellules

- Nettoyage : `scripts/clean_notebooks_watermarks.py` (sources + sorties)


