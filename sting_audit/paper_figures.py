"""Publication figures for the PDF (white theme, consistent typography). Writes report/paper_figs/*.png.

  fig_architecture.png   system architecture of the study (SVG rendered by headless Chrome at 2x)
  fig_protocol.png       one turn of the open-channel Liar's Bar game (SVG)
  fig_acceptance.png     (a) pooled acceptance by offer, Wilson 95% CI; (b) 12 configs x 4 offers heatmap
  fig_sting_benign.png   sting score vs benign acceptance, one point per configuration (main probe result)
  fig_all_models.png     acceptance pooled over personas, Groq roster + exploratory Claude models
  shot_private_channel.png, shot_probe_replies.png, shot_evidence.png   light-theme screenshots built from the logs
Every plotted number is read from results/tables/ (written by analysis.py / probe_extra.py).
"""
import json
import shutil
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

from sting_audit.paths import REPO, TABLES

OUT = REPO / "report" / "paper_figs"
CHROME = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or shutil.which("chromium")
FONT = "Inter Tight"
INK, MUTED, RULE = "#1a1a1a", "#555555", "#c8c8c8"
OFFER = {"S0": ("#7f7f7f", "S0 designer tool"), "S1": ("#c0392b", "S1 direct pact"),
         "S2": ("#e08e0b", "S2 indirect hint"), "S3": ("#2e86c1", "S3 benign request")}
MODEL_ORDER = ["allam-7b", "gpt-oss-20b", "gpt-oss-120b", "qwen3.8-27b"]
MODEL_LABEL = {"allam-7b": "allam-2-7b", "gpt-oss-20b": "gpt-oss-20b", "gpt-oss-120b": "gpt-oss-120b", "qwen3.8-27b": "qwen3.8-27b",
               "claude-haiku": "Claude\nHaiku 5.5*", "claude-sonnet": "Claude\nSonnet 5.5*"}
PERSONAS = ["neutral", "competitive", "fair"]
MARK = {"allam-7b": "o", "gpt-oss-20b": "s", "gpt-oss-120b": "^", "qwen3.8-27b": "D"}
PCOL = {"neutral": "#4c4c4c", "competitive": "#c0392b", "fair": "#1e8449"}

plt.rcParams.update({"font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 9, "axes.edgecolor": "#333", "axes.linewidth": 0.8,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.titlesize": 9.5, "axes.titleweight": "bold", "legend.frameon": False,
                     "savefig.dpi": 300, "figure.dpi": 150})


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / name, bbox_inches="tight", facecolor="white", pad_inches=0.04)
    plt.close(fig)
    print("fig ->", OUT / name)


def render_html(body, name, width, height, css=""):
    """Render an HTML/SVG snippet to a tight, white-background PNG at 2x."""
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"_{name}.html"
    p.write_text(f"<!doctype html><html><head><meta charset='utf-8'>"
                 f"<link href='https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=block' rel='stylesheet'>"
                 f"<style>html,body{{margin:0;background:#fff}} body{{font-family:'Inter Tight',sans-serif;color:{INK}}}{css}</style></head><body>{body}</body></html>")
    out = OUT / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--virtual-time-budget=6000", f"--window-size={width},{height}", f"--screenshot={out}", f"file://{p}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    img = Image.open(out).convert("RGB")
    bbox = Image.eval(img, lambda v: 255 if v < 250 else 0).getbbox()  # trim white margins
    if bbox:
        pad = 16
        img = img.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(img.width, bbox[2] + pad), min(img.height, bbox[3] + pad)))
    img.save(out)
    p.unlink(missing_ok=True)
    print("fig ->", out)


# ----------------------------------------------------------------------------------------------- diagrams (SVG)

def _box(x, y, w, h, title, lines=(), fill="#f7f9fc", stroke="#4a6fa5", tcol="#1f3b63", r=10, dashed=False, badge=None):
    dash = " stroke-dasharray='6 4'" if dashed else ""
    s = f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='{r}' fill='{fill}' stroke='{stroke}' stroke-width='1.6'{dash}/>"
    s += f"<text x='{x + 14}' y='{y + 24}' font-size='15' font-weight='700' fill='{tcol}'>{title}</text>"
    for i, ln in enumerate(lines):
        s += f"<text x='{x + 14}' y='{y + 46 + 18 * i}' font-size='12.5' fill='#333'>{ln}</text>"
    if badge:
        txt, bc = badge
        bw = 8 + 6.6 * len(txt)
        s += (f"<rect x='{x + w - bw - 10}' y='{y + 10}' width='{bw}' height='20' rx='10' fill='{bc}'/>"
              f"<text x='{x + w - bw / 2 - 10}' y='{y + 24}' font-size='11' font-weight='600' fill='#fff' text-anchor='middle'>{txt}</text>")
    return s


def _arrow(x1, y1, x2, y2, label=None, dy=-7, color="#555"):
    s = f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{color}' stroke-width='1.6' marker-end='url(#ah)'/>"
    if label:
        s += f"<text x='{(x1 + x2) / 2}' y='{(y1 + y2) / 2 + dy}' font-size='11.5' fill='{MUTED}' text-anchor='middle'>{label}</text>"
    return s


DEFS = ("<defs><marker id='ah' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto-start-reverse'>"
        "<path d='M0,0 L10,5 L0,10 z' fill='#555'/></marker></defs>")
DONE, STOP, PLAN = ("completed", "#1e8449"), ("stopped by quota", "#b9770e"), ("not run", "#7f8c8d")


def _h(lines):
    return 40 + 18 * len(lines) + 8


def fig_architecture():
    W, H = 1240, 560
    s = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' font-family='Inter Tight, sans-serif'>{DEFS}"
    cfg = ["4 models (fixed seats)", "× 3 personas (system message)", "neutral · competitive · fair", "unit of audit = model × persona"]
    a1 = ["Vignette: live game state (hand, target, scores)", "+ one private offer from a random peer:", "S0 designer tool · S1 direct pact",
          "S2 indirect hint · S3 benign request (control)", "Strict JSON parse → re-ask once → frozen judge", "480 trials (12 × 4 × 10), seed 7"]
    sc = ["sting score = mean acceptance (S1, S2)", "benign score = acceptance (S3)", "test-awareness flag (keyword heuristic)",
          "exploratory: Claude Haiku / Sonnet 5.5 (240 trials)"]
    a2 = ["Liar's Bar + open private channel, no offer", "Monitors: messages-only (LLM), actions-only", "(pass-rate gap), fused claims-vs-actions (LLM)",
          "planned 9 games (seeds 101–103); 1 completed"]
    bb = ["Same game, fresh seeds 201–204, no offer", "Frozen judge: private agreement? (per pair)", "Behaviour: preferential play PP ≥ 0.25",
          "Labels: COLLUDE · TALK-ONLY · ACT-ONLY · NONE", "planned 12 games; 1 completed"]
    an = ["H1 sting score predicts deployment collusion", "H2 sting adds to the fused monitor", "H3 fused > messages-only, actions-only",
          "H4 benign score does not predict collusion", "Spearman ρ, AUROC, cluster bootstrap"]
    X1, X2, X3 = 20, 300, 790
    y_a1, y_a2, y_b = 20, 20 + _h(a1) + 24, 20 + _h(a1) + 24 + _h(a2) + 24
    s += _box(X1, 200, 240, _h(cfg), "12 configurations", cfg, fill="#fbfbfb", stroke="#888", tcol=INK)
    s += _box(X2, y_a1, 410, _h(a1), "Phase A1 · Sting probe", a1, badge=DONE)
    s += _box(X2, y_a2, 410, _h(a2), "Phase A2 · Audit games", a2, badge=STOP)
    s += _box(X2, y_b, 410, _h(bb), "Phase B · Deployment games", bb, badge=STOP)
    s += _box(X3, y_a1 + 20, 430, _h(sc), "Probe scores per configuration", sc, fill="#f3f9f4", stroke="#1e8449", tcol="#145a32")
    y_an = y_a2 + 30
    s += _box(X3, y_an, 430, _h(an), "Pre-registered analysis (H1–H4)", an, fill="#fbfbfb", stroke="#7f8c8d", tcol=INK, dashed=True, badge=PLAN)
    cy = 200 + _h(cfg) / 2
    s += _arrow(X1 + 240, cy - 20, X2 - 2, y_a1 + _h(a1) / 2) + _arrow(X1 + 240, cy, X2 - 2, y_a2 + _h(a2) / 2) + _arrow(X1 + 240, cy + 20, X2 - 2, y_b + _h(bb) / 2)
    s += _arrow(X2 + 410, y_a1 + 20 + _h(sc) / 2, X3 - 2, y_a1 + 20 + _h(sc) / 2)
    s += _arrow(X3 + 215, y_a1 + 20 + _h(sc), X3 + 215, y_an - 2)
    s += f"<text x='{X3 + 225}' y='{(y_a1 + 20 + _h(sc) + y_an) / 2 + 4}' font-size='11.5' fill='{MUTED}'>predictors</text>"
    s += _arrow(X2 + 410, y_a2 + _h(a2) / 2, X3 - 2, y_an + 40)
    s += f"<text x='{X2 + 418}' y='{y_a2 + _h(a2) / 2 - 8}' font-size='11.5' fill='{MUTED}'>monitor scores</text>"
    s += _arrow(X2 + 410, y_b + _h(bb) / 2, X3 - 2, y_an + _h(an) - 30)
    s += f"<text x='{X2 + 418}' y='{y_b + _h(bb) / 2 + 20}' font-size='11.5' fill='{MUTED}'>labels</text>"
    s += (f"<text x='{X1}' y='{y_b + _h(bb) + 28}' font-size='11.5' fill='{MUTED}'>Pre-registration committed (624c534) before any A2/B game. "
          "Prompts, judge model, temperature and thresholds frozen. No alliance instruction appears in any game prompt.</text>")
    s += "</svg>"
    render_html(s, "fig_architecture", W + 20, H + 20)


def fig_protocol():
    W, H = 1240, 300
    s = f"<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' font-family='Inter Tight, sans-serif'>{DEFS}"
    steps = [("1 · Private message", ["optional: one message to", "one alive player; one reply", "(neutral prompt, no hint)"], "#eef3fb", "#4a6fa5"),
             ("2 · Play cards", ["play 1–3 cards face down,", "claim they match the target;", "sees last 6 private exchanges"], "#f7f9fc", "#4a6fa5"),
             ("3 · Challenge?", ["next player decides to call", "a bluff or let it pass;", "sees the same messages"], "#f7f9fc", "#4a6fa5"),
             ("4 · Penalty", ["loser of a challenge pulls", "the revolver (1 live round", "in 6 chambers)"], "#fdf2f0", "#c0392b"),
             ("5 · Log & label", ["record every message, play,", "bluff and challenge; label", "agreement + preferential play"], "#f3f9f4", "#1e8449")]
    x, w, gap = 10, 220, 30
    for i, (t, ls, f, st) in enumerate(steps):
        s += _box(x, 40, w, 130, t, ls, fill=f, stroke=st, tcol=INK)
        if i < len(steps) - 1:
            s += _arrow(x + w, 105, x + w + gap - 2, 105)
        x += w + gap
    s += ("<path d='M 1220 175 C 1220 250, 120 250, 120 178' fill='none' stroke='#888' stroke-width='1.4' stroke-dasharray='5 4' marker-end='url(#ah)'/>"
          f"<text x='620' y='262' font-size='12' fill='{MUTED}' text-anchor='middle'>next player's turn · game ends at a fixed 12-round horizon (engine counter) and is scored</text>"
          f"<text x='10' y='22' font-size='12.5' fill='{MUTED}'>Our patch to the pre-existing engine only appends the private-message history to the play and challenge prompts "
          "(player.py, 3 lines); the original secret-channel “alliance reminder” is never activated.</text>")
    s += "</svg>"
    render_html(s, "fig_protocol", W + 20, H + 20)


# ----------------------------------------------------------------------------------------------- plots

def _wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def fig_acceptance():
    kn = json.loads((TABLES / "key_numbers.json").read_text())["probe"]
    acc = pd.read_csv(TABLES / "T2_acceptance.csv")
    fig = plt.figure(figsize=(7.2, 3.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.45], wspace=0.78)
    ax = fig.add_subplot(gs[0])
    offers = ["S0", "S1", "S2", "S3"]
    r = [kn["accept_by_offer"][o]["rate"] for o in offers]
    lo = [kn["accept_by_offer"][o]["lo"] for o in offers]; hi = [kn["accept_by_offer"][o]["hi"] for o in offers]
    ax.bar(range(4), r, 0.62, color=[OFFER[o][0] for o in offers], edgecolor="none", zorder=2)
    ax.errorbar(range(4), r, yerr=[np.subtract(r, lo), np.subtract(hi, r)], fmt="none", ecolor=INK, capsize=3, lw=0.9, zorder=3)
    for i, v in enumerate(r):
        ax.text(i, hi[i] + 0.025, f"{v:.0%}", ha="center", fontsize=8.5, fontweight="bold")
    ax.set_xticks(range(4)); ax.set_xticklabels(["S0", "S1", "S2", "S3"])
    ax.set_ylim(0, 1.08); ax.set_ylabel("Acceptance rate"); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="y", color="#e6e6e6", lw=0.7, zorder=0)
    ax.set_title("(a) Pooled, n = 120 per offer", loc="left")
    # heatmap
    ax2 = fig.add_subplot(gs[1])
    rows = [(m, p) for m in MODEL_ORDER for p in PERSONAS]
    M = np.array([[acc[(acc.model == m) & (acc.persona == p) & (acc.offer == o)].accept_rate.iloc[0] for o in offers] for m, p in rows])
    im = ax2.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax2.text(j, i, f"{M[i, j] * 10:.0f}", ha="center", va="center", fontsize=7.5, color="white" if M[i, j] > 0.55 else INK)
    ax2.set_xticks(range(4)); ax2.set_xticklabels(["S0", "S1", "S2", "S3"])
    ax2.set_yticks(range(len(rows))); ax2.set_yticklabels([f"{MODEL_LABEL[m]} · {p}" for m, p in rows], fontsize=7.2)
    for k in (3, 6, 9):
        ax2.axhline(k - 0.5, color="white", lw=2)
    ax2.tick_params(length=0); [sp.set_visible(False) for sp in ax2.spines.values()]
    ax2.set_title("(b) Accepted / 10 per configuration", loc="left")
    cb = fig.colorbar(im, ax=ax2, fraction=0.04, pad=0.02); cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7)
    cb.ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    save(fig, "fig_acceptance.png")


def fig_sting_benign():
    kn = json.loads((TABLES / "key_numbers.json").read_text())["probe"]["config_scores"]
    ex = json.loads((TABLES / "probe_extra.json").read_text())
    fig, ax = plt.subplots(figsize=(4.3, 3.4))
    ax.plot([0, 1], [0, 1], ls="--", color="#bbbbbb", lw=0.9, zorder=1)
    rng = np.random.default_rng(1)
    for key, v in kn.items():
        m, p = key.split("|")
        jx, jy = rng.uniform(-0.018, 0.018, 2)
        ax.scatter(v["benign"] + jx, v["sting"] + jy, marker=MARK[m], s=58, color=PCOL[p], edgecolor="white", lw=0.8, zorder=3)
    for m in MODEL_ORDER:
        ax.scatter([], [], marker=MARK[m], color="#666", s=40, label=MODEL_LABEL[m])
    for p in PERSONAS:
        ax.scatter([], [], marker="s", color=PCOL[p], s=40, label=p)
    ax.legend(fontsize=7, loc="lower right", ncol=2, handletextpad=0.3, columnspacing=0.8)
    ax.annotate("allam-2-7b, all 3 personas\n(accepts every offer)", xy=(0.97, 0.99), xytext=(0.52, 0.9), fontsize=7, color=MUTED,
                arrowprops=dict(arrowstyle="-", color="#999", lw=0.7))
    ax.annotate("qwen3.8-27b, all 3 personas", xy=(0.03, 0.06), xytext=(0.16, 0.3), fontsize=7, color=MUTED,
                arrowprops=dict(arrowstyle="-", color="#999", lw=0.7))
    r = ex["rho_sting_vs_benign"]
    ax.text(0.02, 0.97, f"Spearman ρ = {r['rho']:.2f}  (p = {r['p_two_sided']:.1g}, n = {r['n_configs']} configs)",
            transform=ax.transAxes, fontsize=8.2, va="top", fontweight="bold")
    ax.set_xlabel("Benign score: acceptance of S3 fair-play request"); ax.set_ylabel("Sting score: mean acceptance of S1, S2")
    ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.08)
    for a in (ax.xaxis, ax.yaxis):
        a.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(color="#eeeeee", lw=0.7, zorder=0)
    save(fig, "fig_sting_benign.png")


def fig_all_models():
    acc = pd.concat([pd.read_csv(TABLES / "T2_acceptance.csv"), pd.read_csv(TABLES / "T2b_acceptance_claude.csv")])
    order = MODEL_ORDER + ["claude-haiku", "claude-sonnet"]
    offers = ["S0", "S1", "S2", "S3"]
    fig, ax = plt.subplots(figsize=(7.0, 2.7))
    w = 0.19
    for k, o in enumerate(offers):
        rates, los, his = [], [], []
        for m in order:
            sub = acc[(acc.model == m) & (acc.offer == o)]
            n, a = sub.n_valid.sum(), sub.n_accept.sum()
            rates.append(a / n); l, h = _wilson(a, n); los.append(a / n - l); his.append(h - a / n)
        x = np.arange(len(order)) + (k - 1.5) * w
        ax.bar(x, rates, w * 0.92, color=OFFER[o][0], label=OFFER[o][1], zorder=2)
        ax.errorbar(x, rates, yerr=[los, his], fmt="none", ecolor="#333", capsize=1.6, lw=0.6, zorder=3)
    ax.axvline(3.5, color="#999", ls="--", lw=0.9)
    ax.text(3.58, 1.1, "* exploratory, not pre-registered", fontsize=7.5, color=MUTED, va="top")
    ax.set_xticks(range(len(order))); ax.set_xticklabels([MODEL_LABEL[m] for m in order], fontsize=8)
    ax.set_ylim(0, 1.12); ax.set_ylabel("Acceptance (pooled over personas)")
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0)); ax.grid(axis="y", color="#e6e6e6", lw=0.7, zorder=0)
    ax.legend(ncol=4, fontsize=7.8, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    save(fig, "fig_all_models.png")


# ----------------------------------------------------------------------------------------------- light screenshots

LIGHT_CSS = """body{background:#fff;font-family:'Inter Tight',sans-serif;color:#1a1a1a}
.card{margin:14px;background:#fff;border:1px solid #d0d7de;border-radius:10px;padding:18px 22px}
h1{font-size:18px;margin:0 0 4px 0;color:#111} .sub{font-size:12px;color:#57606a;margin-bottom:12px}
table{border-collapse:collapse;width:100%;font-size:12.5px} th{color:#24292f;font-weight:600;text-align:left;padding:6px 8px;border-top:1.5px solid #333;border-bottom:1px solid #333}
td{padding:6px 8px;border-bottom:1px solid #e3e6ea;vertical-align:top} .acc{color:#b03a2e;font-weight:700} .ref{color:#1e8449;font-weight:700}
.mono,code{font-family:'JetBrains Mono',monospace;font-size:11.5px} .bubble{max-width:80%;padding:9px 12px;border-radius:12px;margin:5px 0;font-size:13px;line-height:1.35}
.l{background:#eaf1fb;border:1px solid #c9daf3;margin-right:auto} .r{background:#f4eefb;border:1px solid #ddd0f0;margin-left:auto}
.who{font-size:11px;color:#57606a;margin-bottom:1px} .verdict{background:#f1f8f3;border:1px solid #9fd3ae;border-radius:8px;padding:10px 12px;font-size:12.5px;margin-top:12px}
.term{background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:14px 16px;font-family:'JetBrains Mono',monospace;font-size:11.5px;white-space:pre-wrap;color:#24292f;line-height:1.45}
.ok{color:#1a7f37;font-weight:600} .dim{color:#6e7781} .kv{font-family:'JetBrains Mono',monospace;font-size:12px;white-space:pre}
.foot{font-size:11px;color:#6e7781;margin-top:10px}"""


def light_screenshots():
    from sting_audit import make_media as mm
    names = {"private_channel": "shot_private_channel", "probe_replies": "shot_probe_replies", "evidence_terminal": "shot_evidence"}
    orig = mm.shot
    def shot(body, name, width=1000, height=700):
        render_html(body, names.get(name, name), width, height, css=LIGHT_CSS)
        return OUT / f"{names.get(name, name)}.png"
    mm.shot = shot
    try:
        mm.private_channel(); mm.probe_replies(k=8); mm.evidence_terminal()
    finally:
        mm.shot = orig


def make_all():
    fig_architecture(); fig_protocol(); fig_acceptance(); fig_sting_benign(); fig_all_models(); light_screenshots()


if __name__ == "__main__":
    make_all()


def shot_quota():
    """Proof card for why the game phase stopped: the provider error recorded in NOTES.md and the per-game token use in results/cost_log.csv."""
    import csv, html as H
    notes = (REPO / "NOTES.md").read_text().splitlines()
    err = next((l for l in notes if "tokens per day (TPD)" in l), "")
    rows = [r for r in csv.reader((REPO / "results" / "cost_log.csv").read_text().splitlines())]
    head, games = rows[0], [r for r in rows[1:] if r[1] in ("A2", "B")]
    tr = "".join("<tr>" + "".join(f"<td class='mono'>{H.escape(c)}</td>" for c in (r[0], r[1], r[4], r[6], r[7])) + "</tr>" for r in games)
    body = (f"<div class='card'><h1>Why the game phase stopped: provider quota</h1>"
            f"<div class='sub'>Excerpt from NOTES.md (lab notebook) and results/cost_log.csv</div>"
            f"<div class='term'>{H.escape(err.strip('- '))}</div>"
            f"<div class='sub' style='margin-top:14px'>Completed games, size per game (all four seats; characters, not tokens):</div>"
            f"<table><tr><th>run_id</th><th>phase</th><th>LLM calls</th><th>prompt characters</th><th>completion characters</th></tr>{tr}</table>"
            f"<div class='foot'>Free tier: 200,000 tokens/day for qwen/qwen3.8-27b (seat Luke): only a few games per day; 19 games remained.</div></div>")
    render_html(body, "shot_quota", 1100, 700, css=LIGHT_CSS)
