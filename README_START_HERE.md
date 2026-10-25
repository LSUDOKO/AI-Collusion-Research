# START HERE (for you, the human)

This pack tells Claude Code exactly how to build, run, analyse and write up your sprint project
**"Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?"** (Track 3).
Deadline: **Monday 26 Oct 2026, 17:29 IST**. Plan to submit by **16:30 IST**.

## 1. Before you start (10 minutes)
1. Have an API key: **Nebius** (preferred) or **OpenRouter**. Hackathon keys come via the event
   Slack/Luma — ask in Discord help-desk (tag @Support) if you don't have one. Add ~US$10–20 credit.
2. Install: `git`, `uv` (https://docs.astral.sh/uv/), Python 3.9+, and Claude Code.
3. Log Claude Code in with your **claude.ai account** (`/login`) so your connectors (alphaXiv,
   Consensus, Elicit, Scite, SciSpace, Hugging Face…) are available; check with `/mcp`.
   Optional: `claude mcp add --transport http consensus https://mcp.consensus.app/mcp`
4. GitHub account ready (`gh auth login` lets Claude Code create/push the repo).

## 2. Set up the folder
```bash
mkdir sting-audits && cd sting-audits
# unzip this pack here so CLAUDE.md, docs/, templates/ sit in this folder
claude
```
Claude Code reads `CLAUDE.md` automatically.

## 3. Paste this kickoff prompt into Claude Code
```
Read CLAUDE.md and every file in docs/ in order, then templates/. Then:
1) Create a task list from docs/05_EXPERIMENT_PROTOCOL.md (Tiers 0–3) and docs/09 checklist.
2) Do the setup in docs/02 (I will paste my API key into compute.env when you ask).
3) Build and test in the order of docs/04, starting with the mock client.
4) Run Tier 0, show me the probe acceptance table and 5 sample replies, then continue to Tier 1.
Follow every non-negotiable rule in CLAUDE.md (no fabricated numbers or references; pre-register
before Phase B; mark pre-existing code). Check the time with `date` at each step and cut scope by
tier if behind. Keep NOTES.md updated. Ask me only when blocked.
```

## 4. What you do yourself
| When | You |
|---|---|
| Start | Paste the API key into `collusion_hackathon/compute.env` (never commit it) |
| Sun ~20:00 | Look at the probe table + sample replies; say "continue" |
| Sun ~22:00 | Approve the pre-registration commit and making the GitHub repo public |
| Before sleeping | Allow Claude Code to keep running the overnight batch (or leave it running) |
| Mon ~08:00 | Read figures + key numbers; ask questions; let it write the report |
| Mon ~13:00 | Read the full draft; fix anything unclear; check your name/affiliation |
| Mon 14:00–15:30 | Copy the template (link in docs/08), paste text + figures, export PDF |
| **Mon by 16:30** | Submit on the sprint page (Track 3), upload PDF, add repo link; check the confirmation email |

## 5. If things go wrong
- Behind schedule → tell Claude Code: "Cut to the minimum publishable scope (Tier 0 + Tier 1)."
- API errors / no key → Discord help-desk @Support or sprints@apartresearch.com.
- Any result is publishable if honest — including "the sting did not predict collusion".
- Submit *something* before 17:29 IST even if unfinished.
