import os
from pathlib import Path

LATEX_HEADER = r"""
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{float}
\usepackage{titlesec}
\usepackage{caption}
\usepackage{fancyhdr}
\usepackage{hyperref}
\usepackage{amsmath}
\usepackage{listings}
\usepackage{parskip}
\usepackage{xcolor}
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{Engineering Design Report}
\titleformat{\section}{\large\bfseries}{\thesection.}{1em}{}
\titleformat{\subsection}{\normalsize\bfseries}{\thesubsection.}{1em}{}
\captionsetup[figure]{labelfont=bf}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=cyan
}
\begin{document}
"""

LATEX_FOOTER = r"""
\end{document}
"""

def escape_latex(text):
    return text.replace('_', r'\_')

def render_folder_to_latex(folder_path):
    content = ""
    for item in sorted(os.listdir(folder_path)):
        item_path = os.path.join(folder_path, item)
        title = escape_latex(Path(item).stem.replace('_', ' ').title())

        if os.path.isdir(item_path):
            content += f"\n\\section{{{title}}}\n"
            content += render_folder_to_latex(item_path)
        elif item.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf')):
            content += f"""
\\begin{figure}[H]
    \\centering
    \\includegraphics[width=0.9\\textwidth]{{{item_path.replace('\\', '/')}}}
    \\caption{{{title}}}
\\end{figure}
"""
        elif item.lower().endswith(('.txt', '.md')):
            with open(item_path, 'r', encoding='utf-8') as f:
                text = escape_latex(f.read())
                content += f"\n\\subsection*{{{title}}}\n\\begin{{flushleft}}\n{text}\n\\end{{flushleft}}\n"

    return content

def generate_report(project_folder):
    project_title = Path(project_folder).name.replace('_', ' ')
    tex_output = LATEX_HEADER
    tex_output += f"\\begin{{center}}\\Huge\\textbf{{{escape_latex(project_title)}}}\\end{{center}}\n\\vspace{{1cm}}\n"

    # Render each section
    for section_num in range(1, 10):
        section_folder = f"{section_num}_"
        matches = [f for f in os.listdir(project_folder) if f.startswith(section_folder)]
        if matches:
            section_path = os.path.join(project_folder, matches[0])
            tex_output += render_folder_to_latex(section_path)

    tex_output += LATEX_FOOTER

    # Write to file
    with open("design_report.tex", "w", encoding="utf-8") as f:
        f.write(tex_output)

    print("✅ LaTeX file generated: design_report.tex")
    print("📦 Now run: pdflatex design_report.tex")

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Your Project Folder")
    if folder:
        generate_report(folder)
