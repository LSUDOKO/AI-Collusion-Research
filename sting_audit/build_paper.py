"""Build the submission PDF: report/report_filled.md -> report/paper.html -> report/Sting_Audits_Apart_Collusion_Sprint.pdf

python-markdown + headless Chrome (no LaTeX). Research-paper layout: STIX Two Text (journal serif), booktabs-style tables,
numbered figure captions, page numbers, clickable links. Front matter = the five lines after the title in report.md:
author, affiliation, venue, links (markdown), blank. Figures are referenced relative to report/.
"""
import re
import shutil
import subprocess

import markdown

from sting_audit.paths import REPO

REPORT_DIR = REPO / "report"
MD = REPORT_DIR / "report_filled.md"
HTML = REPORT_DIR / "paper.html"
PDF = REPORT_DIR / "Sting_Audits_Apart_Collusion_Sprint.pdf"
TITLE_SHORT = "Sting Audits for LLM Agents"

FONTS = ("https://fonts.googleapis.com/css2?family=STIX+Two+Text:ital,wght@0,400;0,600;0,700;1,400;1,600"
         "&family=Inter+Tight:wght@500;600;700&family=JetBrains+Mono:wght@400&display=block")

CSS = f"""
@page {{ size: A4; margin: 22mm 20mm 20mm 20mm;
  @top-center {{ content: "{TITLE_SHORT}"; font-family: 'STIX Two Text', serif; font-style: italic; font-size: 8.5pt; color: #666; }}
  @bottom-center {{ content: counter(page); font-family: 'STIX Two Text', serif; font-size: 9pt; color: #333; }} }}
@page :first {{ @top-center {{ content: none; }} }}
html {{ font-size: 10.6pt; }}
body {{ font-family: 'STIX Two Text', 'Noto Serif', 'Times New Roman', serif; line-height: 1.36; color: #111; margin: 0;
       font-variant-numeric: lining-nums; -webkit-font-smoothing: antialiased; }}
a {{ color: #1f4e8c; text-decoration: none; }}
h1.title {{ font-size: 19pt; line-height: 1.22; margin: 4mm 6mm 5pt 6mm; text-align: center; font-weight: 700; letter-spacing: -0.1pt; }}
.author {{ text-align: center; font-size: 12pt; margin-top: 8pt; font-weight: 600; }}
.affil {{ text-align: center; font-size: 10pt; font-style: italic; color: #333; margin-top: 1pt; }}
.venue {{ text-align: center; font-size: 9.4pt; color: #333; margin-top: 6pt; }}
.links {{ text-align: center; font-size: 9pt; margin: 6pt 0 12pt 0; font-family: 'Inter Tight', sans-serif; }}
.links a {{ display: inline-block; margin: 0 5pt; padding: 1.5pt 7pt; border: 0.7pt solid #9db3d4; border-radius: 9pt; }}
.abstract {{ margin: 6pt 9mm 12pt 9mm; font-size: 9.8pt; }}
.abstract .ah {{ text-align: center; font-weight: 700; font-size: 10.5pt; margin-bottom: 3pt; font-variant: small-caps; letter-spacing: 0.5pt; }}
.abstract p {{ text-indent: 0; }}
h2 {{ font-size: 12.6pt; margin: 15pt 0 5pt 0; font-weight: 700; page-break-after: avoid; }}
h3 {{ font-size: 10.8pt; margin: 10pt 0 3pt 0; font-weight: 700; font-style: italic; page-break-after: avoid; }}
p {{ margin: 0 0 6pt 0; text-align: justify; hyphens: auto; orphans: 3; widows: 3; }}
strong {{ font-weight: 700; }}
table {{ border-collapse: collapse; margin: 8pt auto 10pt auto; font-size: 8.9pt; width: 100%; page-break-inside: avoid;
        border-top: 1.3pt solid #111; border-bottom: 1.3pt solid #111; }}
thead th {{ border-bottom: 0.7pt solid #111; font-weight: 700; text-align: left; padding: 3pt 5pt; }}
td {{ padding: 2.4pt 5pt; text-align: left; vertical-align: top; }}
tbody tr:nth-child(even) td {{ background: #f7f7f7; }}
.tcap {{ font-size: 9pt; margin: 8pt 0 0 0; text-align: left; }}
figure {{ margin: 10pt 0 10pt 0; text-align: center; page-break-inside: avoid; }}
figure img {{ max-width: 100%; max-height: 98mm; }}
figure.narrow img {{ max-width: 62%; }}
figcaption {{ font-size: 9pt; text-align: justify; margin: 5pt 2mm 0 2mm; line-height: 1.3; }}
figcaption b {{ font-weight: 700; }}
code {{ font-family: 'JetBrains Mono', 'DejaVu Sans Mono', monospace; font-size: 8.2pt; background: #f3f4f6; padding: 0 2pt; border-radius: 2pt; }}
pre {{ background: #f6f8fa; border: 0.6pt solid #d0d7de; border-radius: 3pt; padding: 6pt 8pt; font-size: 7.9pt; white-space: pre-wrap; page-break-inside: avoid; }}
pre code {{ background: none; padding: 0; }}
blockquote {{ border-left: 2pt solid #9db3d4; margin: 6pt 0; padding: 2pt 9pt; color: #333; font-size: 9.6pt; }}
ul, ol {{ margin: 0 0 6pt 16pt; padding: 0; }} li {{ margin-bottom: 2pt; text-align: justify; }}
.refs p {{ font-size: 8.9pt; text-align: left; margin-bottom: 3.5pt; padding-left: 14pt; text-indent: -14pt; }}
.appendix {{ font-size: 9.6pt; }}
.appendix > h2:first-child {{ page-break-before: always; }}
.refs > h2 {{ page-break-before: auto; }}
"""


def _front(lines):
    title = lines[0].lstrip("# ").strip()
    author, affil, venue, links = (lines[i].strip() if len(lines) > i else "" for i in (2, 3, 4, 5))
    links_html = markdown.markdown(links)[3:-4] if links else ""
    return title, (f'<h1 class="title">{title}</h1><div class="author">{author}</div><div class="affil">{affil}</div>'
                   f'<div class="venue">{venue}</div><div class="links">{links_html}</div>'), "\n".join(lines[6:])


def md_to_html(md_text):
    title, front, body = _front(md_text.splitlines())

    def fig(m):
        cap, src = m.group(1), m.group(2)
        cls = ' class="narrow"' if "narrow" in src or "sting_benign" in src else ""
        cap = re.sub(r"^(Figure [A-Z]?\d+\.)", r"<b>\1</b>", cap)
        return f'<figure{cls}><img src="{src}" alt=""><figcaption>{cap}</figcaption></figure>'
    body = re.sub(r"^!\[(.*?)\]\((.*?)\)\s*$", fig, body, flags=re.M)
    html = markdown.markdown(body, extensions=["tables", "fenced_code", "sane_lists", "attr_list", "smarty"])
    # table captions written as a paragraph starting with "**Table N." directly before the table
    html = re.sub(r"<p><strong>(Table [A-Z]?\d+\.)</strong>(.*?)</p>", r'<p class="tcap"><b>\1</b>\2</p>', html)
    # autolink bare URLs (references, appendix)
    html = re.sub(r'(?<![="\'>])(https?://[^\s<>()]+[^\s<>().,;])', r'<a href="\1">\1</a>', html)
    html = html.replace("<h2>Abstract</h2>", '<div class="abstract"><div class="ah">Abstract</div>', 1)
    html = html.replace("<h2>1. Introduction</h2>", "</div><h2>1. Introduction</h2>", 1)
    html = html.replace("<h2>References</h2>", '<div class="refs"><h2>References</h2>', 1)
    html = html.replace("<h2>Appendix A.", '</div><div class="appendix"><h2>Appendix A.', 1)
    html += "</div>"
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>'
            f'<link rel="stylesheet" href="{FONTS}"><style>{CSS}</style></head><body>{front}{html}</body></html>')


def build():
    HTML.write_text(md_to_html(MD.read_text()))
    chrome = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        print("no chrome found; HTML written only"); return HTML
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer", "--virtual-time-budget=10000",
           f"--print-to-pdf={PDF}", f"file://{HTML}"]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    print("wrote", PDF, PDF.stat().st_size, "bytes")
    return PDF


if __name__ == "__main__":
    build()
