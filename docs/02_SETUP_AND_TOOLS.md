# 02 — Setup and tools

## 1. Project layout to create
```
sting-audits/                      # our public repo (git init here)
├── CLAUDE.md, docs/, templates/   # this instruction pack
├── collusion_hackathon/           # PRE-EXISTING starter repo (cloned, see below)
├── sting_audit/                   # NEW code written during the sprint
├── prompts/                       # NEW frozen prompts (offers, monitors, judges)
├── configs/                       # NEW run configs (yaml/json)
├── results/                       # raw logs, tables, figures (commit these)
├── report/                        # report.md draft + figures for the PDF
├── PREREGISTRATION.md             # committed BEFORE Phase B
├── NOTES.md                       # lab notebook
└── README.md                      # from templates/REPO_README.md
```
Keep the starter repo as a plain sub-folder (remove its `.git` after cloning, or add it as a
submodule) so the diff of what we changed is easy to show. Record the upstream commit hash in
`NOTES.md` and the README (`git -C collusion_hackathon rev-parse HEAD` before removing `.git`).

## 2. Environment (exact steps)
```bash
# prerequisites: git, Python 3.9+, uv  (install uv: curl -LsSf https://astral.sh/uv/install.sh | sh)
mkdir sting-audits && cd sting-audits && git init
git clone --depth 1 https://github.com/poseidon-research/collusion_hackathon.git
git -C collusion_hackathon rev-parse HEAD   # write into NOTES.md
cd collusion_hackathon
cp compute.env.example compute.env          # add NEBIUS_API_KEY (preferred) and/or OPENROUTER_API_KEY
./setup.sh llm-agent-collusion-2            # installs shared poseidon_compute + project venv
cd llm-agent-collusion-2 && source .venv/bin/activate   # or prefix commands with `uv run`
```
- **Never commit `compute.env`.** Add it to `.gitignore` at the repo root.
- **Do not set `LLM_MODEL`.**
- API keys: the starter README says hackathon keys are handed out via the event Slack/Luma; ask in
  the Discord help-desk channel (tag @Support) if needed. Nebius serves all four roster models;
  OpenRouter is the fallback and also serves closed models.

## 3. Smoke tests (must pass before any new code)
```bash
# from collusion_hackathon/llm-agent-collusion-2 with venv active
cd Collusion_Cleanup && python -m cleanup_llm.games.tournament --games 1 --steps 5 --out runs/smoke --roster small && cd ..
# success = "Tournament completed in … seconds" then "Results saved to runs/smoke"
cd Collusion_Liars_Bar && python src/game/game.py     # one baseline game, ~260 calls, ~11 min
```
If every call for one seat warns "is not a valid model ID", that seat is not reaching a model:
check the key/provider. Occasional `WARNING:agents.llm_agent` lines are tolerated.
All Liar's Bar commands must be run from inside `Collusion_Liars_Bar/` (prompt paths are relative).

## 4. Research tools (MCP) for literature and verification
Use these to verify every reference and to check novelty. Log each lookup in `NOTES.md`.

**Connectors from claude.ai appear in Claude Code automatically** when Claude Code is logged in with
the same claude.ai subscription account (run `/mcp` to see them; run `/status` if they're missing —
an `ANTHROPIC_API_KEY` in the environment disables them). Add or authenticate connectors at
claude.ai/customize/connectors. Useful ones for this project:

| Tool | Use it for |
|---|---|
| **alphaXiv** | Search arXiv, read full text of a paper, answer questions about a PDF. Primary tool: almost all cited work is on arXiv. |
| **Consensus** | Broad search over 220M+ papers; quick evidence summaries; find related work outside arXiv. |
| **Elicit** | Search papers and build comparison tables (method, setting, models, findings) for Related Work. |
| **Scite** | Check whether later papers support or contradict a claim before you rely on it. |
| **SciSpace** | Additional paper search (no account needed). |
| **Hugging Face** | Exact model IDs, sizes, licences for the Methods section. |
| **Context7** | Up-to-date library docs (pandas, scikit-learn, matplotlib, openai SDK) when debugging. |
| **Firecrawl** | Research-paper search and US legal search (antitrust "plus factors" background). |

To add Consensus directly to Claude Code instead (official server, OAuth sign-in on first use):
```bash
claude mcp add --transport http consensus https://mcp.consensus.app/mcp
```
Then `/mcp` to authenticate. Do not add other servers by guessed URLs; use claude.ai connectors.

**Verification protocol for each reference** (record result in `docs/07_LITERATURE.md` table):
1. Find the arXiv/DOI page with alphaXiv or WebFetch; confirm exact title, authors, year.
2. Confirm the specific claim you cite appears in the paper (alphaXiv answer_pdf_queries / read).
3. If not found → do not cite; or cite the organisers' summary explicitly ("as summarised in the
   sprint brief") only if the organisers cite it.

## 5. Python extras for analysis
Inside the project venv: `uv pip install pandas numpy scipy scikit-learn matplotlib seaborn pyyaml`
(check what's already installed first). Pin versions in `requirements-analysis.txt`.

## 6. GitHub
- Create a public repo `sting-audits` on the human's GitHub account (ask the human to create it or to
  authenticate `gh auth login`). Making the repo public is an irreversible-ish action: confirm with
  the human first.
- Push early (after setup) so the pre-registration commit has a public timestamp.
- Commit message convention: `prereg:`, `feat:`, `run:`, `analysis:`, `report:`.
