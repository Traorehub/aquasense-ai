"""Convert reports/AquaSense_AI_Report.md to LaTeX for PDF compilation."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "reports" / "AquaSense_AI_Report.md"
TEX_PATH = ROOT / "reports" / "AquaSense_AI_Report.tex"

LATEX_PREAMBLE = r"""\documentclass[11pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[french]{babel}
\usepackage{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{float}
\usepackage{caption}
\usepackage{enumitem}

\geometry{margin=2.5cm}
\hypersetup{colorlinks=true, linkcolor=blue!50!black, urlcolor=blue!60!black}
\graphicspath{{reports/}{reports/image/}}

\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  frame=single,
  backgroundcolor=\color{gray!8},
}

\title{AquaSense AI\\[0.4em]\large Rapport académique final\\Maintenance prédictive des forages et points d'eau}
\author{TRAORE Fanogo Mohamed \and NADAHE Mohamed\\EHTP --- Master Ingénierie Géomatique S4\\Encadrement : Dr. Rym Nassih}
\date{Juin 2026}

\begin{document}
\maketitle
\tableofcontents
\newpage
"""

LATEX_END = r"""
\end{document}
"""


def escape_latex(text: str) -> str:
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        text = text.replace(k, v)
    return text


def inline_format(text: str) -> str:
    text = escape_latex(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", text)
    text = re.sub(r"\*(.+?)\*", r"\\textit{\1}", text)
    text = re.sub(r"`([^`]+)`", r"\\texttt{\1}", text)
    return text


def latex_image_path(path: str) -> str:
    """Chemin fichier pour \\includegraphics (sans echapper les underscores)."""
    path = path.replace("%20", " ").replace("Capture%20d'écran", "Capture d'écran")
    for old, new in {
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
    }.items():
        path = path.replace(old, new)
    return path


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        if not all(set(c) <= set("-: ") for c in row):
            rows.append(row)
        i += 1
    if not rows:
        return "", start

    col_count = max(len(r) for r in rows)
    if col_count <= 4:
        w = 0.9 / col_count
        cols = "".join(
            f">{{\\raggedright\\arraybackslash}}p{{{w:.2f}\\textwidth}}" for _ in range(col_count)
        )
        col_spec = "@{}" + cols + "@{}"
    else:
        col_spec = "@{}" + ("l" * col_count) + "@{}"
    out = ["{\\small", "\\begin{longtable}{" + col_spec + "}", "\\toprule"]
    for idx, row in enumerate(rows):
        while len(row) < col_count:
            row.append("")
        out.append(" & ".join(inline_format(c) for c in row) + r" \\")
        if idx == 0:
            out.append("\\midrule")
    out.extend(["\\bottomrule", "\\end{longtable}", "}", ""])
    return "\n".join(out), i


def convert_md_to_latex(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    skip_until = 0

    while i < len(lines):
        line = lines[i]

        if i < skip_until:
            i += 1
            continue

        # skip duplicate title block before resume
        if line.startswith("# AquaSense AI"):
            i += 1
            continue
        if line.strip() == "---":
            i += 1
            continue
        if line.startswith("**Maintenance prédictive"):
            i += 1
            continue
        if line.startswith("|") and i < 25:
            # skip header metadata table
            while i < len(lines) and (lines[i].strip().startswith("|") or lines[i].strip() == ""):
                i += 1
            continue
        if line.startswith("## Table des matières"):
            while i < len(lines) and not lines[i].startswith("## 1."):
                i += 1
            continue

        if line.startswith("```"):
            lang = line.strip("` ").strip()
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            body = "\n".join(escape_latex(c) for c in code_lines)
            out.append("\\begin{lstlisting}")
            out.append(body)
            out.append("\\end{lstlisting}")
            continue

        if line.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", line.strip())
            if m:
                alt, path = m.group(1), m.group(2)
                path = latex_image_path(path)
                out.append("\\begin{figure}[htbp]")
                out.append("\\centering")
                out.append(f"\\includegraphics[width=0.92\\linewidth]{{{path}}}")
                out.append(f"\\caption{{{inline_format(alt)}}}")
                out.append("\\end{figure}")
            i += 1
            continue

        if line.startswith("|"):
            block, i = parse_table(lines, i)
            out.append(block)
            continue

        if line.startswith("### "):
            sub = re.sub(r"^\d+\.\d+\s*", "", line[4:].strip())
            out.append(f"\\subsection{{{inline_format(sub)}}}")
            i += 1
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            # Sprint : titre explicite Sprint N (sans numero de chapitre LaTeX decale)
            m_sprint = re.match(r"^\d+\.\s*Sprint\s+(\d+)\s*:\s*(.+)$", title, re.I)
            if m_sprint:
                sn, rest = m_sprint.group(1), m_sprint.group(2)
                if sn == "0":
                    out.append("\\part{Réalisation technique}")
                out.append("\\clearpage")
                out.append(
                    f"\\chapter[Sprint {sn}]{{Sprint {sn} : {inline_format(rest)}}}"
                )
                out.append(f"\\label{{ch:sprint{sn}}}")
                i += 1
                continue
            # Chapitres generaux : retirer le prefixe numerique markdown (1., 2., ...)
            title = re.sub(r"^\d+\.\s*", "", title)
            if title == "Résumé exécutif":
                out.append("\\chapter*{Résumé exécutif}")
                out.append("\\addcontentsline{toc}{chapter}{Résumé exécutif}")
            elif title.startswith("Sprint "):
                out.append("\\clearpage")
                out.append(f"\\chapter{{{inline_format(title)}}}")
            else:
                out.append(f"\\chapter{{{inline_format(title)}}}")
            i += 1
            continue

        if line.startswith("> "):
            out.append("\\begin{quote}")
            out.append(inline_format(line[2:].strip()))
            out.append("\\end{quote}")
            i += 1
            continue

        if line.strip() == "":
            out.append("")
            i += 1
            continue

        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"\\item {inline_format(lines[i][2:].strip())}")
                i += 1
            out.append("\\begin{itemize}")
            out.extend(items)
            out.append("\\end{itemize}")
            continue

        out.append(inline_format(line.strip()))
        i += 1

    return re.sub(r"\n{3,}", "\n\n", "\n\n".join(out))


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    body = convert_md_to_latex(md)
    tex = LATEX_PREAMBLE + body + LATEX_END
    TEX_PATH.write_text(tex, encoding="utf-8")
    print(f"LaTeX généré : {TEX_PATH} ({TEX_PATH.stat().st_size:,} octets)")


if __name__ == "__main__":
    main()
