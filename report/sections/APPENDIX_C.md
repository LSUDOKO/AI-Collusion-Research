**Repository.** https://github.com/LSUDOKO/AI-Collusion-Research. Pre-registration: `PREREGISTRATION.md`, commit `{{PREREG_HASH}}`. Lab notebook: `NOTES.md`.

**Pre-existing work (not ours).** `collusion_hackathon/` is the sprint starter repository (github.com/poseidon-research/collusion_hackathon, commit `e6fb1308dae9cf97ae42aec1c5f7889d9e2291e8`), including `llm-agent-collusion-2/` (the code of Zeng & Rudzicz 2026, adapted by the organisers to hosted APIs), its rules, play/challenge/reflection prompts, game engine, record format, LLM client, model roster and the original designer offer text (our S0). We patched one pre-existing file: `Collusion_Liars_Bar/src/agents/player.py` (added `self.extra_context = ""` and appended it to the prompt in `choose_cards_to_play` and `decide_challenge`; 3 lines, marked `[sting_audit patch]`). Everything under `sting_audit/`, `prompts/`, `configs/`, `tests/`, `results/`, `report/` is new in this sprint.

**Reproduce.**
```
cd collusion_hackathon && cp compute.env.example compute.env  # LLM_BASE_URL=https://api.groq.com/openai/v1, LLM_API_KEY=<groq key>; do NOT set LLM_MODEL
./setup.sh llm-agent-collusion-2 && source llm-agent-collusion-2/.venv/bin/activate && cd ..
export PYTHONPATH=collusion_hackathon/util:.
python -m pytest tests -q                       # mock tests, no API calls
python -m sting_audit.probe --personas all --offers S0,S1,S2,S3 --n 10 --seed 7
python -m sting_audit.probe --client claude --models claude-haiku,claude-sonnet --n 10 --seed 7 --out results/raw/probe_claude   # exploratory
python -m sting_audit.run_games --phase A2 --personas all --seeds 101-103
python -m sting_audit.run_games --phase B  --personas all --seeds 201-204
python -m sting_audit.labels --phase A2 && python -m sting_audit.labels --phase B
python -m sting_audit.monitors --phase A2
python -m sting_audit.analysis all && python -m sting_audit.probe_extra
```
![Figure C1. Reproducibility evidence captured from the repository at build time: the mock test suite, the pre-registration commit preceding all games, the agreement judge on its hand-written fixtures, and the raw-log inventory.](paper_figs/shot_evidence.png)

Re-running the analysis on the committed raw logs reproduces every number in this report; judge and monitor calls are cached in `results/judge_cache.jsonl`. Seeds: probe 7; A2 101–103; B 201–204 (completed: A2 101 fair, B 202 neutral). Judge: {{JUDGE_MODEL}}, temperature 0.

**Deviations from the pre-registration.** {{DEVIATIONS}}

![Figure C2. Why the game phase stopped: the provider's rate-limit diagnosis recorded in the lab notebook, and the size of the two completed games from the cost log.](paper_figs/shot_quota.png)

**Cost.** {{COST}}

**AI assistance.** Code, literature search and drafting were assisted by Claude (Anthropic) running in Claude Code, with research connectors (alphaXiv, Consensus, SciSpace) used to locate and verify every cited paper against its full text; the author reviewed all code, results and text. No number in this report was produced by a language model: all statistics come from `sting_audit/analysis.py` run on the saved logs.
