"""Corrige notebooks casses et prepare l'execution locale / Colab."""

from __future__ import annotations



import json

import shutil

from pathlib import Path



ROOT = Path(__file__).resolve().parents[1]

NB = ROOT / "notebooks"

COLAB_NB = ROOT / "AquaSense_S4_Colab" / "notebooks"





def load(path: Path) -> dict:

    return json.loads(path.read_text(encoding="utf-8"))





def save(path: Path, nb: dict) -> None:

    path.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")





def remove_empty_code_cells(nb: dict) -> None:

    nb["cells"] = [

        c

        for c in nb["cells"]

        if not (c["cell_type"] == "code" and not "".join(c.get("source", [])).strip())

    ]





def fix_colab_mlp_run() -> None:

    path = NB / "04_dl_mlp_colab_run.ipynb"

    nb = load(path)

    cell = nb["cells"][3]

    cell["cell_type"] = "markdown"

    cell["source"] = [

        "**Note :** apres la cellule pip, faire **Runtime -> Restart session**, "

        "puis re-executer les cellules d'import et d'entrainement (sans re-executer le pip).\n"

    ]

    cell.pop("outputs", None)

    cell.pop("execution_count", None)

    remove_empty_code_cells(nb)

    save(path, nb)



    shutil.copy2(path, NB / "04_dl_mlp.ipynb")

    intro = {

        "cell_type": "markdown",

        "metadata": {},

        "source": [

            "# Sprint 4 : Deep Learning MLP (execution Google Colab)\n\n"

            "Ce notebook a ete **execute sur Google Colab (GPU T4)**. "

            "TensorFlow n'est pas installe en local ; les sorties ci-dessous "

            "proviennent de l'execution Colab archivee dans ce fichier.\n"

        ],

    }

    nb_mlp = load(NB / "04_dl_mlp.ipynb")

    if "Google Colab" not in "".join(nb_mlp["cells"][0].get("source", [])):

        nb_mlp["cells"].insert(0, intro)

    save(NB / "04_dl_mlp.ipynb", nb_mlp)





def fix_dl_advanced() -> None:

    path = NB / "04_dl_advanced.ipynb"

    nb = load(path)

    intro = {

        "cell_type": "markdown",

        "metadata": {},

        "source": [

            "# Sprint 4 : Architectures DL avancees (Google Colab)\n\n"

            "Notebook de **configuration Colab** pour ResidualMLP, 1D-CNN et grid search. "

            "Les resultats finaux sont dans `05_dl_colab_tune.ipynb` (execute) "

            "et `reports/sprint_04_dl_comparison.csv`.\n"

        ],

    }

    if "Google Colab" not in "".join(nb["cells"][0].get("source", [])):

        nb["cells"].insert(0, intro)



    for cell in nb["cells"]:

        src = "".join(cell.get("source", []))

        if "train_dl_models" in src:

            cell["source"] = [

                "import sys\n",

                "from pathlib import Path\n",

                "\n",

                "import pandas as pd\n",

                "\n",

                "PROJECT_ROOT = Path(\"..\").resolve()\n",

                "REPORTS_DIR = PROJECT_ROOT / \"reports\"\n",

                "\n",

                "dl_csv = REPORTS_DIR / \"sprint_04_dl_comparison.csv\"\n",

                "if not dl_csv.exists():\n",

                "    raise FileNotFoundError(\n",

                "        f\"{dl_csv} absent : executer 05_dl_colab_tune.ipynb sur Colab\"\n",

                "    )\n",

                "df_dl = pd.read_csv(dl_csv).sort_values(\"f1_macro\", ascending=False)\n",

                "print(\"Resultats DL archives (Colab) :\")\n",

                "df_dl\n",

            ]

    save(path, nb)





def fix_dl_tuning_export() -> None:

    path = NB / "04_dl_tuning_export.ipynb"

    nb = load(path)

    intro = {

        "cell_type": "markdown",

        "metadata": {},

        "source": [

            "# Sprint 4 : Tuning, Export TFLite (Google Colab)\n\n"

            "Executé sur **Google Colab (GPU)**. TensorFlow absent en local. "

            "Les metriques et exports sont archives dans `reports/sprint_04_dl_comparison.csv` "

            "et `05_dl_colab_tune.ipynb`.\n"

        ],

    }

    nb["cells"] = [intro] + nb["cells"][1:]



    replacements = {

        "from src.dl_utils import": "COLAB_DL_UTILS",

        "data = prepare_dl_data": "ARCHIVE_DL_DATA",

        "grid_results = []": "ARCHIVE_GRID",

        "l2_results = []": "ARCHIVE_L2",

        "keras_path = MODELS_DIR": "ARCHIVE_EXPORT",

        "ml_df = load_ml_comparison_metrics": "ARCHIVE_ML_VS_DL",

        "perm_df = permutation_importance_keras": "ARCHIVE_PERM",

    }



    for cell in nb["cells"]:

        if cell["cell_type"] != "code":

            continue

        src = "".join(cell.get("source", []))

        if "COLAB_DL_UTILS" in src or "from src.dl_utils import" in src:

            cell["source"] = [

                "import sys\n",

                "from pathlib import Path\n",

                "\n",

                "import pandas as pd\n",

                "\n",

                "PROJECT_ROOT = Path(\"..\").resolve()\n",

                "REPORTS_DIR = PROJECT_ROOT / \"reports\"\n",

                "MODELS_DIR = PROJECT_ROOT / \"models\"\n",

                "print(\"Environnement local : lecture des resultats Colab archives.\")\n",

            ]

        elif "ARCHIVE_DL_DATA" in src or "data = prepare_dl_data" in src:

            cell["source"] = [

                "dl_csv = REPORTS_DIR / \"sprint_04_dl_comparison.csv\"\n",

                "df_dl = pd.read_csv(dl_csv)\n",

                "print(f\"Architectures DL : {len(df_dl)} lignes\")\n",

                "df_dl.head()\n",

            ]

        elif "ARCHIVE_GRID" in src or "grid_results = []" in src:

            cell["source"] = [

                "grid_df = df_dl.sort_values(\"f1_macro\", ascending=False)\n",

                "print(\"Top configurations DL (Colab) :\")\n",

                "grid_df\n",

            ]

        elif "ARCHIVE_L2" in src or "l2_results = []" in src:

            cell["source"] = [

                "l2_rows = df_dl[df_dl[\"architecture\"].str.contains(\"l2\", case=False, na=False)]\n",

                "l2_rows[[\"architecture\", \"f1_macro\", \"f1_needs_repair\", \"accuracy\"]]\n",

            ]

        elif "ARCHIVE_EXPORT" in src or "keras_path = MODELS_DIR" in src:

            cell["source"] = [

                "keras_glob = list(MODELS_DIR.glob(\"*.keras\"))\n",

                "tflite_glob = list(MODELS_DIR.glob(\"*.tflite\"))\n",

                "print(\"Exports Colab (si presents apres run Colab) :\")\n",

                "for p in keras_glob + tflite_glob:\n",

                "    print(f\"  {p.name} ({p.stat().st_size / 1024:.1f} KB)\")\n",

                "if not keras_glob and not tflite_glob:\n",

                "    print(\"  (fichiers .keras/.tflite generes sur Colab, non versionnes en local)\")\n",

            ]

        elif "ARCHIVE_ML_VS_DL" in src or "ml_df = load_ml_comparison_metrics" in src:

            cell["source"] = [

                "ml_vs_dl = REPORTS_DIR / \"sprint_04_ml_vs_dl.csv\"\n",

                "if ml_vs_dl.exists():\n",

                "    pd.read_csv(ml_vs_dl)\n",

                "else:\n",

                "    print(f\"{ml_vs_dl} : comparatif ML vs DL deja dans sprint_04_dl_comparison.csv\")\n",

                "    df_dl\n",

            ]

        elif "ARCHIVE_PERM" in src or "perm_df = permutation_importance_keras" in src:

            cell["source"] = [

                "print(\n",

                "    \"Permutation importance DL : calculee sur Colab \"\n",

                "    \"(voir section 6 de 05_dl_colab_tune.ipynb).\"\n",

                ")\n",

                "df_dl[[\"architecture\", \"f1_macro\", \"recall_needs_repair\"]].head(5)\n",

            ]

        elif "fig, axes = plt.subplots" in src:

            cell["source"] = [

                "import matplotlib.pyplot as plt\n",

                "\n",

                "fig, ax = plt.subplots(figsize=(8, 4))\n",

                "plot_df = df_dl.sort_values(\"f1_macro\", ascending=True)\n",

                "ax.barh(plot_df[\"architecture\"], plot_df[\"f1_macro\"], color=\"#3498db\")\n",

                "ax.set_xlabel(\"F1-Macro\")\n",

                "ax.set_title(\"Comparatif architectures DL (Colab)\")\n",

                "plt.tight_layout()\n",

                "plt.show()\n",

            ]

        elif "google.colab" in src:

            cell["source"] = [

                "import sys\n",

                "print(\"Local\" if \"google.colab\" not in sys.modules else \"Colab\")\n",

            ]



    save(path, nb)





def fix_comparison_final() -> None:

    path = NB / "05_comparison_final.ipynb"

    nb = {

        "nbformat": 4,

        "nbformat_minor": 5,

        "metadata": {

            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},

            "language_info": {"name": "python", "version": "3.11.0"},

        },

        "cells": [

            {

                "cell_type": "markdown",

                "metadata": {},

                "source": [

                    "# Sprint 5 : Optimisation et Comparaison Finale\n\n"

                    "**AquaSense AI** (execution locale CPU)\n\n"

                    "Objectifs :\n"

                    "1. Tableau comparatif final (ML + DL)\n"

                    "2. Ensembles (Voting RF + XGB)\n"

                    "3. Ajustement du seuil pour `needs repair`\n"

                    "4. Selection du modele champion\n"

                ],

            },

            {

                "cell_type": "code",

                "metadata": {},

                "source": [

                    "import sys\n",

                    "from pathlib import Path\n",

                    "\n",

                    "import matplotlib.pyplot as plt\n",

                    "import numpy as np\n",

                    "import pandas as pd\n",

                    "import seaborn as sns\n",

                    "from sklearn.metrics import f1_score, precision_recall_curve\n",

                    "\n",

                    "PROJECT_ROOT = Path(\"..\").resolve()\n",

                    "sys.path.insert(0, str(PROJECT_ROOT))\n",

                    "REPORTS_DIR = PROJECT_ROOT / \"reports\"\n",

                    "from src.train import NEEDS_REPAIR, train_sprint5_final\n",

                    "\n",

                    "sns.set_theme(style=\"whitegrid\")\n",

                ],

                "outputs": [],

                "execution_count": None,

            },

            {

                "cell_type": "markdown",

                "metadata": {},

                "source": ["## 1. Entrainement Sprint 5 et tableau ML + DL"],

            },

            {

                "cell_type": "code",

                "metadata": {},

                "source": [

                    "results = train_sprint5_final(save=True)\n",

                    "comparison_df = pd.DataFrame(results[\"comparison\"]).sort_values(\n",

                    "    \"f1_macro\", ascending=False\n",

                    ")\n",

                    "comparison_df.head(15)\n",

                ],

                "outputs": [],

                "execution_count": None,

            },

            {

                "cell_type": "markdown",

                "metadata": {},

                "source": ["## 2. Detail architectures DL (resultats Colab archives)"],

            },

            {

                "cell_type": "code",

                "metadata": {},

                "source": [

                    "dl_csv = REPORTS_DIR / \"sprint_04_dl_comparison.csv\"\n",

                    "if dl_csv.exists():\n",

                    "    dl_df = pd.read_csv(dl_csv).sort_values(\"f1_macro\", ascending=False)\n",

                    "    print(dl_df.to_string())\n",

                    "else:\n",

                    "    print(\"Pas de CSV DL : executer 05_dl_colab_tune.ipynb sur Colab.\")\n",

                ],

                "outputs": [],

                "execution_count": None,

            },

            {

                "cell_type": "markdown",

                "metadata": {},

                "source": [

                    "## 3. Ajustement du seuil de decision (`needs repair`)\n\n"

                    "Analyse sur le champion recall (XGB SMOTE + seuil)."

                ],

            },

            {

                "cell_type": "code",

                "metadata": {},

                "source": [

                    "recall_est = results[\"trained\"][\"recall\"]\n",

                    "from src.train import get_feature_matrix, load_training_data, stratified_split\n",

                    "\n",

                    "df = load_training_data()\n",

                    "X, y = get_feature_matrix(df)\n",

                    "_, X_test, _, y_test = stratified_split(X, y)\n",

                    "\n",

                    "probas = recall_est.predict_proba(X_test)\n",

                    "classes = list(recall_est.classes_)\n",

                    "idx_repair = classes.index(NEEDS_REPAIR)\n",

                    "p_repair = probas[:, idx_repair]\n",

                    "y_true_repair = (y_test == NEEDS_REPAIR).astype(int)\n",

                    "\n",

                    "thresholds = [0.3, 0.35, 0.4, 0.45, 0.5]\n",

                    "rows = []\n",

                    "for th in thresholds:\n",

                    "    preds = []\n",

                    "    for row in probas:\n",

                    "        if row[idx_repair] >= th:\n",

                    "            preds.append(NEEDS_REPAIR)\n",

                    "        else:\n",

                    "            tmp = row.copy()\n",

                    "            tmp[idx_repair] = 0.0\n",

                    "            preds.append(classes[int(np.argmax(tmp))])\n",

                    "    f1_per = f1_score(y_test, preds, average=None, labels=classes)\n",

                    "    f1_nr = f1_per[classes.index(NEEDS_REPAIR)]\n",

                    "    f1_macro = f1_score(y_test, preds, average=\"macro\")\n",

                    "    rows.append((th, f1_nr, f1_macro))\n",

                    "\n",

                    "th_df = pd.DataFrame(rows, columns=[\"Seuil\", \"F1 needs repair\", \"F1 Macro\"])\n",

                    "print(th_df.to_string(index=False))\n",

                    "\n",

                    "precision, recall, _ = precision_recall_curve(y_true_repair, p_repair)\n",

                    "plt.figure(figsize=(8, 5))\n",

                    "plt.plot(recall, precision, label=\"Precision-Recall\", color=\"#8e44ad\")\n",

                    "plt.xlabel(\"Recall\")\n",

                    "plt.ylabel(\"Precision\")\n",

                    "plt.title(\"Courbe PR - needs repair (champion recall)\")\n",

                    "plt.legend()\n",

                    "plt.show()\n",

                ],

                "outputs": [],

                "execution_count": None,

            },

            {

                "cell_type": "markdown",

                "metadata": {},

                "source": [

                    "## 4. Selection du modele de production\n\n"

                    "Deux champions : F1-Macro (analytics) et recall `needs repair` (alertes terrain).\n\n"

                    "Voir `reports/model_card.md` et `reports/sprint_05_metrics.json`."

                ],

            },

            {

                "cell_type": "code",

                "metadata": {},

                "source": [

                    "print(\"Champions Sprint 5 :\")\n",

                    "for k, v in results[\"champions\"].items():\n",

                    "    print(f\"  {k}: {v}\")\n",

                    "print(\"\\nRecommandation :\", results[\"recommendation\"])\n",

                ],

                "outputs": [],

                "execution_count": None,

            },

        ],

    }

    # Fix markdown cell 4 - can't use f-string with results at build time

    nb["cells"][8]["source"] = [

        "## 4. Selection du modele de production\n\n"

        "Deux champions : F1-Macro (analytics) et recall `needs repair` (alertes terrain).\n\n"

        "Voir `reports/model_card.md` et `reports/sprint_05_metrics.json`."

    ]

    save(path, nb)





def fix_mqtt_test() -> None:

    path = NB / "06_mqtt_test.ipynb"

    nb = load(path)

    for cell in nb["cells"]:

        if cell["cell_type"] != "code":

            continue

        src = "".join(cell.get("source", []))

        if "telemetry.db" in src or "DB_PATH = PROJECT_ROOT" in src and "PYTHON" in src:

            cell["source"] = [

                "import subprocess\n",

                "import sys\n",

                "import time\n",

                "import sqlite3\n",

                "from pathlib import Path\n",

                "\n",

                "PROJECT_ROOT = Path(\"..\").resolve()\n",

                "DB_PATH = PROJECT_ROOT / \"data\" / \"mqtt\" / \"aquasense.db\"\n",

                "PYTHON = sys.executable\n",

            ]

        if "simulator.py" in src and "Popen" in src:

            cell["source"] = [

                "print(\"Demarrage consumer MQTT...\")\n",

                "cons_proc = subprocess.Popen(\n",

                "    [PYTHON, \"-m\", \"src.mqtt_consumer\"],\n",

                "    cwd=str(PROJECT_ROOT),\n",

                ")\n",

                "print(\"Demarrage simulateur (5 pompes, 12 s)...\")\n",

                "sim_proc = subprocess.Popen(\n",

                "    [PYTHON, \"-m\", \"src.simulator\", \"--pumps\", \"5\", \"--interval\", \"2\"],\n",

                "    cwd=str(PROJECT_ROOT),\n",

                ")\n",

                "time.sleep(12)\n",

                "print(\"Pause terminee. Arret des processus...\")\n",

                "sim_proc.terminate()\n",

                "cons_proc.terminate()\n",

            ]

        if "sqlite3.connect" in src and "SELECT COUNT" in src:

            cell["source"] = [

                "if not DB_PATH.exists():\n",

                "    print(f\"Base absente : {DB_PATH}\")\n",

                "else:\n",

                "    conn = sqlite3.connect(DB_PATH)\n",

                "    t = conn.execute(\"SELECT COUNT(*) FROM telemetry\").fetchone()[0]\n",

                "    p = conn.execute(\"SELECT COUNT(*) FROM predictions\").fetchone()[0]\n",

                "    print(f\"telemetry={t}, predictions={p}\")\n",

                "    conn.close()\n",

            ]

        if "df_telemetry" in src:

            cell["source"] = [

                "import pandas as pd\n",

                "\n",

                "if not DB_PATH.exists():\n",

                "    print(\"Pas de donnees.\")\n",

                "else:\n",

                "    conn = sqlite3.connect(DB_PATH)\n",

                "    df_telemetry = pd.read_sql_query(\n",

                "        \"SELECT pump_id, timestamp, pressure, vibration, flow FROM telemetry \"\n",

                "        \"ORDER BY timestamp DESC LIMIT 50\",\n",

                "        conn,\n",

                "    )\n",

                "    preds = pd.read_sql_query(\n",

                "        \"SELECT pump_id, timestamp, prediction FROM predictions \"\n",

                "        \"ORDER BY timestamp DESC LIMIT 20\",\n",

                "        conn,\n",

                "    )\n",

                "    conn.close()\n",

                "    print(\"Dernieres telemetries :\")\n",

                "    print(df_telemetry.head(5).to_string(index=False))\n",

                "    print(\"\\nDernieres predictions :\")\n",

                "    print(preds.head(5).to_string(index=False))\n",

            ]

        if "sim_proc.terminate()" in src and "Processus" in src:

            cell["source"] = [

                "try:\n",

                "    sim_proc.terminate()\n",

                "    cons_proc.terminate()\n",

                "    print(\"Processus arretes.\")\n",

                "except NameError:\n",

                "    print(\"Processus deja arretes.\")\n",

            ]

    save(path, nb)





def sync_colab_copies() -> None:

    """Copie les notebooks executes vers AquaSense_S4_Colab pour coherence."""

    if not COLAB_NB.exists():

        return

    for name in ["04_dl_mlp.ipynb", "04_dl_advanced.ipynb", "05_dl_colab_tune.ipynb"]:

        src = NB / name

        if src.exists():

            shutil.copy2(src, COLAB_NB / name)





def main() -> None:

    fix_colab_mlp_run()

    fix_dl_advanced()

    fix_dl_tuning_export()

    fix_comparison_final()

    fix_mqtt_test()

    sync_colab_copies()

    print("Notebooks prepares.")





if __name__ == "__main__":

    main()


