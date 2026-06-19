"""Genere main.tex + zip Overleaf (noms ASCII, compatible pdfLaTeX)."""
from __future__ import annotations

import re
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
BUILD = REPORTS / "overleaf_build"
ZIP_OUT = REPORTS / "AquaSense_Overleaf.zip"

# Captures ecran -> noms ASCII (apostrophes/espaces cassent LaTeX)
IMAGE_RENAME = {
    "Capture d'écran 2026-06-19 121202.png": "fig_mqtt_consumer.png",
    "Capture d'écran 2026-06-19 121255.png": "fig_mqtt_simulator.png",
    "Capture d'écran 2026-06-19 145330.png": "fig_dashboard_overview.png",
    "Capture d'écran 2026-06-19 145829.png": "fig_dashboard_alerts.png",
    "Capture d'écran 2026-06-19 150248.png": "fig_dashboard_pump.png",
    "Capture d'écran 2026-06-19 150314.png": "fig_dashboard_models1.png",
    "Capture d'écran 2026-06-19 150330.png": "fig_dashboard_models2.png",
    "Capture d'écran 2026-06-19 150357.png": "fig_dashboard_about.png",
    "sprint08_pytest_all_passed.png": "fig_pytest_all.png",
    "sprint08_pytest_integration.png": "fig_pytest_mqtt.png",
}

SPRINT_FIGS = [
    "sprint_03_confusion_matrices.png",
    "sprint_03_feature_importance.png",
    "sprint_04_training_history.png",
    "sprint_04_confusion_matrix.png",
]

PREAMBLE = r"""\documentclass[11pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{lmodern}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{grffile}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{colortbl}
\usepackage{hyperref}
\usepackage[table]{xcolor}
\usepackage{listings}
\usepackage{float}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{ragged2e}
\usepackage{microtype}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{tikz}

% --- Charte couleurs EHTP / AquaSense ---
\definecolor{EHTPPrimary}{HTML}{1B4F72}
\definecolor{EHTPSecondary}{HTML}{2874A6}
\definecolor{EHTPAccent}{HTML}{17A589}
\definecolor{EHTPText}{HTML}{2C3E50}
\definecolor{EHTPLight}{HTML}{F4F7F9}
\definecolor{EHTPTableHead}{HTML}{D6EAF8}
\definecolor{EHTPAlert}{HTML}{C0392B}

\usepackage{microtype}

\geometry{margin=2.5cm}
\color{EHTPText}
\setlength{\parskip}{0.45em}
\setlength{\parindent}{0pt}
\hypersetup{
  colorlinks=true,
  linkcolor=EHTPSecondary,
  urlcolor=EHTPAccent,
  citecolor=EHTPPrimary
}
\graphicspath{{reports/}{reports/image/}}

% --- Titres : pas de "Chapitre N" (le titre Sprint 0 / Introduction suffit) ---
\titleformat{\chapter}[display]
  {\normalfont\huge\bfseries\color{EHTPPrimary}}
  {}
  {0pt}
  {\Huge\color{EHTPPrimary}}
  [\vspace{0.4em}{\color{EHTPAccent}\titlerule[1.2pt]}\vspace{0.6em}]

\titleformat{name=\chapter,numberless}[display]
  {\normalfont\huge\bfseries\color{EHTPPrimary}}
  {}
  {0pt}
  {\Huge\color{EHTPPrimary}}
  [\vspace{0.5em}{\color{EHTPAccent}\titlerule[1.5pt]}]

\titleformat{\section}
  {\Large\bfseries\color{EHTPSecondary}}
  {\thesection}{1em}{}
\titleformat{\subsection}
  {\large\bfseries\color{EHTPPrimary}}
  {\thesubsection}{1em}{}
\titleformat{\subsubsection}
  {\normalsize\bfseries\color{EHTPSecondary}}
  {\thesubsubsection}{1em}{}

% --- En-tetes / pieds de page ---
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\color{EHTPSecondary}\nouppercase\leftmark}
\fancyhead[R]{}
\fancyfoot[C]{\small\color{EHTPPrimary}\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{EHTPAccent}\leaders\hrule height \headrulewidth\hfill}}
\renewcommand{\footrule}{\hbox to\headwidth{\color{EHTPAccent}\leaders\hrule height \footrulewidth\hfill}}

\captionsetup{
  labelfont={bf,color=EHTPPrimary},
  textfont={color=EHTPText},
  skip=8pt
}

\lstset{
  basicstyle=\ttfamily\small\color{EHTPText},
  breaklines=true,
  frame=single,
  rulecolor=\color{EHTPSecondary},
  backgroundcolor=\color{EHTPLight},
}

\setlist[itemize]{label=\textcolor{EHTPAccent}{\textbullet}}
\setlist[enumerate]{label=\textcolor{EHTPPrimary}{\arabic*.}}

% --- Page de garde coloree ---
\newcommand{\makecoverpage}{%
\begin{titlepage}
  \begin{tikzpicture}[remember picture,overlay]
    \fill[EHTPPrimary] (current page.north west) rectangle ([yshift=-7.2cm]current page.north east);
    \fill[EHTPLight] ([yshift=-7.2cm]current page.north west) rectangle (current page.south east);
    \draw[EHTPAccent,line width=2pt] ([yshift=-7.2cm]current page.west) -- ([yshift=-7.2cm]current page.east);
  \end{tikzpicture}
  \vspace*{1.2cm}
  {\color{white}\textbf{\large École Hassania des Travaux Publics (EHTP)}}\\[0.5cm]
  {\color{white}\large Projet Machine Learning}\\[2.8cm]
  \begin{flushleft}
  {\fontsize{28}{32}\selectfont\bfseries\color{EHTPPrimary}AquaSense AI}\\[0.6cm]
  {\Large\color{EHTPSecondary}Maintenance prédictive des forages et points d'eau}\\[0.3cm]
  {\large\color{EHTPAccent}en contexte marocain}\\[1.8cm]
  {\Large\bfseries\color{EHTPPrimary}Rapport de projet}\\[2.5cm]
  \begin{minipage}{0.85\textwidth}
  \color{EHTPText}
  \textbf{Équipe :}\\[0.2cm]
  TRAORE Fanogo Mohamed\\
  NADAHE Mohamed\\[0.8cm]
  \textbf{Encadrement :} Dr. Rym Nassih\\[0.8cm]
  \textbf{Date :} Juin 2026
  \end{minipage}
  \end{flushleft}
\end{titlepage}
}

\begin{document}
\makecoverpage
\tableofcontents
\newpage
"""
LATEX_END = r"""
\end{document}
"""


def fix_tex_body(body: str) -> str:
    """Post-traitement pour pdfLaTeX sur Overleaf."""
    body = body.replace("≥", r"$\geq$")
    body = body.replace("≤", r"$\leq$")
    body = body.replace("→", r"$\rightarrow$")
    for old, new in IMAGE_RENAME.items():
        body = body.replace(f"image/{old}", f"image/{new}")
        body = body.replace(old, new)
    body = re.sub(
        r"\\includegraphics(\[[^\]]*\])\{([^}]+)\}",
        lambda m: f"\\includegraphics{m.group(1)}{{{m.group(2).replace(r'\_', '_')}}}",
        body,
    )
    # En-tetes tableaux colores
    body = re.sub(
        r"(\\toprule\n)([^\\]+ & [^\n]+ \\\\)",
        r"\1\\rowcolor{EHTPTableHead}\2",
        body,
    )
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body


def prepare_build_dir() -> Path:
    if BUILD.exists():
        shutil.rmtree(BUILD)
    img_out = BUILD / "reports" / "image"
    img_out.mkdir(parents=True)

    for name in SPRINT_FIGS:
        src = REPORTS / name
        if src.exists():
            shutil.copy2(src, BUILD / "reports" / name)

    src_img = REPORTS / "image"
    for old_name, new_name in IMAGE_RENAME.items():
        src = src_img / old_name
        if src.exists():
            shutil.copy2(src, img_out / new_name)

    return BUILD


def build_main_tex() -> str:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from md_to_latex_report import convert_md_to_latex

    md = (REPORTS / "AquaSense_AI_Report.md").read_text(encoding="utf-8")
    body = fix_tex_body(convert_md_to_latex(md))
    return PREAMBLE + body + LATEX_END


def create_zip() -> None:
    prepare_build_dir()
    main_tex = build_main_tex()
    (BUILD / "main.tex").write_text(main_tex, encoding="utf-8")

    with zipfile.ZipFile(ZIP_OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in BUILD.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(BUILD).as_posix())
        readme = (
            "AquaSense AI - Overleaf\n\n"
            "1. Upload ce zip sur overleaf.com\n"
            "2. Le fichier principal est main.tex (deja selectionne par defaut)\n"
            "3. Compiler avec pdfLaTeX\n"
            "4. Telecharger le PDF\n"
        )
        zf.writestr("LISEZMOI.txt", readme)

    print(f"OK  {ZIP_OUT} ({ZIP_OUT.stat().st_size / 1024 / 1024:.2f} Mo)")
    print(f"    main.tex + {len(list((BUILD / 'reports').rglob('*')))} fichiers reports/")


if __name__ == "__main__":
    create_zip()
