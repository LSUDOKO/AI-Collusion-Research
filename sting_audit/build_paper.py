"""Build the submission PDF: report/report_filled.md -> report/paper.html (academic two-column-ish CSS) -> report/Sting_Audits_Apart_Collusion_Sprint.pdf

Uses python-markdown + headless Chrome (no LaTeX needed). Figures are referenced relative to report/.
"""
import re
import subprocess
import shutil
from pathlib import Path

import markdown

from sting_audit.paths import REPO

REPORT_DIR = REPO / "report"
MD = REPORT_DIR / "report_filled.md"
HTML = REPORT_DIR / "paper.html"
PDF = REPORT_DIR / "Sting_Audits_Apart_Collusion_Sprint.pdf"

CSS = """
@page { size: A4; margin: 20mm 18mm 20mm 18mm; }
html { font-size: 10.5pt; }
body { font-family: "Source Serif 4", "Noto Serif", Georgia, "Times New Roman", serif; line-height: 1.38; color: #111; max-width: 174mm; margin: 0 auto; }
h1 { font-size: 20pt; line-height: 1.2; margin: 0 0 6pt 0; text-align: center; font-weight: 700; }
.authors { text-align: center; font-size: 10.5pt; margin-bottom: 2pt; }
.venue { text-align: center; font-size: 9.5pt; color: #333; margin-bottom: 14pt; }
h2 { font-size: 13pt; margin: 16pt 0 6pt 0; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11pt; margin: 12pt 0 4pt 0; }
p { margin: 0 0 7pt 0; text-align: justify; hyphens: auto; }
.abstract { margin: 0 10mm 10pt 10mm; font-size: 10pt; }
.abstract p::before { content: "Abstract. "; font-weight: 700; }
table { border-collapse: collapse; margin: 8pt auto; font-size: 9pt; width: 100%; }
th, td { border-top: 1px solid #bbb; border-bottom: 1px solid #bbb; padding: 3pt 5pt; text-align: left; vertical-align: top; }
th { background: #f3f3f3; font-weight: 600; }
figure { margin: 10pt 0; text-align: center; page-break-inside: avoid; }
figure img { max-width: 100%; max-height: 95mm; }
figcaption { font-size: 9pt; text-align: justify; margin-top: 4pt; color: #222; }
code { font-family: "JetBrains Mono", "DejaVu Sans Mono", monospace; font-size: 8.6pt; background: #f4f4f4; padding: 0 2pt; }
pre { background: #f6f6f6; border: 1px solid #ddd; padding: 6pt; font-size: 8.4pt; overflow-x: auto; white-space: pre-wrap; }
blockquote { border-left: 3px solid #bbb; margin: 6pt 0; padding: 2pt 8pt; color: #333; font-size: 9.6pt; }
ul, ol { margin: 0 0 7pt 18pt; padding: 0; } li { margin-bottom: 2pt; }
.refs p { font-size: 9pt; text-align: left; margin-bottom: 4pt; padding-left: 14pt; text-indent: -14pt; }
.appendix h2 { page-break-before: always; }
.pagebreak { page-break-before: always; }
.small { font-size: 9pt; }
"""


def md_to_html(md_text):
    # author/venue lines: the two lines after the title
    lines = md_text.splitlines()
    title = lines[0].lstrip("# ").strip()
    authors = lines[2].strip() if len(lines) > 2 else ""
    venue = lines[3].strip() if len(lines) > 3 else ""
    body = "\n".join(lines[4:])
    # figures: lines like ![Caption](figures/x.png) -> <figure>
    def fig(m):
        return f'<figure><img src="{m.group(2)}" alt=""><figcaption>{m.group(1)}</figcaption></figure>'
    body = re.sub(r"!\[(.*?)\]\((.*?)\)", fig, body)
    html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists", "attr_list"])
    # wrap abstract
    html = html.replace("<h2>Abstract</h2>", '<div class="abstract">', 1)
    html = html.replace("<h2>1. Introduction</h2>", '</div><h2>1. Introduction</h2>', 1)
    html = html.replace("<h2>References</h2>", '<div class="refs"><h2>References</h2>', 1)
    html = html.replace("<h2>Appendix A.", '</div><div class="appendix"><h2>Appendix A.', 1)
    html += "</div>"
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head>
<body><h1>{title}</h1><div class="authors">{authors}</div><div class="venue">{venue}</div>{html}</body></html>"""


def build():
    md_text = MD.read_text()
    HTML.write_text(md_to_html(md_text))
    chrome = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("no chrome found; HTML written only"); return HTML
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
           f"--print-to-pdf={PDF}", f"file://{HTML}"]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    print("wrote", PDF, PDF.stat().st_size, "bytes")
    return PDF


if __name__ == "__main__":
    build()
