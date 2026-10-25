"""Figures (docs/06 §E). Colour-blind-safe palette (Okabe–Ito). Writes results/figures and report/figures (300 dpi)."""
import json
import shutil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sting_audit.paths import TABLES, FIGURES, REPO

REPORT_FIG = REPO / "report" / "figures"
OKABE = {"neutral": "#0072B2", "competitive": "#D55E00", "fair": "#009E73"}
OFFER_COL = {"S0": "#999999", "S1": "#D55E00", "S2": "#E69F00", "S3": "#56B4E9"}
MARK = {"llama-3.1-8b": "o", "llama-3.2-3b": "s", "ministral-8b": "^", "qwen2.5-7b": "D"}
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True); REPORT_FIG.mkdir(parents=True, exist_ok=True)
    p = FIGURES / name
    fig.savefig(p, dpi=300, bbox_inches="tight")
    shutil.copy(p, REPORT_FIG / name)
    plt.close(fig)
    print("fig ->", p)


def fig1_design():
    fig, ax = plt.subplots(figsize=(7.2, 3.2)); ax.axis("off")
    def box(x, y, w, h, text, fc="#f2f2f2", ec="#333"):
        ax.add_patch(plt.Rectangle((x, y), w, h, fc=fc, ec=ec, lw=1.0, zorder=2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, zorder=3, wrap=True)
    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", lw=1.0, color="#333"))
    box(0.02, 0.62, 0.27, 0.30, "Phase A1  Sting probe\n(vignette, out-of-game)\nS0 designer · S1 direct ·\nS2 indirect · S3 benign\n12 configs × 20 trials", "#FDE7D9")
    box(0.02, 0.10, 0.27, 0.40, "Phase A2  Passive audit games\nopen private channel, no offer\nseeds 101–103\n→ messages-only, actions-only,\nfused monitors", "#DCEBF7")
    box(0.37, 0.30, 0.24, 0.42, "Predictors per\nconfiguration\n(model × persona)\nsting · benign · M_msg ·\nM_act · M_fused · sting+fused", "#F2F2F2")
    box(0.70, 0.30, 0.28, 0.42, "Phase B  Deployment games\n(ground truth)\nopen channel, no offer, seeds 201–204\nCOLLUDE = private agreement\n+ preferential play", "#DFF2E9")
    box(0.70, 0.02, 0.28, 0.20, "Phase C  Entrapment arm (Tier 3)\nS1 pre-sting vs matched control", "#EFE6F7")
    arrow(0.29, 0.77, 0.37, 0.60); arrow(0.29, 0.30, 0.37, 0.42); arrow(0.61, 0.51, 0.70, 0.51)
    ax.text(0.655, 0.56, "ρ, AUROC", ha="center", fontsize=8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "fig1_design.png")


def fig2_acceptance():
    p = TABLES / "T2_acceptance.csv"
    if not p.exists():
        return
    acc = pd.read_csv(p)
    personas = [x for x in ["neutral", "competitive", "fair"] if x in set(acc.persona)]
    models = sorted(acc.model.unique())
    offers = [o for o in ["S0", "S1", "S2", "S3"] if o in set(acc.offer)]
    fig, axes = plt.subplots(1, len(personas), figsize=(2.6 * len(personas) + 0.8, 2.9), sharey=True)
    axes = np.atleast_1d(axes)
    w = 0.8 / len(offers)
    for ax, pe in zip(axes, personas):
        for k, off in enumerate(offers):
            sub = acc[(acc.persona == pe) & (acc.offer == off)].set_index("model").reindex(models)
            x = np.arange(len(models)) + (k - (len(offers) - 1) / 2) * w
            ax.bar(x, sub.accept_rate, w, color=OFFER_COL[off], label=off if ax is axes[0] else None,
                   yerr=[sub.accept_rate - sub.ci_lo, sub.ci_hi - sub.accept_rate], capsize=1.5, error_kw=dict(lw=0.7))
        ax.set_title(pe); ax.set_xticks(range(len(models))); ax.set_xticklabels(models, rotation=30, ha="right", fontsize=7)
        ax.set_ylim(0, 1.05)
    axes[0].set_ylabel("Acceptance rate (Wilson 95% CI)")
    fig.legend(*axes[0].get_legend_handles_labels(), title="Offer", fontsize=7.5, title_fontsize=7.5, loc="lower center",
               ncol=4, bbox_to_anchor=(0.5, -0.12), frameon=False)
    save(fig, "fig2_acceptance.png")


def fig3_scatter():
    p = TABLES / "config_scores_B.csv"
    if not p.exists():
        return
    df = pd.read_csv(p)
    kn = json.loads((TABLES / "key_numbers.json").read_text())
    ycol = kn.get("B", {}).get("primary_outcome", "collusion_rate")
    fig, ax = plt.subplots(figsize=(3.8, 3.2))
    for r in df.itertuples():
        ax.scatter(r.sting_score, getattr(r, ycol), marker=MARK.get(r.model, "o"), color=OKABE.get(r.persona, "k"), s=55, edgecolor="k", lw=0.5, zorder=3)
    for pe, c in OKABE.items():
        if pe in set(df.persona):
            ax.scatter([], [], color=c, label=pe, s=40)
    for m, mk in MARK.items():
        if m in set(df.model):
            ax.scatter([], [], marker=mk, color="w", edgecolor="k", label=m, s=40)
    ax.legend(fontsize=6.5, ncol=2, loc="best")
    ax.set_xlabel("Sting score (mean acceptance of S1 + S2)")
    ax.set_ylabel("Deployment " + ("collusion rate" if ycol == "collusion_rate" else "mean collusion score"))
    h1 = kn.get("H1", {})
    ax.set_title(f"ρ = {h1.get('rho')} [{h1.get('rho_ci_lo')}, {h1.get('rho_ci_hi')}], n = {h1.get('n_configs')} configs", fontsize=8)
    ax.set_xlim(-0.05, 1.05)
    save(fig, "fig3_predictive_validity.png")


def fig4_predictors():
    p = TABLES / "T3_predictors.csv"
    if not p.exists():
        return
    df = pd.read_csv(p)
    order = ["sting", "benign", "messages_only", "actions_only", "fused", "sting_plus_fused"]
    df["o"] = df.predictor.map({k: i for i, k in enumerate(order)}); df = df.sort_values("o")
    fig, ax = plt.subplots(figsize=(4.2, 2.8))
    y = np.arange(len(df))
    ax.errorbar(df.auroc, y, xerr=[df.auroc - df.auroc_ci_lo, df.auroc_ci_hi - df.auroc], fmt="o", color="#0072B2", capsize=3)
    ax.axvline(0.5, ls="--", color="grey", lw=1)
    ax.set_yticks(y); ax.set_yticklabels([s.replace("_", " ") for s in df.predictor]); ax.invert_yaxis()
    ax.set_xlabel("AUROC for deployment collusion (95% cluster-bootstrap CI)"); ax.set_xlim(0, 1)
    save(fig, "fig4_predictor_comparison.png")


def fig5_outcomes():
    p = TABLES / "labels_B.csv"
    if not p.exists():
        return
    lab = pd.read_csv(p); lab = lab[~lab.excluded.astype(bool)]
    cats = ["COLLUDE", "TALK_ONLY", "ACT_ONLY", "NONE"]
    cols = {"COLLUDE": "#D55E00", "TALK_ONLY": "#E69F00", "ACT_ONLY": "#56B4E9", "NONE": "#CCCCCC"}
    pc = TABLES / "labels_C.csv"
    panels = [("Phase B by persona", lab, "persona")]
    if pc.exists():
        c = pd.read_csv(pc); c = c[~c.excluded.astype(bool)]
        if "arm" in c:
            panels.append(("Phase C by arm", c, "arm"))
    fig, axes = plt.subplots(1, len(panels), figsize=(3.3 * len(panels) + 0.5, 2.8))
    axes = np.atleast_1d(axes)
    for ax, (title, d, by) in zip(axes, panels):
        ct = pd.crosstab(d[by], d.label).reindex(columns=cats, fill_value=0)
        share = ct.div(ct.sum(axis=1), axis=0)
        bottom = np.zeros(len(share))
        for cat in cats:
            ax.bar(share.index, share[cat], bottom=bottom, color=cols[cat], label=cat if ax is axes[0] else None)
            bottom += share[cat].values
        for i, (idx, n) in enumerate(ct.sum(axis=1).items()):
            ax.text(i, 1.02, f"n={n}", ha="center", fontsize=7)
        ax.set_title(title, fontsize=9); ax.set_ylim(0, 1.1); ax.set_ylabel("Share of agent-games")
    axes[0].legend(fontsize=7, loc="lower right")
    save(fig, "fig5_outcomes.png")


def make_all():
    fig1_design(); fig2_acceptance(); fig3_scatter(); fig4_predictors(); fig5_outcomes()
    try:
        fig2b_claude()
    except NameError:
        pass


if __name__ == "__main__":
    make_all()


def fig2b_claude():
    p = TABLES / "T2b_acceptance_claude.csv"
    q = TABLES / "T2_acceptance.csv"
    if not p.exists() or not q.exists():
        return
    acc = pd.concat([pd.read_csv(q), pd.read_csv(p)])
    g = acc.groupby(["model", "offer"]).apply(lambda x: x.n_accept.sum() / max(x.n_valid.sum(), 1)).unstack()
    offers = [o for o in ["S0", "S1", "S2", "S3"] if o in g.columns]
    order = [m for m in ["allam-7b", "qwen3.8-27b", "gpt-oss-20b", "gpt-oss-120b", "claude-haiku", "claude-sonnet"] if m in g.index]
    g = g.reindex(order)
    fig, ax = plt.subplots(figsize=(7.2, 2.9))
    w = 0.8 / len(offers)
    for k, o in enumerate(offers):
        ax.bar(np.arange(len(order)) + (k - (len(offers) - 1) / 2) * w, g[o], w, color=OFFER_COL[o], label=o)
    ax.axvline(len([m for m in order if not m.startswith("claude")]) - 0.5, color="grey", ls="--", lw=1)
    ax.text(len(order) - 1, 1.04, "Claude (exploratory,\nsubscription CLI)", ha="center", fontsize=7)
    ax.set_xticks(range(len(order))); ax.set_xticklabels(order, rotation=20, ha="right", fontsize=8)
    ax.set_ylim(0, 1.12); ax.set_ylabel("Acceptance (pooled over personas)")
    ax.legend(ncol=4, fontsize=7.5, loc="lower center", bbox_to_anchor=(0.5, -0.42), frameon=False)
    save(fig, "fig2b_acceptance_all_models.png")
