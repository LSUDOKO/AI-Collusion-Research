"""Descriptive probe statistics added after the game phase was cut short (not pre-registered):
Spearman correlation across the 12 configurations between sting score (S1+S2) / S1 / S2 and benign (S3) acceptance,
and per-model acceptance pooled over personas. Writes results/tables/probe_extra.json."""
import json

from scipy.stats import spearmanr

from sting_audit.paths import TABLES


def main():
    cs = json.loads((TABLES / "key_numbers.json").read_text())["probe"]["config_scores"]
    out = {}
    for k in ("sting", "S1", "S2"):
        r = spearmanr([v[k] for v in cs.values()], [v["benign"] for v in cs.values()])
        out[f"rho_{k}_vs_benign"] = {"rho": round(float(r.statistic), 3), "p_two_sided": float(f"{r.pvalue:.2g}"), "n_configs": len(cs)}
    models = sorted({k.split("|")[0] for k in cs})
    out["by_model"] = {m: {o: round(sum(v[o] for k, v in cs.items() if k.startswith(m + "|")) / 3, 3)
                           for o in ("S0", "S1", "S2", "S3")} for m in models}
    out["n_configs_S2_gt_S1"] = sum(v["S2"] > v["S1"] for v in cs.values())
    out["n_configs_S1_gt_S2"] = sum(v["S1"] > v["S2"] for v in cs.values())
    (TABLES / "probe_extra.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
