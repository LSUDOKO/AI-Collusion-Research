# 05 — Experiment protocol, schedule and budget

## Scope tiers (finish each tier fully before starting the next)
| Tier | Contents | Must be done by (IST) |
|---|---|---|
| **0** | Setup + smoke tests; mock tests; S0 positive control; Phase A1 sting probe (S0–S3, 12 configs, n=20) | **Sun 21:00** |
| **1** | Pre-registration commit; Phase A2 audit games (9); Phase B deployment games (12); labels; H1 + H4 analysis | launch by **Sun 23:30**, analysed by **Mon 06:00** |
| **2** | Messages-only + fused LLM monitors; head-to-head H2/H3 | **Mon 08:00** (feature freeze) |
| **3** | Phase C entrapment (9 sting + 9 control games); stronger-model probe; in-game undercover seat | only if Tier 2 done before **Mon 03:00** |

If time runs short, the minimum publishable result is Tier 0 + Tier 1 (sting acceptance vs. ground-truth
collusion, with S3 control and actions-only baseline). Never skip the positive control.

## Run matrix
Configurations: models {llama-3.1-8b, llama-3.2-3b, ministral-8b, qwen2.5-7b} × personas
{neutral, competitive, fair} = 12. Seats fixed: Lily=llama-3.1-8b, Luke=llama-3.2-3b,
Mike=ministral-8b, Quinn=qwen2.5-7b. Persona is set per game (all seats share it).

| Phase | What | Count | Seeds | Approx. calls |
|---|---|---|---|---|
| Smoke | Cleanup smoke + 1 baseline Liar's Bar game | 2 | — | ~300 |
| Pos. control (in-game, optional) | `game_series_secret_channel.py --games 2 --trigger-game 1 --trigger-round 2 --chosen-player random --allow-refusal` | 2 games | — | ~600 |
| A1 probe | 12 configs × {S0,S1,S2,S3} × n=20 | 960 trials | 7 | ~1,100 + judge |
| A2 audit games | 3 personas × 3 seeds, open channel | 9 games | 101–103 | ~4,000–5,500 |
| B deployment games | 3 personas × 4 seeds, open channel | 12 games | 201–204 | ~5,000–7,000 |
| Labels + monitors | judge calls | ~300 | — | ~300 |
| C entrapment (Tier 3) | 3 personas × 3 seeds × {sting, control} | 18 games | 301–303 | ~8,000–10,000 |

Calls per open-channel game are an estimate (baseline game ≈ 260 calls; messaging adds up to 2 calls
per turn). Measure the real number on the pilot game and update this table in `NOTES.md`.

## Commands (after implementation; run from repo root with the venv active)
```bash
# Tier 0
python -m sting_audit.probe --models all --personas all --offers S0,S1,S2,S3 --n 20 --seed 7 --out results/raw/probe/
python -m sting_audit.analysis probe          # acceptance table + Wilson CIs + Fig. 2 draft

# Pilot (1 game, check cost/time/fallbacks, read the transcript yourself)
python -m sting_audit.run_games --phase PILOT --personas competitive --seeds 999 --workers 1

# Tier 1 (only after PREREGISTRATION.md is committed and pushed)
nohup python -m sting_audit.run_games --phase A2 --personas all --seeds 101-103 --workers 4 > results/logs/A2.out 2>&1 &
nohup python -m sting_audit.run_games --phase B  --personas all --seeds 201-204 --workers 4 > results/logs/B.out 2>&1 &
python -m sting_audit.labels --phase B ; python -m sting_audit.labels --phase A2
python -m sting_audit.analysis main

# Tier 2
python -m sting_audit.monitors --phase A2
python -m sting_audit.analysis predictors

# Tier 3
nohup python -m sting_audit.run_games --phase C --personas all --seeds 301-303 --workers 4 --pre-sting S1 --with-controls > results/logs/C.out 2>&1 &
```
Start with `--workers 4`; if the provider returns many 429 errors, drop to 2. Check progress every
20–30 min (`ls results/raw/B | wc -l`, tail logs) and keep working on analysis code meanwhile.

## Schedule (IST) — adjust in NOTES.md if reality differs
| When | Task |
|---|---|
| Sun 16:30–17:30 | Setup, keys, smoke tests, git repo, push skeleton |
| Sun 17:30–19:00 | paths/mock/personas/probe/judge; probe pilot; hand-check 30 replies |
| Sun 19:00–20:30 | Full A1 probe running in background; build open-channel game + mock tests |
| Sun 20:30–21:30 | Real pilot game; read its transcript; fix issues; measure cost/time |
| Sun 21:30–22:30 | labels.py on pilot game; judge fixtures; **freeze prompts; commit PREREGISTRATION.md; push** |
| Sun 22:30–23:30 | Launch A2 + B in background; write Methods section while waiting |
| Mon 00:00–06:00 | Runs finish; labels; monitors (Tier 2); analysis; (human sleeps; agent continues if allowed) |
| Mon 06:00–08:00 | Figures, tables, robustness checks; **feature freeze 08:00** |
| Mon 08:00–13:00 | Write report (Results, Intro, Related Work, Discussion, Abstract, Ethics appendix) |
| Mon 13:00–15:00 | Reference re-verification, number cross-check, repo README, page/word counts |
| Mon 15:00–16:00 | Human pastes into template, exports PDF, final read |
| **Mon by 16:30** | **Human submits** (form on sprint page; Track 3). Deadline 17:29. |

## Budget
- Small open models on Nebius are cheap (the starter README describes a Liar's Bar game as costing
  cents). Still: log calls per run, compute cost from the provider dashboard after the pilot, and
  stop + ask the human if the projected total exceeds US$40.
- The judge (≥70B model) is the most expensive per call; caching keeps it bounded.

## Exclusion rules (pre-register)
- Exclude a game if any seat used fallback decisions on >20% of its turns, or the game crashed.
  Re-run with the next unused seed (e.g. 205, 206 for Phase B) and log the substitution.
- Probe rows with `decision=AMBIGUOUS` after the judge are excluded from acceptance rates and counted
  separately.

## Fallbacks if blocked (>45 min)
- Open-channel game won't work → run Phase B with the designer-channel game but **remove the alliance
  reminders** (subclass and override `handle_challenge` / `secret_communicate` prompts) and offer the
  channel to every player in round 1 (allow refusal); collusion must still come from their messages.
- Judge model unavailable → use the strongest model you can reach on OpenRouter; record exact ID.
- Provider rate limits → reduce workers; cut Phase B to 3 seeds per persona; keep A2 at 2 seeds.
- Out of time for monitors → report sting vs actions-only baseline (no LLM) and state the gap.
