# Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?

[![Pre-registered](https://img.shields.io/badge/pre--registered-624c534-blue)](PREREGISTRATION.md)
[![Track 3](https://img.shields.io/badge/Apart%20AI%20Collusion%20Sprint-Track%203%20%7C%20Q3.2-purple)](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25)
[![License: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)

Submission to the Apart Research **AI Collusion Research Sprint** (23–25 Oct 2026), Track 3 (Collusion Carriers and
Countermeasures), question 3.2 *"Can we disrupt collusion through introducing trusted agents?"*, with a question-2.2
fused monitor as baseline.

**Paper:** [`report/Sting_Audits_Apart_Collusion_Sprint.pdf`](report/Sting_Audits_Apart_Collusion_Sprint.pdf) ·
**Pre-registration:** [`PREREGISTRATION.md`](PREREGISTRATION.md) (commit [`624c534`](https://github.com/LSUDOKO/AI-Collusion-Research/commit/624c534), pushed before any audit/deployment game) ·
**Lab notebook:** [`NOTES.md`](NOTES.md) · **Key numbers:** [`results/tables/key_numbers.json`](results/tables/key_numbers.json)

{{TLDR}}

---

## 1. The idea in one picture

![Design](report/figures/fig1_design.png)

Law enforcement uses undercover stings to expose conspiracies. We ask whether the analogue works for LLM agents:
give an agent a **private offer of a secret pact from a peer** (out of game, cheap), and test whether its answer
predicts whether the same model-and-persona configuration **later colludes on its own** in independent deployment
games with an open private channel and no offer. We benchmark this *active* audit against *passive* monitors
(messages-only, actions-only, fused claims-vs-actions) and include a **benign fair-play offer** as a false-positive
control, so the sting is not just measuring agreeableness.

## 2. Headline results (proof: every number is produced by `sting_audit/analysis.py` from the raw logs in `results/raw/`)

{{HEADLINE_TABLE}}

| Figure | What it shows |
|---|---|
| ![](report/figures/fig2_acceptance.png) | **Fig. 2** Acceptance of each offer type (S0 designer control, S1 direct peer pact, S2 indirect hint, S3 benign) per model and persona, Wilson 95% CIs. |
| ![](report/figures/fig3_predictive_validity.png) | **Fig. 3** Predictive validity: sting score (x) vs deployment collusion (y), one point per configuration. |
| ![](report/figures/fig4_predictor_comparison.png) | **Fig. 4** AUROC of each predictor for deployment collusion with cluster-bootstrap CIs. |
| ![](report/figures/fig5_outcomes.png) | **Fig. 5** COLLUDE / TALK-ONLY / ACT-ONLY / NONE outcomes in deployment games by persona. |

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
python -m sting_audit.analysis all                                        # tables + key_numbers.json + figures
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

{{DEVIATIONS}}

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
