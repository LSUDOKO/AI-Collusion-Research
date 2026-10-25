Inference ran on a Groq free-tier key and, for the exploratory Claude probe (240 calls in the A1 row), on the author's Claude subscription through the Claude Code CLI; no API charges were incurred. Total LLM calls logged: 1,327 (players + probe; judge/monitor calls are additionally recorded in `results/judge_cache.jsonl`).

| Phase | Calls | Empty responses |
|---|---|---|
| A1 | 1,000 | 4 |
| A2 | 61 | 3 |
| B | 59 | 4 |
| PILOT | 207 | 0 |

Judge/monitor calls cached: 28 (model openai/gpt-oss-120b).