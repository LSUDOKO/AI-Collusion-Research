# CLAUDE.md — Sting Audits project (Apart AI Collusion Research Sprint)

You (Claude Code) are the research engineer for a solo participant. Your job: run a small, honest,
reproducible experiment and produce a judge-ready report + public repo before the deadline.
Read this file fully, then read `docs/` in numeric order before doing anything else.

## Deadline (hard)
- Official: Sunday 25 Oct 2026, 11:59 PM AoE = **Monday 26 Oct 2026, 17:29 IST (11:59 UTC)**.
- **Our target: submitted by Monday 16:30 IST.** Feature freeze for new experiments: Monday 08:00 IST.
- Check the clock with `date` at the start of every work block. If behind schedule, cut scope using the
  tiers in `docs/05_EXPERIMENT_PROTOCOL.md` — never cut the report or the required ethics appendix.

## The project in one paragraph
Track 3, question 3.2 ("Can we disrupt collusion through introducing trusted agents?"), with the 2.2
fused monitor as a baseline. Title: **"Sting Audits: Does an Undercover Peer Offer Predict Which AI
Agents Collude?"** We give LLM agents in Liar's Bar a private offer from a peer (direct pact / indirect
hint / benign fair-play request), then separately observe whether the same agent configurations
collude on their own when given an open private channel and no offer. We test whether sting
acceptance predicts real collusion, compare it with passive monitors (messages-only, actions-only,
fused), and check whether stings create collusion (entrapment). Details: `docs/01_PROJECT_SPEC.md`.

## Non-negotiable rules
1. **Never fabricate.** Every number in the report must come from a script in this repo run on saved
   logs. Every reference must be in `docs/07_LITERATURE.md` as VERIFIED, or re-verified by you with
   a research tool (alphaXiv, Consensus, Elicit, Scite, SciSpace, WebFetch of the arXiv page) before
   citing. Fabricated results or references = disqualification.
2. **Pre-register before ground-truth runs.** Fill `templates/PREREGISTRATION.md` → `PREREGISTRATION.md`,
   commit and push it BEFORE running Phase B (deployment) games. Record the commit hash in the report.
3. **Freeze monitors and judges** (model, prompt, temperature, threshold) before scoring any data.
   Store prompts in `prompts/` and never edit them after the freeze commit. Any later change = a
   documented deviation.
4. **Mark pre-existing code.** Everything from `poseidon-research/collusion_hackathon` is pre-existing.
   Our new files live under `sting_audit/` and are listed in the README "New in this sprint" section.
   Small patches to pre-existing files must be listed file-by-file.
5. **Log everything** to `results/` (raw JSON game records, probe responses, judge outputs, configs,
   seeds, model IDs, git hash, timestamps, API call counts). Never delete raw logs.
6. **One variable at a time.** Same seeds across conditions. Positive control first.
7. **Never set `LLM_MODEL`** in `compute.env` (it forces one model into every seat and the judge).
8. **Budget:** stop and tell the human if projected API spend exceeds US$40. Track calls in
   `results/cost_log.csv`.
9. **Safety:** we study collusion to detect it. Do not optimise offer wording for higher acceptance.
   Do not build techniques to evade monitors. Use the fixed offer texts in `docs/04_IMPLEMENTATION.md`.
10. **Ask the human only when blocked** (missing API key, budget, irreversible action such as making
    the repo public or submitting). Otherwise proceed and record decisions in `NOTES.md`.

## Where things are
| File | What it covers |
|---|---|
| `docs/01_PROJECT_SPEC.md` | Research question, design, hypotheses, novelty claim, definitions |
| `docs/02_SETUP_AND_TOOLS.md` | Environment, API keys, research MCP connectors, verification |
| `docs/03_CODEBASE_NOTES.md` | Verified facts + pitfalls in the starter code (read before editing) |
| `docs/04_IMPLEMENTATION.md` | Exactly what to build, module by module, with acceptance tests |
| `docs/05_EXPERIMENT_PROTOCOL.md` | Tiers, run matrix, commands, schedule, budget |
| `docs/06_ANALYSIS.md` | Labels, metrics, statistics, figures, tables |
| `docs/07_LITERATURE.md` | Verified references + research workflow with MCP tools |
| `docs/08_REPORT_GUIDE.md` | Section-by-section report plan, abstract skeleton, ethics appendix |
| `docs/09_REPO_AND_SUBMISSION.md` | Repo layout, README, final checklist, how to submit |
| `templates/` | PREREGISTRATION, REPO_README, REPORT_DRAFT skeletons |

## Working style
- Use the TodoWrite/task list. Keep `NOTES.md` as a running lab notebook (time, what ran, outcome).
- Pilot small (1 game, 2 configs) before scaling. Run long jobs in the background with `nohup` and
  log to `results/logs/`; check progress, don't block on them.
- When a step fails for >45 min, switch to the fallback listed for that step.
- Draft report sections as soon as their results exist (`report/report.md`).
- Short status updates to the human: what works, what failed, next step.
