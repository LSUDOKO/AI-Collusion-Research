# Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?

Submission to the Apart Research **AI Collusion Research Sprint** (23–25 Oct 2026), Track 3
(Collusion Carriers and Countermeasures), question 3.2, with a 2.2 fused-monitor baseline.

**Report:** `report/sting_audits_report.pdf` · **Pre-registration:** `PREREGISTRATION.md` (commit `<hash>`)

## TL;DR
<2–3 sentences with the headline result and its uncertainty — fill from key_numbers.json>

## What we did
1. **Sting probe:** agents receive a private peer offer — direct pact (S1), indirect hint (S2), or benign
   fair-play request (S3, control) — plus the original designer offer (S0, positive control).
2. **Passive audit games:** open private channel, no offer; scored by messages-only, actions-only and
   fused monitors.
3. **Deployment games (ground truth):** fresh games, open private channel, no offer; collusion =
   private agreement + preferential play.
4. **Compare** how well each audit predicts deployment collusion; test entrapment (if run).

## Reproduce
```bash
git clone <this repo> && cd sting-audits/collusion_hackathon
cp compute.env.example compute.env   # add NEBIUS_API_KEY or OPENROUTER_API_KEY; do NOT set LLM_MODEL
./setup.sh llm-agent-collusion-2 && source llm-agent-collusion-2/.venv/bin/activate && cd ..
python -m pytest tests -q            # mock tests, no API calls
python -m sting_audit.probe --models all --personas all --offers S0,S1,S2,S3 --n 20 --seed 7 --out results/raw/probe/
python -m sting_audit.run_games --phase A2 --personas all --seeds 101-103 --workers 4
python -m sting_audit.run_games --phase B  --personas all --seeds 201-204 --workers 4
python -m sting_audit.labels --phase A2 && python -m sting_audit.labels --phase B
python -m sting_audit.monitors --phase A2
python -m sting_audit.analysis all     # writes results/tables and results/figures
```
Re-running the analysis on the committed raw logs reproduces every number in the report
(judge calls are cached in `results/judge_cache.jsonl`). LLM sampling is not seeded by the API, so
re-running games gives statistically similar, not identical, logs.

## Pre-existing vs. new (required by sprint rules)
**Pre-existing (not our work):** `collusion_hackathon/` — the sprint starter repo
(github.com/poseidon-research/collusion_hackathon, commit `<upstream hash>`), including
`llm-agent-collusion-2/` (code for Zeng & Rudzicz 2026, arXiv 2605.27593, adapted by the organisers),
its rules, prompts, game engine, LLM client and the original designer offer text.

**Patched pre-existing files (sprint work):**
| File | Change |
|---|---|
| `llm-agent-collusion-2/Collusion_Liars_Bar/src/agents/player.py` | added `extra_context` (private-message block appended to play/challenge prompts), N lines |
| <others, if any> | |

**New in this sprint:** `sting_audit/` (persona wrapper, sting probe, open-channel game, runner,
labels, monitors, analysis, figures), `prompts/`, `configs/`, `tests/`, `results/`, `report/`,
`PREREGISTRATION.md`, `NOTES.md`.

## Ethics / dual use
See the report's appendix. Offer texts are plain and fixed (not optimised for acceptance). No
monitor-evasion techniques were developed.

## AI assistance
Code and drafting were assisted by Claude (Anthropic); the author reviewed all code, results and text.

## Licence
Our code: MIT. Starter code: see licences in `collusion_hackathon/`.
