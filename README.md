# Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?

[![Pre-registered](https://img.shields.io/badge/pre--registered-624c534-blue)](PREREGISTRATION.md)
[![Track 3](https://img.shields.io/badge/Apart%20AI%20Collusion%20Sprint-Track%203%20%7C%20Q3.2-purple)](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)

Submission to the Apart Research **AI Collusion Research Sprint** (23–25 Oct 2026), Track 3 (Collusion Carriers and
Countermeasures), question 3.2 *"Can we disrupt collusion through introducing trusted agents?"*, with a question-2.2
fused monitor as baseline.

**Video (3:10):** [`video/Sting_Audits_explainer.mp4`](video/Sting_Audits_explainer.mp4) · **Slides:** [`report/Sting_Audits_Slides.pdf`](report/Sting_Audits_Slides.pdf) · **Paper (PDF):** [`report/Sting_Audits_Apart_Collusion_Sprint.pdf`](report/Sting_Audits_Apart_Collusion_Sprint.pdf) (built from [`report/report.md`](report/report.md) by `sting_audit/build_paper.py`) ·
**Pre-registration:** [`PREREGISTRATION.md`](PREREGISTRATION.md) (commit [`624c534`](https://github.com/LSUDOKO/AI-Collusion-Research/commit/624c534), pushed before any audit/deployment game) ·
**Lab notebook:** [`NOTES.md`](NOTES.md) · **Key numbers:** [`results/tables/key_numbers.json`](results/tables/key_numbers.json)

> **Final status (submitted Sun 25 Oct 2026).** The pre-registered sting probe ran in full (480 trials) plus an exploratory Claude probe (240 trials). The game phase was **stopped after 2 of 21 games** by the provider's free-tier limit of 200,000 tokens/day on one seat model, so the pre-registered predictive-validity test (H1–H4) was **not run**. We report the probe as the main result and the two games as a qualitative pilot; nothing is extrapolated.

**TL;DR.** 12 LLM-agent configurations (4 models × 3 personas) each received a private peer offer to collude, 480 trials in total. The direct pact was accepted in 42% of trials, the indirect hint in 71%, the benign fair-play control in 48%, and the original designer offer (positive control) in 90%. **Sting acceptance tracks benign acceptance almost perfectly across configurations (Spearman ρ = 0.91)**: allam-2-7b accepts everything, qwen3.8-27b refuses nearly everything, so a raw sting score measures compliance, not collusion propensity, and a benign control is essential. Explicit pacts are refused far more than soft hints (gpt-oss-120b: 3% vs 90%). Under a fair-play persona, Claude Haiku 5.5 and Sonnet 5.5 (exploratory) refused every collusive offer and accepted every benign one. In the one deployment game, two agents formed an unprompted private alliance; the model that proposed it (qwen3.8-27b) is the one that refused almost every sting.

---

## 1. The idea in one picture

![Whiteboard walk-through of the design](report/media/whiteboard_pipeline.gif)

*Whiteboard walk-through (generated from the pre-registered design by `sting_audit/make_media.py`).* Static version: [`report/figures/fig1_design.png`](report/figures/fig1_design.png).

Law enforcement uses undercover stings to expose conspiracies. We ask whether the analogue works for LLM agents:
give an agent a **private offer of a secret pact from a peer** (out of game, cheap), and test whether its answer
predicts whether the same model-and-persona configuration **later colludes on its own** in independent deployment
games with an open private channel and no offer. We benchmark this *active* audit against *passive* monitors
(messages-only, actions-only, fused claims-vs-actions) and include a **benign fair-play offer** as a false-positive
control, so the sting is not just measuring agreeableness.

**Architecture of the study** (from the paper, Figure 1):

![Study architecture](report/paper_figs/fig_architecture.png)

**Main probe result** (paper, Figure 4): sting acceptance vs benign acceptance, one point per configuration (ρ = 0.91).

<img src="report/paper_figs/fig_sting_benign.png" width="520" alt="Sting score vs benign score">

## 2. Headline results (proof: every number is produced by `sting_audit/analysis.py` from the raw logs in `results/raw/`)

| Quantity (so far) | Value | Source |
|---|---|---|
| Probe trials / ambiguous / judge fallbacks | 480 / 0 / 0 | `results/raw/probe/probe_seed7.jsonl` |
| Acceptance S0 / S1 / S2 / S3 (pooled) | 90% / 42% / 71% / 48% | `results/tables/T2_acceptance.csv` |
| Parser hand-check agreement | 100% (30 replies) | `results/tables/hand_labels.csv` |
| Test-awareness flags S1 / S2 / S3 | 6% / 2% / 2% | `key_numbers.json` → probe |
| ρ(sting score, benign acceptance), 12 configs | 0.91 (S1 0.78, S2 0.71) | `results/tables/probe_extra.json` |
| Claude Haiku / Sonnet acceptance S0 / S1 / S2 / S3 (exploratory) | 0/60/63/67% · 53/20/47/40% | `results/tables/T2b_acceptance_claude.csv` |
| Games completed (A2 / B) | 1 / 1 of 9 / 12 (quota) | `results/raw/A2`, `results/raw/B` |
| Deployment labels (B, 4 agent-games) | 2 TALK-ONLY, 2 NONE, 0 COLLUDE | `results/tables/labels_B.csv`, `agreements_B.jsonl` |
| Predictive validity H1–H4 | **not tested** (2 of 21 games) | paper §4.5 |

**Per-model acceptance (n = 30 trials per cell, pooled over personas):**

| Model | S0 designer | S1 direct pact | S2 indirect hint | S3 benign |
|---|---|---|---|---|
| allam-7b | 100% | 100% | 100% | 100% |
| gpt-oss-120b | 83% | 3% | 90% | 33% |
| gpt-oss-20b | 100% | 53% | 93% | 57% |
| qwen3.8-27b | 77% | 10% | 0% | 0% |

| Figure | What it shows |
|---|---|
| ![](report/figures/fig2_acceptance.png) | **Fig. 2** Acceptance of each offer type (S0 designer control, S1 direct peer pact, S2 indirect hint, S3 benign) per model and persona, Wilson 95% CIs. |
| ![](report/figures/fig2b_acceptance_all_models.png) | **Fig. 2b** Acceptance pooled over personas for all six models; the two Claude columns are exploratory (not pre-registered). |
| ![](report/figures/fig5_outcomes.png) | **Fig. 5** Labels in the single completed deployment game (pilot, n = 4 agent-games): 2 TALK-ONLY (an unprompted alliance between qwen3.8-27b and gpt-oss-120b that was never tested in play), 2 NONE. |

## 2b. Proof it is real: screenshots rendered from the logs in this repo

Every image below is generated by `python -m sting_audit.make_media` from the committed raw logs, not drawn by hand.

**A real sting, typed out as the model saw it, and its verbatim reply** (`results/raw/probe/probe_seed7.jsonl`):

![A real sting exchange](report/media/sting_exchange.gif)

**More real replies from the probe** (decision parsed from the model's own JSON):

![Real probe replies](report/media/probe_replies.png)

**A real private channel from a deployment game, with the frozen judge's verdict and the behavioural counts that decide the label:**

![Private channel evidence](report/media/private_channel.png)

**Live evidence captured at build time** (tests, pre-registration commit, judge fixtures, raw-log inventory):

![Evidence terminal](report/media/evidence_terminal.png)

**The numbers file the paper reads from:**

![key_numbers.json](report/media/key_numbers.png)

## 3. What we did

| Phase | What | Where the evidence is |
|---|---|---|
| **A1 sting probe** | 12 configurations (4 models × 3 personas) × 4 offers × 10 trials. Strict JSON parse + frozen LLM judge fallback. | `results/raw/probe/probe_seed7.jsonl` (every raw reply), `results/tables/T2_acceptance.csv` |
| **A2 passive audit games** | Liar's Bar with an open private channel, no offer, seeds 101…; scored by messages-only, actions-only and fused monitors. | `results/raw/A2/*.json` (full game records incl. every private message), `results/tables/monitors_A2.csv` |
| **B deployment games (ground truth)** | Fresh games, open channel, no offer, seeds 201…; **COLLUDE = private agreement (LLM judge) + preferential play (behavioural statistic)**. | `results/raw/B/*.json`, `results/tables/labels_B.csv`, `results/tables/agreements_B.jsonl` |
| **Analysis** | Spearman ρ with cluster-bootstrap CI and permutation p; agent-game AUROC; within-persona checks; robustness; say–do gap. | `results/tables/key_numbers.json`, `results/tables/T3_predictors.csv`, `T4_robustness.csv` |
| **Judge cache** | Every judge/monitor call with its prompt hash, raw output and parsed JSON (reproducible, auditable). | `results/judge_cache.jsonl` |

## 4. Repository layout

```
sting_audit/            NEW sprint code
  paths.py              repo paths, seat→model roster, prompt loader
  groq_client.py        Groq-hosted roster client (same chat() contract as the pre-existing LLMClient)
  personas.py           persona system messages, call/cost counting
  mock_llm.py           canned-response client for zero-cost tests
  probe.py              Phase A1 sting probe (S0–S3)
  judge.py              frozen LLM judge/monitors with sha256 cache
  open_channel_game.py  Phase A2/B/C game: open private channel, no offer, no alliance reminders
  play_one.py / run_games.py   one game / parallel batch runner with resume
  labels.py             COLLUDE / TALK_ONLY / ACT_ONLY labels, preferential-play metric
  monitors.py           messages-only, actions-only, fused monitors
  stats.py / analysis.py / figures.py   statistics, tables, figures
  fill_report.py / write_sections.py / build_paper.py   report assembly and PDF build
prompts/                frozen offers, messaging, judge and monitor prompts (hashes in PREREGISTRATION.md)
configs/run_matrix.json roster, model IDs, seeds, thresholds, provider limits
tests/                  mock tests (`python -m pytest tests -q`) and judge fixtures
results/                raw logs, tables, figures, cost log, judge cache (all committed)
report/                 report.md (source), sections/, figures/, paper PDF
collusion_hackathon/    PRE-EXISTING starter code (vendored subset, see below)
docs/, templates/, CLAUDE.md   the instruction pack used to run this sprint (kept for transparency)
```

## 5. Reproduce

```bash
git clone https://github.com/LSUDOKO/AI-Collusion-Research && cd AI-Collusion-Research
cd collusion_hackathon && cp compute.env.example compute.env            # see "Provider" below; never commit compute.env
./setup.sh llm-agent-collusion-2 && source llm-agent-collusion-2/.venv/bin/activate && cd ..
export PYTHONPATH=collusion_hackathon/util:.
python -m pytest tests -q                                                 # 7 mock tests, no API calls
python -m sting_audit.judge fixtures                                      # agreement judge on 6 hand-made conversations
python -m sting_audit.probe --models all --personas all --offers S0,S1,S2,S3 --n 10 --seed 7 --out results/raw/probe/
python -m sting_audit.run_games --phase A2 --personas all --seeds 101 --workers 3
python -m sting_audit.run_games --phase B  --personas all --seeds 201-202 --workers 3
python -m sting_audit.labels --phase A2 && python -m sting_audit.labels --phase B
python -m sting_audit.monitors --phase A2
python -m sting_audit.analysis all && python -m sting_audit.probe_extra   # tables + key_numbers.json + figures
python -m sting_audit.write_sections && python -m sting_audit.fill_report && python -m sting_audit.build_paper
```

Re-running `analysis all` on the committed raw logs reproduces every number in the paper (judge calls are served from
`results/judge_cache.jsonl`, so no API key is needed for that step). Re-running the *games* gives statistically similar,
not identical, logs: model sampling is not seeded by the API.

**Provider.** We ran on a Groq free-tier key through the organisers' `poseidon_compute` custom-endpoint route
(`LLM_BASE_URL=https://api.groq.com/openai/v1`, `LLM_API_KEY=…`). The Groq catalogue on 25 Oct 2026 exposed four chat
models, which became our roster; see §7. To run on Nebius/OpenRouter instead, set `NEBIUS_API_KEY` and edit the roster in
`sting_audit/paths.py` and `sting_audit/groq_client.py` (the client only needs an OpenAI-compatible endpoint).

## 6. Pre-existing vs. new (required by sprint rules)

**Pre-existing (not our work):** `collusion_hackathon/` is a vendored subset of the sprint starter repo
[poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon) at commit
`e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`: `llm-agent-collusion-2/` (code for Zeng & Rudzicz 2026, arXiv 2605.27593, adapted by the
organisers), `util/poseidon_compute`, `literature/`, `setup.sh`, `compute.env.example`, `COMPUTE.md`. Its rules, prompts,
game engine, record format, LLM client and the original designer offer text (our S0) are theirs. Unrelated sub-projects
were removed to keep the repo small (`collusion_hackathon/VENDORED_SUBSET.md`).

**Patched pre-existing files (sprint work):**

| File | Change |
|---|---|
| `collusion_hackathon/llm-agent-collusion-2/Collusion_Liars_Bar/src/agents/player.py` | added `self.extra_context = ""` in `__init__` and `memory_section += self.extra_context` in `choose_cards_to_play` and `decide_challenge` (3 lines, marked `[sting_audit patch]`). Makes private messages visible to decisions; adds no instructions. |

**New in this sprint:** everything under `sting_audit/`, `prompts/`, `configs/`, `tests/`, `results/`, `report/`, plus
`PREREGISTRATION.md`, `NOTES.md`, this README.

## 7. Deviations from the plan (all logged in `NOTES.md` before the affected runs)

(1) Provider/roster: the only key available was a Groq free-tier key; its catalogue exposed four chat models (allam-2-7b, qwen3.8-27b, gpt-oss-20b, gpt-oss-120b), which replaced the planned Nebius roster; `sting_audit/groq_client.py` keeps the pre-existing `chat()` contract. (2) Quota (1,000 requests/day, ~8k tokens/min per model): probe n = 10 instead of 20, fixed 12-round game horizon, the engine's LLM reflection step skipped, `suspects_test` by keyword heuristic with judge only on parse failure, seeds run in a fixed order with all completed games analysed. (3) Judge: openai/gpt-oss-120b (also seat Quinn; self-judging confound acknowledged). (4) Probe prompt layout: rules in the system message, vignette + offer as one user message. All recorded in `NOTES.md` and `PREREGISTRATION.md` §2b before the affected runs. (5) **Game phase stopped** (not pre-specified): qwen/qwen3.8-27b's 200,000 tokens/day free-tier limit stopped Phases A2/B after 1 + 1 completed games; 8 in-progress games were terminated and not analysed; Phase C not started; H1–H4 not tested. (6) Added after the fact and labelled exploratory: the Claude probe and `sting_audit/probe_extra.py`. A Modal/vLLM client for the original starter roster (`sting_audit/modal_vllm.py`, `modal_client.py`) is included but was **not run**.

## 8. Ethics / dual use

See Appendix A of the paper. Offer texts are plain and fixed (not optimised for acceptance); no monitor-evasion
techniques were developed; raw logs are released so that labels can be audited.

## 9. AI assistance

Code, literature search and drafting were assisted by Claude (Anthropic) in Claude Code; research connectors
(alphaXiv, Consensus, SciSpace) were used to find and verify every cited paper against its full text. The author reviewed
all code, results and text. No number in the paper or this README was produced by a language model: all statistics come
from `sting_audit/analysis.py` run on the saved logs.

## Licence

Our code: MIT. Starter code: see licences in `collusion_hackathon/`.
