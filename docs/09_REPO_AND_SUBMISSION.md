# 09 — Repository and submission

## Public repo (GitHub) — final layout
```
sting-audits/
├── README.md                  # from templates/REPO_README.md
├── PREREGISTRATION.md         # committed before Phase B (hash cited in report)
├── NOTES.md                   # lab notebook (keep; shows process)
├── LICENSE                    # MIT for our code; starter code keeps its own licences
├── sting_audit/               # NEW sprint code
├── prompts/                   # NEW frozen prompts
├── configs/                   # run configs
├── tests/                     # mock tests + judge fixtures
├── results/
│   ├── raw/{probe,A2,B,C}/    # raw JSON/JSONL logs (commit them; they are small)
│   ├── tables/  figures/  logs/
│   └── cost_log.csv
├── report/report.md + figures/ + sting_audits_report.pdf
├── collusion_hackathon/       # PRE-EXISTING starter code (upstream commit hash in README)
└── docs/ templates/ CLAUDE.md # this instruction pack (fine to keep; shows method)
```
- `.gitignore`: `compute.env`, `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `experiments/game_records/`
  (we copy records into `results/raw/`).
- **Before pushing: scan for secrets** — `git grep -nE "sk-|NEBIUS_API_KEY=.+|OPENROUTER_API_KEY=.+"`
  must return nothing.
- README must contain a **"Pre-existing vs. new"** section listing (a) the starter repo + upstream
  commit, (b) every patched pre-existing file with a one-line description (e.g. `player.py`: added
  `extra_context`, 4 lines), (c) all new files.
- Tag the submitted version: `git tag submission-v1 && git push --tags`.

## Video (optional, only if time remains after the PDF is final)
3–5 min screen recording: problem (30 s) → design diagram (60 s) → key figures (2 min) → limitations
and takeaway (60 s). Upload unlisted to YouTube/Drive; add the link to the form and README.

## Final checklist (tick all before submitting)
- [ ] PDF made from the official template; ≤ 8 pages before references/appendices
- [ ] Abstract 150–250 words (count it)
- [ ] Author name(s) + affiliation(s) on the first page
- [ ] Appendix "Limitations and Dual-Use / Ethical Considerations" present
- [ ] Every number in the PDF matches `results/tables/key_numbers.json`
- [ ] Every reference is VERIFIED in `docs/07_LITERATURE.md` (no Berger 2025)
- [ ] Positive control reported; n and CIs reported; pre-registration hash + deviations listed
- [ ] Pre-existing work clearly marked in report (Methods + Appendix C) and README
- [ ] Repo public, link works in an incognito window, no secrets, tag `submission-v1`
- [ ] Figures readable in the PDF at 100% zoom; captions self-contained
- [ ] File name e.g. `Sting_Audits_<Surname>_Apart_Collusion_Sprint.pdf`

## Submitting (the human does this)
1. Go to https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25 →
   submission form ("Submit your project").
2. Enter title, abstract, authors/affiliations/emails, **Track 3: Collusion Carriers and
   Countermeasures**, upload the PDF, add repo (and video) links.
3. Confirm the confirmation email arrives (if not, email sprints@apartresearch.com).
4. **Target: submitted by Monday 26 Oct, 16:30 IST.** Hard deadline 17:29 IST (11:59 PM AoE Sunday).
5. Fixing mistakes: wrong form details → resubmit with the **same title**. A new PDF → new submission
   with a slightly different title, or email the PDF to sprints@apartresearch.com — before the deadline.
6. Help: Discord help-desk channel (tag @Support) or sprints@apartresearch.com.
