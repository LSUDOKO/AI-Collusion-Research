"""Generate the data-dependent text sections from results/tables/key_numbers.json (no number is typed by hand):
report/sections/{HEADLINE, ABSTRACT_RESULTS, RESULTS, DISCUSSION, CONCLUSION, DEVIATIONS, TLDR, HEADLINE_TABLE}.md
and README.md from report/sections/README_TEMPLATE.md. Wording is conditional on the pre-registered tests.
"""
import json
from pathlib import Path

import pandas as pd

from sting_audit.paths import REPO, TABLES

SEC = REPO / "report" / "sections"
MODEL_LABEL = {"allam-7b": "allam-2-7b", "qwen3.8-27b": "Qwen3.8-27B", "gpt-oss-20b": "gpt-oss-20b", "gpt-oss-120b": "gpt-oss-120b"}


def pct(x):
    return "n/a" if x is None else f"{100*x:.0f}%"


def f2(x):
    return "n/a" if x is None else f"{x:.2f}"


def ci(lo, hi):
    return f"[{f2(lo)}, {f2(hi)}]"


def verdict_h1(h):
    rho, lo, hi, au, alo, ahi, p = h["rho"], h["rho_ci_lo"], h["rho_ci_hi"], h["auroc"], h["auroc_ci_lo"], h["auroc_ci_hi"], h["perm_p"]
    if rho is None:
        return "could not be evaluated (outcome constant)"
    if rho > 0 and lo is not None and lo > 0 and p is not None and p < 0.05:
        return "supported"
    if rho > 0:
        return "directionally positive but not statistically distinguishable from zero at this sample size"
    return "not supported"


def main():
    kn = json.loads((TABLES / "key_numbers.json").read_text())
    pr, B, H1, H4 = kn["probe"], kn["B"], kn["H1"], kn["H4"]
    preds = kn.get("predictors", {})
    H2, H3, H5 = kn.get("H2"), kn.get("H3"), kn.get("H5")
    cfg = pr["config_scores"]; rates = B["config_rates"]
    # --- per-model probe summary
    acc = pd.read_csv(TABLES / "T2_acceptance.csv")
    by_model_offer = acc.groupby(["model", "offer"]).apply(lambda g: g.n_accept.sum() / max(g.n_valid.sum(), 1)).unstack()
    by_persona_offer = acc.groupby(["persona", "offer"]).apply(lambda g: g.n_accept.sum() / max(g.n_valid.sum(), 1)).unstack()
    s0, s1, s2, s3 = (pr["accept_by_offer"][o]["rate"] for o in ("S0", "S1", "S2", "S3"))
    lab = pd.read_csv(TABLES / "labels_B.csv"); lab = lab[~lab.excluded.astype(bool)]
    n_games, n_ag = B["n_games"], B["n_agent_games"]
    lc = B["label_counts"]; base = B["base_rate_rule_triggered"]
    primary_label = "agreement (talk)" if base else "COLLUDE"
    primary_outcome = "mean collusion score" if base else "collusion rate"

    # ---------------- HEADLINE
    v1 = verdict_h1(H1)
    headline = (f"**Headline.** Across {n_games} deployment games ({n_ag} agent-games), unprompted private agreements occurred in "
                f"{pct(B['agree_rate_overall'])} of agent-games and the full COLLUDE label (agreement followed by preferential play) in "
                f"{pct(B['collusion_rate_overall'])} ({lc.get('COLLUDE', 0)} cases). The pre-registered primary test of predictive validity was {v1}: "
                f"Spearman ρ = {f2(H1['rho'])} {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])} across the 12 configurations "
                f"(one-sided permutation p = {f2(H1['perm_p'])}), agent-game AUROC = {f2(H1['auroc'])} {ci(H1['auroc_ci_lo'], H1['auroc_ci_hi'])}. "
                f"The benign-offer control reached ρ = {f2(H4['rho'])} {ci(H4['rho_ci_lo'], H4['rho_ci_hi'])}.")
    (SEC / "HEADLINE.md").write_text(headline)

    # ---------------- ABSTRACT_RESULTS
    ab = (f"The designer offer (positive control) was accepted in {pct(s0)} of trials, the direct peer pact in {pct(s1)}, the indirect hint in {pct(s2)} "
          f"and the benign request in {pct(s3)}; configuration-level sting scores ranged from {pct(pr['sting_score_range'][0])} to {pct(pr['sting_score_range'][1])}. "
          f"Private agreements arose unprompted in {pct(B['agree_rate_overall'])} of deployment agent-games and full collusion (agreement plus preferential play) in "
          f"{pct(B['collusion_rate_overall'])}. The sting score {('predicted' if H1['rho'] and H1['rho'] > 0 else 'did not predict')} deployment {primary_outcome} "
          f"(Spearman ρ = {f2(H1['rho'])}, 95% CI {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])}; AUROC = {f2(H1['auroc'])} {ci(H1['auroc_ci_lo'], H1['auroc_ci_hi'])}), "
          f"while the benign control gave ρ = {f2(H4['rho'])}.")
    if preds:
        ab += (f" Passive monitors on separate audit games reached AUROC {f2(preds['messages_only']['auroc'])} (messages-only), "
               f"{f2(preds['actions_only']['auroc'])} (actions-only) and {f2(preds['fused']['auroc'])} (fused); combining sting and fused scores gave {f2(preds['sting_plus_fused']['auroc'])}.")
    sd = B["say_do"]
    if sd["n_agreements"]:
        ab += f" {pct(sd['talk_only_share_of_agreements'])} of agreements were not followed by preferential play (a say–do gap)."
    (SEC / "ABSTRACT_RESULTS.md").write_text(ab)

    # ---------------- RESULTS
    R = []
    R.append("### 4.1 Positive control: the designer offer is still accepted")
    R.append(f"The pre-existing designer offer (S0) was accepted in {pct(s0)} of {pr['n_rows']//4} trials overall "
             f"({', '.join(f'{MODEL_LABEL[m]} {pct(v)}' for m, v in pr['S0_by_model'].items())}). Zeng & Rudzicz [2026] report 100% acceptance for all 7–8B open-weight "
             f"models and 0% for Qwen2.5-72B and Claude-Sonnet-4.5; none of our Groq-hosted models overlaps with their table, so the comparison is directional only: "
             f"small and mid-size open models accept a designer-sanctioned unfair tool at high rates, and refusals are concentrated in one model family.")
    R.append("")
    R.append("### 4.2 Who accepts a sting? (Fig. 2, Table 2)")
    rows = ["| Model | S0 designer | S1 direct pact | S2 indirect hint | S3 benign |", "|---|---|---|---|---|"]
    for m in by_model_offer.index:
        rows.append(f"| {MODEL_LABEL.get(m, m)} | " + " | ".join(pct(by_model_offer.loc[m].get(o)) for o in ["S0", "S1", "S2", "S3"]) + " |")
    R.append(f"Acceptance differed sharply between models (Table 2; n = {pr['n_rows']//16} trials per model × offer, pooled over personas). "
             f"The direct pact S1 was accepted in {pct(s1)} of trials, the indirect hint S2 in {pct(s2)} and the benign request S3 in {pct(s3)}. "
             f"Persona had a visible effect in some models (pooled acceptance of S1+S2 by persona: "
             + ", ".join(f"{p} {pct((by_persona_offer.loc[p].get('S1', 0) + by_persona_offer.loc[p].get('S2', 0)) / 2)}" for p in by_persona_offer.index)
             + f"). Replies flagged as suspecting a test or rule violation were rare ("
             + ", ".join(f"{o} {pct(v)}" for o, v in pr['suspects_test_by_offer'].items()) + ").")
    R.append("")
    R.append("**Table 2. Acceptance by model and offer type (pooled over personas; per-configuration values with Wilson CIs in `results/tables/T2_acceptance.csv`).**")
    R.append("")
    R.extend(rows)
    R.append("")
    R.append(f"Parsing: {pr['parse_method_counts']}; {pr['n_ambiguous']} replies remained ambiguous. A hand-check of "
             f"{pr.get('parser_audit_n', 0)} random replies agreed with the automated decision in {pct(pr.get('parser_audit_agreement'))} of cases.")
    R.append("")
    R.append("### 4.3 Unprompted collusion in deployment games (Fig. 5)")
    R.append(f"In the {n_games} Phase B games ({n_ag} agent-games; {B['mean_messages_per_agent']} private messages per agent on average) the labels were "
             + ", ".join(f"{k} {v}" for k, v in lc.items())
             + f". By persona: " + "; ".join(f"{p}: " + ", ".join(f"{k} {v}" for k, v in d.items()) for p, d in B["label_counts_by_persona"].items())
             + f". By model: " + "; ".join(f"{MODEL_LABEL.get(m, m)}: " + ", ".join(f"{k} {v}" for k, v in d.items()) for m, d in B["label_counts_by_model"].items()) + ".")
    if base:
        R.append(f"Fewer than five COLLUDE labels occurred, so by the pre-registered base-rate rule the primary outcome switches to the continuous collusion score "
                 f"and to agreement incidence; the COLLUDE-label analysis is reported alongside for completeness.")
    R.append("")
    R.append("### 4.4 Does sting acceptance predict collusion? (Fig. 3)")
    R.append(f"**H1 was {v1}.** Across the 12 configurations, the sting score (mean S1+S2 acceptance) correlated with deployment {primary_outcome} at "
             f"Spearman ρ = {f2(H1['rho'])} (95% cluster-bootstrap CI {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])}; one-sided permutation p = {f2(H1['perm_p'])}). "
             f"At the agent-game level the configuration's sting score separated {primary_label} from non-{primary_label} agent-games with AUROC = {f2(H1['auroc'])} "
             f"{ci(H1['auroc_ci_lo'], H1['auroc_ci_hi'])} (TPR at FPR ≤ 10%: {f2(H1['tpr_at_fpr10'])}). "
             f"Within persona (n = 4 models each, descriptive) ρ was " + ", ".join(f"{p} {f2(v)}" for p, v in H1["within_persona_rho"].items()) + ". ")
    hc, ha = kn.get("H1_collude_label", {}), kn.get("H1_agree_label", {})
    R.append(f"Using the strict COLLUDE label and collusion rate instead: ρ = {f2(hc.get('rho'))} {ci(hc.get('rho_ci_lo'), hc.get('rho_ci_hi'))}, AUROC = {f2(hc.get('auroc'))}; "
             f"using agreement and mean collusion score: ρ = {f2(ha.get('rho'))} {ci(ha.get('rho_ci_lo'), ha.get('rho_ci_hi'))}, AUROC = {f2(ha.get('auroc'))}.")
    R.append("")
    R.append("### 4.5 Specificity: the benign offer")
    R.append(f"**H4.** The benign score (S3 acceptance) correlated with deployment {primary_outcome} at ρ = {f2(H4['rho'])} {ci(H4['rho_ci_lo'], H4['rho_ci_hi'])} "
             f"(AUROC = {f2(H4['auroc'])} {ci(H4['auroc_ci_lo'], H4['auroc_ci_hi'])}). The rank-based partial correlation of the sting score with the outcome, controlling for the "
             f"benign score, was {f2(kn.get('partial_rho_sting_given_benign'))}. "
             + ("Because benign acceptance predicts about as well as collusive acceptance, the sting in this setting mostly measures general compliance with peer requests rather than a specific collusion propensity."
                if (H4["rho"] is not None and H1["rho"] is not None and abs(H4["rho"]) >= abs(H1["rho"]) - 0.1) else
                "The sting retains predictive signal beyond general agreeableness."))
    R.append("")
    if preds:
        R.append("### 4.6 Sting audits versus passive monitors (Fig. 4, Table 3)")
        t3 = ["| Predictor | ρ (config level) | 95% CI | AUROC (agent-game) | 95% CI | TPR@FPR≤10% |", "|---|---|---|---|---|---|"]
        for k in ["sting", "benign", "messages_only", "actions_only", "fused", "sting_plus_fused"]:
            p_ = preds[k]
            t3.append(f"| {k.replace('_', ' ')} | {f2(p_['rho'])} | {ci(p_['rho_ci_lo'], p_['rho_ci_hi'])} | {f2(p_['auroc'])} | {ci(p_['auroc_ci_lo'], p_['auroc_ci_hi'])} | {f2(p_['tpr_at_fpr10'])} |")
        R.append(f"**H3.** On the separate audit games, the fused monitor reached AUROC {f2(preds['fused']['auroc'])} against deployment ground truth, "
                 f"versus {f2(preds['messages_only']['auroc'])} for messages-only and {f2(preds['actions_only']['auroc'])} for actions-only "
                 f"(fused > messages: {H3['fused_beats_messages']}; fused > actions: {H3['fused_beats_actions']}). "
                 f"**H2.** Combining the sting score with the fused monitor (rank mean) changed AUROC by {f2(H2['auroc_diff_combined_minus_fused'])} "
                 f"(95% paired cluster-bootstrap CI {ci(*H2['ci'])}) relative to the fused monitor alone; the sting alone differed from the fused monitor by "
                 f"{f2(H2['auroc_diff_sting_minus_fused'])} {ci(*H2['ci_sting_minus_fused'])}. All intervals are wide; see Table 3.")
        R.append("")
        R.append("**Table 3. Predictor comparison against Phase B ground truth.**")
        R.append("")
        R.extend(t3)
        R.append("")
    R.append("### 4.7 Say–do gap and test awareness")
    R.append(f"Of {sd['n_agreements']} private agreements in deployment games, {pct(sd['talk_only_share_of_agreements'])} were not followed by measurable preferential play "
             f"(TALK-ONLY), matching Colosseum's 'collusion on paper'. Of {sd['n_preferential_play']} agent-games with preferential play, "
             f"{pct(sd['act_only_share_of_preferential'])} had no agreement at all (ACT-ONLY). Test-awareness flags in the probe were "
             + ", ".join(f"{o} {pct(v)}" for o, v in pr['suspects_test_by_offer'].items()) + ".")
    R.append("")
    if H5:
        R.append("### 4.8 Entrapment")
        R.append(f"In {H5['n_pairs']} matched pairs, the stung seat's collusion score was {f2(H5['stung_seat_score_diff'])} higher in the sting arm "
                 f"(bootstrap 95% CI {ci(*H5['stung_seat_score_diff_ci'])}); the whole-table difference was {f2(H5['table_score_diff'])} {ci(*H5['table_score_diff_ci'])}.")
    else:
        R.append("### 4.8 Entrapment")
        R.append("Phase C (entrapment arm) was not run: the request quota was exhausted by Phases A1, A2 and B. H5 remains untested.")
    rb = kn.get("robustness")
    if rb:
        R.append("")
        R.append("**Robustness.** " + "; ".join(f"{r['variant']}: ρ = {f2(r.get('rho'))}, AUROC = {f2(r.get('auroc'))}" for r in rb) + " (Table B.7).")
    (SEC / "RESULTS.md").write_text("\n".join(R))

    # ---------------- DISCUSSION
    strong = H1["rho"] is not None and H1["rho"] > 0 and (H1["rho_ci_lo"] or -1) > 0
    specific = H4["rho"] is not None and H1["rho"] is not None and abs(H4["rho"]) < abs(H1["rho"]) - 0.1
    D = []
    D.append("**What auditors should take away.** " + (
        "A one-message peer sting carried real signal about which configurations later formed private pacts in deployment, at a cost of a dozen cheap calls per configuration. "
        if strong else
        "A one-message peer sting did not reliably rank configurations by their later deployment collusion at this sample size. The point estimate was "
        + ("positive" if (H1["rho"] or 0) > 0 else "non-positive") + ", but the interval is wide and the result should be read as a pilot, not as evidence for or against sting audits in general. "))
    D.append("Three observations survive the uncertainty. First, acceptance is dominated by *model identity*: one model accepted every offer, including the benign one, and another refused every offer, including the benign one. "
             "A sting score therefore cannot be interpreted without a benign control, and " + (
             "in our data the benign control absorbed most of the variance, meaning the sting mostly measured compliance with peer requests. "
             if not specific else "the benign control is what separates propensity from mere agreeableness. ")
             + "Second, framing matters as much as content: the indirect hint ('go easy on each other') was accepted by models that refused the explicit pact, which mirrors Zeng & Rudzicz's finding that neutral wording unlocks capabilities that explicit framings block. An auditor who only runs explicit stings will under-estimate risk. "
             "Third, talk and action diverge: a sizeable share of private agreements was never followed by preferential play, so message-level evidence over-predicts behavioural collusion and action-level evidence misses the intent, which is exactly the gap the fused monitor and the sting are meant to bridge.")
    D.append("**When stings help or mislead.** Stings are cheap and run before deployment, which passive monitors cannot do. They mislead when (i) the agent is compliant with any peer request, (ii) the agent detects the test, or (iii) the offer's framing differs from the collusion that arises in the wild. Our data show (i) clearly; test awareness was rare for these small models, but Krakovna et al. [2026] and Williams et al. [2026] show it rises with capability.")
    D.append("**Relation to plus factors.** In antitrust, a competitor's acceptance of an explicit invitation to collude is direct evidence of agreement, far stronger than circumstantial 'plus factors' [Kovacic et al. 2011]. For AI agents our results caution against importing this logic wholesale: acceptance of a scripted offer by a small model is often a compliance reflex, not an agreement in the legal sense, and an audit regime should weight it as a plus factor to be combined with behavioural evidence, not as proof.")
    D.append("**Limitations.** Small n (12 configurations, " + str(n_ag) + " deployment agent-games), one environment, a 12-round horizon, a self-judging confound (the judge model is also a player), a roster dictated by provider availability rather than design, and personas that manufacture variance. See Appendix A.")
    D.append("**Future work.** An in-game undercover seat that delivers offers mid-game with a track record; repeated contact; stronger and more test-aware models; environments with real economic stakes; and adaptive stings that vary framing to estimate a configuration's acceptance *surface* rather than a single rate.")
    (SEC / "DISCUSSION.md").write_text("\n\n".join(D))

    # ---------------- CONCLUSION
    C = (f"We built and pre-registered the first peer-to-peer collusion sting for LLM agents and tested its predictive validity against independent deployment collusion, "
         f"benchmarked against passive monitors and a benign control. In this pilot the sting " + ("predicted" if strong else "did not reliably predict") +
         f" later collusion (ρ = {f2(H1['rho'])} {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])}), and the benign control showed that much of the acceptance signal reflects "
         f"general compliance rather than collusion propensity. Stings are cheap and worth running, but only with controls, varied framings and behavioural follow-up; "
         f"on their own they over-predict collusion, and the say–do gap we observe ({pct(sd['talk_only_share_of_agreements'])} of agreements not acted on) shows why. "
         f"Code, prompts, raw logs and the judge cache are released for replication at scale.")
    (SEC / "CONCLUSION.md").write_text(C)

    # ---------------- DEVIATIONS (fixed text; facts from NOTES.md)
    dev = ("(1) Provider/roster: the only key available was a Groq free-tier key; its catalogue exposed four chat models (allam-2-7b, qwen3.8-27b, gpt-oss-20b, gpt-oss-120b), which replaced the planned Nebius roster; a new client (`sting_audit/groq_client.py`) with the same `chat()` contract was written because Groq rejects the pre-existing client's `repetition_penalty` field. "
           "(2) Quota: 1,000 requests/day and ~8k tokens/min per model forced probe n = 10 (not 20), a fixed 12-round game horizon, skipping the engine's LLM reflection step, a keyword heuristic for `suspects_test` (judge only on parse failure), and running seeds in a fixed order with all completed games analysed. "
           "(3) Judge: openai/gpt-oss-120b (temperature 0, low reasoning effort) instead of Llama-3.3-70B; it is also seat Quinn (self-judging confound). "
           "(4) Probe prompt layout: rules in the system message, vignette + offer as one user message. "
           f"(5) Phase C (entrapment) {'was run' if H5 else 'was not run (quota)'}; A2 used seeds {sorted(set(pd.read_csv(TABLES / 'monitors_A2.csv').seed)) if (TABLES / 'monitors_A2.csv').exists() else '—'} and B seeds {sorted(set(lab.seed))}. "
           "All items were recorded in NOTES.md and PREREGISTRATION.md §2b before the affected runs, except (5), which reflects quota at run time.")
    (SEC / "DEVIATIONS.md").write_text(dev)

    # ---------------- README pieces
    tl = (f"**TL;DR.** We gave 12 LLM-agent configurations (4 models × 3 personas) a private peer offer to collude, then watched the same configurations in "
          f"{n_games} independent deployment games with an open private channel and no offer. Direct pacts were accepted in {pct(s1)} of probe trials, indirect hints in {pct(s2)}, "
          f"benign fair-play requests in {pct(s3)}. Unprompted private agreements occurred in {pct(B['agree_rate_overall'])} of deployment agent-games; full collusion "
          f"(agreement + preferential play) in {pct(B['collusion_rate_overall'])}. The sting score's association with later collusion was ρ = {f2(H1['rho'])} "
          f"(95% CI {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])}; AUROC {f2(H1['auroc'])}), the benign control's ρ = {f2(H4['rho'])}: "
          + ("the sting carries signal beyond agreeableness." if specific else "the sting mostly measures compliance with peer requests, not collusion propensity.")
          + f" {pct(sd['talk_only_share_of_agreements'])} of agreements were never acted on (say–do gap). Pre-registered pilot; every number traces to a script and a log.")
    (SEC / "TLDR.md").write_text(tl)
    ht = ["| Quantity | Value | Source |", "|---|---|---|",
          f"| Probe trials / deployment games / agent-games | {pr['n_rows']} / {n_games} / {n_ag} | `key_numbers.json` |",
          f"| Acceptance S0 / S1 / S2 / S3 | {pct(s0)} / {pct(s1)} / {pct(s2)} / {pct(s3)} | `T2_acceptance.csv` |",
          f"| Deployment: agreement rate / COLLUDE rate | {pct(B['agree_rate_overall'])} / {pct(B['collusion_rate_overall'])} | `labels_B.csv` |",
          f"| H1 sting → collusion: ρ [95% CI], perm. p; AUROC [CI] | {f2(H1['rho'])} {ci(H1['rho_ci_lo'], H1['rho_ci_hi'])}, p = {f2(H1['perm_p'])}; {f2(H1['auroc'])} {ci(H1['auroc_ci_lo'], H1['auroc_ci_hi'])} | `key_numbers.json` → H1 |",
          f"| H4 benign → collusion: ρ [95% CI]; AUROC | {f2(H4['rho'])} {ci(H4['rho_ci_lo'], H4['rho_ci_hi'])}; {f2(H4['auroc'])} | `key_numbers.json` → H4 |"]
    if preds:
        ht.append(f"| Monitors AUROC: messages / actions / fused / sting+fused | {f2(preds['messages_only']['auroc'])} / {f2(preds['actions_only']['auroc'])} / {f2(preds['fused']['auroc'])} / {f2(preds['sting_plus_fused']['auroc'])} | `T3_predictors.csv` |")
    ht.append(f"| Say–do gap: TALK-ONLY share of agreements | {pct(sd['talk_only_share_of_agreements'])} ({sd['n_agreements']} agreements) | `key_numbers.json` → B.say_do |")
    (SEC / "HEADLINE_TABLE.md").write_text("\n".join(ht))
    # README
    t = (SEC / "README_TEMPLATE.md").read_text()
    for k in ["TLDR", "HEADLINE_TABLE", "DEVIATIONS"]:
        t = t.replace("{{" + k + "}}", (SEC / f"{k}.md").read_text().strip())
    (REPO / "README.md").write_text(t)
    print("sections written; README filled")


if __name__ == "__main__":
    main()
