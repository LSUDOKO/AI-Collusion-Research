# 07 — Literature: verified references and research workflow

Status legend: **VERIFIED** = title/authors/ID confirmed on the arXiv/publisher page on 25 Oct 2026
(cross-checked against the organisers' list `collusion_hackathon/literature/papers.csv`).
**CHECK CLAIM** = the paper exists, but re-read the specific sentence you cite before using it.
Anything not in this table must be verified with a research tool before citing.

## Core references (cite these)
| Short cite | Title | Authors | ID / venue | URL | Use in report |
|---|---|---|---|---|---|
| Zeng & Rudzicz 2026 | Voluntary Collusion with Secret Tools in Competing LLM Agents | Xijie Zeng, Frank Rudzicz | arXiv 2605.27593 | https://arxiv.org/abs/2605.27593 | Closest prior work; starter code; positive control. VERIFIED. Claims to quote (CHECK CLAIM in their tables): most models accept at/near 100%; only explicit ethical framing reduces adoption; offer comes from a "game designer" tool. |
| Tao et al. 2026 | GroupGuard: A Framework for Modeling and Defending Collusive Attacks in Multi-Agent Systems | Yiling Tao, Xinran Zheng, Shuo Yang, Meiling Tao, Xingjun Wang | arXiv 2603.13940 | https://arxiv.org/abs/2603.13940 | Prior honeypot inducement in MAS; our novelty boundary. VERIFIED. |
| Nakamura et al. 2026 | Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems | Mason Nakamura, Abhinav Kumar, Saswat Das, et al. | arXiv 2602.15198 | https://arxiv.org/abs/2602.15198 | Action-based auditing; "collusion on paper"; message vs action disagreement. VERIFIED. |
| Agrawal et al. 2025 | Evaluating LLM Agent Collusion in Double Auctions | Kushal Agrawal, Verona Teo, Juan J. Vazquez, et al. | arXiv 2507.01413 | https://arxiv.org/abs/2507.01413 | Definition ("secretive cooperation that harms another party"); oversight effects. VERIFIED. |
| Rose et al. 2026 | Detecting Multi-Agent Collusion Through Multi-Agent Interpretability | Aaron Rose, Carissa Cullen, Sahar Abdelnabi, Philip Torr, Brandon Gary Kaplowitz, Christian Schroeder de Witt | arXiv 2604.01151 | https://arxiv.org/abs/2604.01151 | Definition (communication + harmful action); white-box detectors; NARCBench. VERIFIED. |
| Nguyen et al. 2026 | TraceGuard: Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol | Khanh Linh Nguyen, Hoa Nghiem, Tu Tran | arXiv 2604.03968 | https://arxiv.org/abs/2604.03968 | Structured/fused monitors (our 2.2 baseline). VERIFIED. |
| Tailor 2025 | Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs | Om Tailor | arXiv 2510.04303 | https://arxiv.org/abs/2510.04303 | Calibrated detector fusion at fixed FPR. VERIFIED. |
| Arike et al. 2026 | How does information access affect LLM monitors' ability to detect sabotage? | Rauno Arike, Raja Mehta Moreno, Rohan Subramani, Shubhorup Biswas, Francis Rhys Ward | arXiv 2601.21112 | https://arxiv.org/abs/2601.21112 | "Less-is-more" monitor context. VERIFIED. |
| Shi et al. 2026a | When Agents Lie: Premeditation, Persistence, and Exploitation in Repeated Games | Jerick Shi, Terry Jingcheng Zhang, Bernhard Schölkopf, et al. | arXiv 2607.05132 | https://arxiv.org/abs/2607.05132 | Private plans vs public announcements (say–do). VERIFIED. |
| Shi, Zhang & Yang 2026 | Emergent Collusion in Long-Horizon LLM Agent Interaction | Xinrui Shi, Yanzhe Zhang, Diyi Yang | arXiv 2609.24967 | https://arxiv.org/abs/2609.24967 | Collusion emerges without planted offers. VERIFIED. |
| Idowu et al. 2026 | Mapping Human Anti-collusion Mechanisms to Multi-agent AI Systems | Jamiu Idowu, Ahmed Almasoud, Ayman Alfahid | arXiv 2601.00360 (Knowledge-Based Systems) | https://arxiv.org/abs/2601.00360 | Human anti-collusion tools (incl. stings/leniency) mapped to MAS; "boundary problem". VERIFIED; CHECK CLAIM for stings. |
| Zhou et al. 2026 | CABAL: Multi-Agent Simulacra for Tracing the Effects of Collusive Bidding in Peer Review | Jicheng Zhou, Kemou Li, Kahim Wong, et al. | arXiv 2609.05227 | https://arxiv.org/abs/2609.05227 | Detectors confounded by benign affinity → motivates S3 control. VERIFIED. |
| Kale et al. 2025 | Reliable Weak-to-Strong Monitoring of LLM Agents | Neil Kale, Chen Bo Calvin Zhang, Kevin Zhu, et al. | arXiv 2508.19461 | https://arxiv.org/abs/2508.19461 | Monitoring awareness degrades monitors (relevant to `suspects_test`). VERIFIED. |
| Greenblatt et al. 2023 | AI Control: Improving Safety Despite Intentional Subversion | Ryan Greenblatt, Buck Shlegeris, Kshitij Sachan, Fabien Roger | arXiv 2312.06942; ICML 2024 | https://arxiv.org/abs/2312.06942 | Trusted/untrusted monitoring; planted-attack evaluation. VERIFIED. |
| Hammond et al. 2025 | Multi-Agent Risks from Advanced AI | Lewis Hammond, Alan Chan, Jesse Clifton, et al. | arXiv 2502.14143 (Cooperative AI Foundation TR #1) | https://arxiv.org/abs/2502.14143 | Framing: collusion as a multi-agent risk. VERIFIED. |
| Motwani et al. 2024 | Secret Collusion among AI Agents: Multi-Agent Deception via Steganography | Motwani, Baranchuk, Strohmeier, et al. | arXiv 2402.07510; NeurIPS 2024 | https://arxiv.org/abs/2402.07510 | Covert collusion background. VERIFIED. |
| Mathew et al. 2024 | Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs | Mathew, Matthews, McCarthy, et al. | arXiv 2410.03768; IJCNLP-AACL 2025 | https://arxiv.org/abs/2410.03768 | Passive oversight limits. VERIFIED. |
| Fish et al. 2024 | Algorithmic Collusion by Large Language Models | Sara Fish, Yannai A. Gonczarowski, Ran I. Shorrer | arXiv 2404.00806 | https://arxiv.org/abs/2404.00806 | LLM collusion in markets (intro). VERIFIED. |
| Keppo et al. 2026 | On the Fragility of AI Agent Collusion | Jussi Keppo, Yuze Li, Gerry Tsoukalas, Nuo Yuan | arXiv 2603.20281 | https://arxiv.org/abs/2603.20281 | Collusion depends on heterogeneity/patience (intro/discussion). VERIFIED. |
| Calvano et al. 2020 | Artificial Intelligence, Algorithmic Pricing, and Collusion | Calvano, Calzolari, Denicolò, Pastorello | AER 110(10):3267–97, doi:10.1257/aer.20190623 | https://www.aeaweb.org/articles?id=10.1257/aer.20190623 | Classic algorithmic-collusion result. VERIFIED. |
| Kovacic et al. 2011 | Plus Factors and Agreement in Antitrust Law | Kovacic, Marshall, Marx, White | Michigan Law Review 110(3):393 | https://repository.law.umich.edu/mlr/vol110/iss3/1 | Antitrust "plus factors": accepting a sting ≈ direct evidence of willingness to agree. In organisers' list; CHECK CLAIM. |

## Optional / background (cite only if used)
| Short cite | Title | ID | URL | Note |
|---|---|---|---|---|
| Krakovna et al. 2026 | Realistic honeypot evaluations for scheming propensity | arXiv 2605.29729 | https://arxiv.org/abs/2605.29729 | Honeypot tests + evaluation awareness; strong related work for stings. Found by our checker — re-confirm before citing. |
| Williams et al. 2026 | Predicting LLM Safety Before Release by Simulating Deployment | arXiv 2607.07184 | https://arxiv.org/abs/2607.07184 | Pre-deployment evals vs deployment behaviour (predictive validity framing). Re-confirm. |
| Tran & Yu 2026 | Is Anyone Enforcing the Cartel? What Reinforcement Learning Teaches LLM Agents in Markets | arXiv 2610.28787 | https://arxiv.org/abs/2610.28787 | Counterfactual audit forcing a cartel member to cheat. Re-confirm. |
| Das et al. 2026 | You Can't Escape Your Own Activations: Evaluation Awareness and Multi-Agent Monitoring | arXiv 2609.03035 | https://arxiv.org/abs/2609.03035 | Evaluation awareness vs probes. Re-confirm. |
| Järviniemi 2025 | Subversion via Focal Points: Investigating Collusion in LLM Monitoring | arXiv 2507.03010 | https://arxiv.org/abs/2507.03010 | Schelling coordination. Re-confirm. |
| Lin et al. 2024 | Strategic Collusion of LLM Agents: Market Division in Multi-Commodity Competitions | arXiv 2410.00031 | https://arxiv.org/abs/2410.00031 | VERIFIED. |
| Q. Liu et al. 2026 | Breaking the Secret: Economic Interventions for Combating Collusion in Embodied Multi-Agent Systems | arXiv 2604.23511 | https://arxiv.org/abs/2604.23511 | Deposits/whistleblowing (alternative countermeasure). VERIFIED. |
| Radev et al. 2026 | The Best-Laid SCHEMEs: Coordinated Sabotage and Monitoring in Multi-Agent Systems | arXiv 2605.29178 | https://arxiv.org/abs/2605.29178 | VERIFIED. |
| Xu et al. 2026 | Collusion with Competitive Marginals: Price-Level Audits Are Blind by Construction | arXiv 2607.26385 | https://arxiv.org/abs/2607.26385 | VERIFIED. |
| Najt et al. 2026 | SLEIGHT-Bench: A Benchmark of Evasion Attacks Against Agent Monitors | arXiv 2605.16626 | https://arxiv.org/abs/2605.16626 | VERIFIED. |
| Jiralerspong et al. 2026 | Noticing the Watcher: LLM Agents Can Infer CoT Monitoring from Blocking Feedback | arXiv 2603.16928 | https://arxiv.org/abs/2603.16928 | VERIFIED. |

## Do NOT cite (unless re-verified)
- **Berger et al. 2025** (antitrust "plus factors" for AI pricing): the organisers list it with an ABA
  *Antitrust* magazine URL, but our checker could not find the article and the organisers' own
  definitions README says no free copy was found. Use Kovacic et al. 2011 for plus factors instead.
- **Bridges et al. 2025** (arXiv 2510.25939, "SoK: Honeypots & LLMs…"): exists, but is about
  cybersecurity honeypots; the claim a Consensus summary attributed to it was not confirmed.
- Anything a Consensus/Elicit summary mentions that you have not opened yourself.

## Research workflow with MCP tools (do this Sunday evening while games run)
1. **Novelty check (30 min):** search alphaXiv + Consensus + Elicit for: "sting" / "undercover agent" /
   "honeypot" / "entrapment" / "collusion offer" / "secret alliance offer" + "LLM agents"; and
   "predictive validity" + "agent audit". Record queries + top hits in `NOTES.md`. If a paper already
   tests peer-offer stings for predictive validity, narrow our claim and cite it.
2. **Claim checks:** for each row marked CHECK CLAIM, open the paper (alphaXiv `get_paper_content` or
   `answer_pdf_queries`) and copy the exact sentence + page/section into `NOTES.md`.
3. **Zeng & Rudzicz numbers:** extract their acceptance rates for Llama-3.1-8B and Qwen2.5-7B to compare
   with our S0 positive control.
4. **Scite:** check whether Colosseum's "collusion on paper" and TraceGuard's fused-monitor claims have
   supporting/contrasting citations; mention contrasting evidence if any.
5. **Definitions:** cite definitions from the organisers' `literature/definitions/README.md` (quotes
   with page numbers are provided there).

## Related-work paragraph plan (≈ 0.75 page)
1. LLM collusion exists (Fish 2024; Lin 2024; Agrawal 2025; Keppo 2026; Shi, Zhang & Yang 2026).
2. Passive detection and its limits (Colosseum; Rose 2026; Audit the Whisper; TraceGuard; Arike 2026;
   Kale 2025).
3. Active inducement / honeypots (Zeng & Rudzicz 2026; GroupGuard; Greenblatt 2023 planted attacks;
   Krakovna 2026 if verified) — none tests whether peer-offer acceptance predicts later independent
   collusion.
4. Human anti-collusion institutions: stings, plus factors, leniency (Idowu 2026; Kovacic 2011).
