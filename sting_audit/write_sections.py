"""Generate data-driven report sections into report/sections/: APPENDIX_B.md (prompts verbatim, parser audit, robustness,
cost), COST.md, JUDGE_MODEL.md, PREREG_HASH.md, DEVIATIONS.md (from NOTES.md 'Deviations' block if present).
Hand-written sections (RESULTS, DISCUSSION, CONCLUSION, HEADLINE, ABSTRACT_RESULTS) are not touched."""
import csv
import json
import subprocess
from pathlib import Path

import pandas as pd

from sting_audit.paths import REPO, TABLES, PROMPTS, COST_LOG, LB_DIR
from sting_audit.judge import DEFAULT_JUDGE_MODEL

SEC = REPO / "report" / "sections"


def prereg_hash():
    out = subprocess.run(["git", "-C", str(REPO), "log", "--format=%h", "--diff-filter=A", "--", "PREREGISTRATION.md"], capture_output=True, text=True).stdout.split()
    return out[-1] if out else "unknown"


def cost_block():
    if not COST_LOG.exists():
        return "No cost log."
    df = pd.read_csv(COST_LOG)
    by = df.groupby("phase")[["calls", "empty_responses"]].sum()
    total = int(df.calls.sum())
    lines = [f"All inference ran on a Groq free-tier key (no monetary cost). Total LLM calls logged: {total:,} "
             f"(players + probe; judge/monitor calls are additionally recorded in `results/judge_cache.jsonl`)."]
    lines.append("")
    lines.append("| Phase | Calls | Empty responses |")
    lines.append("|---|---|---|")
    for ph, r in by.iterrows():
        lines.append(f"| {ph} | {int(r.calls):,} | {int(r.empty_responses)} |")
    jc = REPO / "results" / "judge_cache.jsonl"
    if jc.exists():
        n = sum(1 for _ in open(jc))
        lines.append(f"\nJudge/monitor calls cached: {n:,} (model {DEFAULT_JUDGE_MODEL}).")
    return "\n".join(lines)


def appendix_b():
    kn = json.loads((TABLES / "key_numbers.json").read_text()) if (TABLES / "key_numbers.json").exists() else {}
    parts = ["**B.1 Offer texts (frozen; `prompts/offers_S1_S2_S3.txt`).** S0 is the starter repository's `tool_offer_prompt.txt` verbatim.", "",
             "```", (PROMPTS / "offers_S1_S2_S3.txt").read_text().strip(), "```", "",
             "**B.2 S0 designer offer (pre-existing, verbatim).**", "", "```", (LB_DIR / "prompts/secret_channel/tool_offer_prompt.txt").read_text().strip(), "```", "",
             "**B.3 Open-channel messaging prompts (`prompts/open_channel_messaging.txt`).**", "", "```", (PROMPTS / "open_channel_messaging.txt").read_text().strip(), "```", "",
             "**B.4 Persona system messages.**", "", "```", (PROMPTS / "personas.txt").read_text().strip(), "```", "",
             "**B.5 Judge and monitor prompts.**", ""]
    for name in ["judge_offer_reply.txt", "judge_agreement.txt", "monitor_messages.txt", "monitor_fused.txt"]:
        parts += [f"*{name}*", "", "```", (PROMPTS / name).read_text().strip(), "```", ""]
    pa = kn.get("probe", {})
    parts += ["**B.6 Parser audit.** " + (f"Of {pa.get('n_rows', '?')} probe replies, parse methods were {pa.get('parse_method_counts')}; "
              f"{pa.get('n_ambiguous', 0)} replies remained AMBIGUOUS after the judge. "
              + (f"Hand-check of {pa['parser_audit_n']} random replies: {pa['parser_audit_agreement']*100:.0f}% agreement with the automated decision."
                 if pa.get("parser_audit_n") else "Hand-check: see NOTES.md.")), ""]
    rb = TABLES / "T4_robustness.csv"
    if rb.exists():
        df = pd.read_csv(rb)
        parts += ["**B.7 Robustness (H1 under alternative label definitions).**", "", df.to_markdown(index=False), ""]
    parts += ["**B.8 Cost and calls.**", "", cost_block()]
    return "\n".join(parts)


def main():
    SEC.mkdir(parents=True, exist_ok=True)
    (SEC / "JUDGE_MODEL.md").write_text(DEFAULT_JUDGE_MODEL + " (Groq)")
    (SEC / "PREREG_HASH.md").write_text(prereg_hash())
    (SEC / "COST.md").write_text(cost_block())
    (SEC / "APPENDIX_B.md").write_text(appendix_b())
    notes = (REPO / "NOTES.md").read_text()
    if "## Deviations" in notes:
        (SEC / "DEVIATIONS.md").write_text(notes.split("## Deviations", 1)[1].split("\n## ", 1)[0].strip())
    print("sections written:", sorted(p.name for p in SEC.iterdir()))


if __name__ == "__main__":
    main()
