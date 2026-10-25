# 08 — Report guide (what judges score and how to write it)

## Requirements (from the sprint Guidelines tab)
- PDF using the **official template** (Google Docs; make a copy):
  https://docs.google.com/document/d/1Y5wd3VRbXU5N08BvAGiJUQTaWbMCSPjhzXsR-ozuehg/copy?usp=sharing
- ≤ 8 pages excluding references and appendices (aim for 5–7).
- Title + abstract of **150–250 words**; author names + affiliations ("Independent" is fine).
- **Required appendix: "Limitations and Dual-Use / Ethical Considerations".**
- Optional: public GitHub repo link; 3–5 min video.
- Judges score 1–5 on: Impact & Innovation; Execution Quality; Presentation & Clarity.

## Workflow
1. Claude Code writes `report/report.md` following `templates/REPORT_DRAFT.md`, with figure files in
   `report/figures/` and every number taken from `results/tables/key_numbers.json`.
2. The human copies the template, pastes section text, inserts figures (width ≈ 16 cm), sets captions,
   and exports **File → Download → PDF**. (If a Google Docs connector is available to Claude Code,
   it may fill the copy directly; the human still checks the result.)
3. Final checks with `docs/09_REPO_AND_SUBMISSION.md`.

## Section plan and page budget
| Section | Pages | Content |
|---|---|---|
| Abstract | — | 150–250 words; skeleton below |
| 1 Introduction | 0.75 | Problem (agent collusion; passive monitors miss it); undercover-officer analogy; the gap (no peer sting tested for predictive validity); contributions (3 bullets); one-sentence headline result |
| 2 Related Work | 0.75 | Plan in `docs/07_LITERATURE.md` |
| 3 Methods | 1.5–2 | Environment (Liar's Bar, rules in one paragraph, starter code credited as pre-existing); collusion definition + operationalisation; configs (Table 1 with exact model IDs, provider, sampling); Phase A1 offers (quote S1–S3 in full); Phase A2/B open-channel game (neutral messaging prompt; note we removed harness alliance reminders); labels; predictors; statistics; pre-registration link + commit hash; exclusions |
| 4 Results | 2–2.5 | 4.1 Positive control (S0 vs Zeng). 4.2 Who accepts stings (Fig. 2). 4.3 Unprompted collusion in deployment (Fig. 5). 4.4 Does the sting predict? (Fig. 3, H1, within-persona). 4.5 Specificity (S3, H4). 4.6 Sting vs passive monitors (Fig. 4, H2/H3). 4.7 Say–do gap; suspicion. 4.8 Entrapment (if run). |
| 5 Discussion | 0.75 | What auditors should take away; when stings work/fail; relation to plus factors; limitations summary; future work (in-game undercover seat, stronger models, other environments, adaptive agents that detect stings) |
| 6 Conclusion | 0.25 | 3–4 sentences |
| References | — | Only verified entries from `docs/07_LITERATURE.md`; consistent style |
| Appendix A | — | **Limitations and Dual-Use / Ethical Considerations** (required) |
| Appendix B | — | Prompts (offers, messaging, judge/monitor prompts), parser audit, robustness table, exclusions, cost |
| Appendix C | — | Reproducibility: repo URL, commands, seeds, upstream starter-repo commit, what is pre-existing vs new, AI-assistance statement |

## Title options
- Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude? (preferred)
- Undercover Agents for AI Agents: Testing Sting Audits Against Passive Collusion Monitors

## Abstract skeleton (fill numbers only from key_numbers.json; 150–250 words)
> LLM agents can collude, and passive monitors that read transcripts or actions often miss it. Law
> enforcement uses undercover stings; we ask whether an analogous **sting audit** — a private offer
> of a secret pact from a peer agent — predicts which agent configurations later collude on their own.
> In Liar's Bar (4 open-weight models × 3 personas = 12 configurations), we measured acceptance of
> direct, indirect and benign (control) peer offers, then ran separate deployment games with an open
> private channel and no offer, labelling collusion as a private agreement followed by preferential
> play. [Positive control result.] Sting acceptance was [X–Y]% across configurations [vs benign Z%].
> [H1 result: ρ = …, 95% CI …; AUROC = …]. [H3/H2: comparison with messages-only, actions-only and fused
> monitors.] [Say–do gap result.] [Entrapment result, if run.] Our results suggest that [one-sentence
> takeaway, honest about uncertainty]. This is a small pre-registered pilot (n = …); we release code,
> prompts and logs.

## Writing rules
- Lead every Results subsection with the answer, then the evidence. Put the n next to every rate.
- Use "we find/observe" for measured results and "suggests" for interpretation. No hype words.
- Every figure has a self-contained caption (what, n, error bars meaning).
- Distinguish clearly: pre-registered (confirmatory) vs exploratory analyses; list deviations.
- State what is new in this sprint vs pre-existing (starter code, original offer prompt).
- AI assistance: one sentence in Appendix C, e.g. "Code and drafting were assisted by Claude; the
  author reviewed all code, results and text." (AI tools are allowed; honesty about use is good practice.)

## Appendix A — Limitations and Dual-Use / Ethical Considerations (draft points)
**What the results do and do not establish**
- Pilot scale: one game, four small open models, three personas, few games per configuration.
- Personas manipulate propensity by design; cross-persona prediction may be easier than real-world
  prediction; we report within-persona results to show this.
- The sting is a vignette probe embedded in a game state, not an in-game undercover seat; agents might
  respond differently mid-game or to repeated contact.
- Labels rely on an LLM judge plus a behavioural threshold; we hand-checked a sample (report agreement).
- Stochastic sampling without API seeds; results may vary across providers/model versions.
- Agents may recognise tests (`suspects_test` rate); more capable models may detect stings more often,
  which would weaken sting audits — an open problem.
- Liar's Bar collusion harms other players in a game, not real people; external validity is limited.

**Dual-use risks and mitigations**
- Our offer texts show how easily agents can be recruited into secret pacts; an attacker could use
  similar messages to recruit agents. Mitigation: we used three plain, fixed texts, did not optimise
  wording for acceptance, and do not release any optimised persuasion prompts.
- Detailed knowledge of what passive monitors miss could help colluders evade them; we report
  aggregate monitor performance and do not build evasion techniques.
- Entrapment: stings can create the behaviour they detect (Phase C measures this). Deploying sting
  audits on production agents needs governance: who may run them, disclosure, and how results are
  used (e.g., not as sole evidence) — analogous to legal limits on entrapment.
- Evaluation awareness: publicising sting formats may teach future models to recognise them;
  auditors should rotate and vary probes.
