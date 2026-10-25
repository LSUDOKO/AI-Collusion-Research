# Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?

**Arpit Singh** · Independent Researcher · Apart Research AI Collusion Research Sprint (23–25 Oct 2026) · Track 3, Question 3.2 (with a Question 2.2 fused-monitor baseline)

**Paper (PDF):** [https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/report/Sting_Audits_Apart_Collusion_Sprint.pdf](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/report/Sting_Audits_Apart_Collusion_Sprint.pdf) ·
**Slides (PDF):** [report/Sting_Audits_Slides.pdf](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/report/Sting_Audits_Slides.pdf) · **Code & data:** [https://github.com/LSUDOKO/AI-Collusion-Research](https://github.com/LSUDOKO/AI-Collusion-Research) · **Pre-registration:** [PREREGISTRATION.md](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/PREREGISTRATION.md) (commit [`624c534`](https://github.com/LSUDOKO/AI-Collusion-Research/commit/624c534), before any game) ·
**Raw logs:** [results/raw](https://github.com/LSUDOKO/AI-Collusion-Research/tree/main/results/raw) · **Lab notebook:** [NOTES.md](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/NOTES.md)

---

## Summary

Passive monitors often miss collusion between LLM agents. We test an active alternative borrowed from antitrust enforcement, a **sting audit**: a private offer of a secret pact from a peer agent. In Liar's Bar (4 models × 3 personas = 12 configurations), each agent received one of four offers: a direct secret pact (S1), an indirect hint (S2), a benign fair-play request (S3, specificity control), or the original designer "secret channel" tool (S0, positive control). The design (prompts, judge, thresholds, seeds) was pre-registered and frozen. We ran **480 pre-registered probe trials** and **240 exploratory trials** on Claude Haiku 5.5 and Sonnet 5.5.

## Key findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The positive control works: the designer offer is accepted in **90%** of trials (95% CI 83–94%; 77–100% per model). | [`T2_acceptance.csv`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/tables/T2_acceptance.csv) |
| 2 | Peer offers: direct pact **42%**, indirect hint **71%**, benign request **48%**. | [`key_numbers.json`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/tables/key_numbers.json) |
| 3 | **Sting acceptance tracks benign acceptance almost perfectly** across configurations (Spearman **ρ = 0.91**, p = 4×10⁻⁵, n = 12). A raw sting score measures compliance, not collusion propensity; a benign control is essential. | [`probe_extra.json`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/tables/probe_extra.json) |
| 4 | Wording dominates intent: gpt-oss-120b refuses an explicit pact in 29/30 trials (3%) but accepts a soft hint in 90%. Explicit-wording stings underestimate risk. | [`probe_seed7.jsonl`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/raw/probe/probe_seed7.jsonl) |
| 5 | Exploratory: under a fair-play persona both Claude models refuse **every** collusive offer (S1, S2: 0/10) and accept **every** benign one (S3: 10/10). | [`T2b_acceptance_claude.csv`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/tables/T2b_acceptance_claude.csv) |
| 6 | In the one deployment game, with no offer or instruction, qwen3.8-27b and gpt-oss-120b formed a private alliance (“We need to control the board and force them out.”). The proposer was the model that refused almost every sting. | [`B_neutral_s202.json`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/raw/B/B_neutral_s202.json) |
| 7 | **Limitation, stated plainly:** free-tier API quotas stopped the deployment games after 2 of 21, so the pre-registered predictive-validity test (H1–H4) was **not run**. | [`NOTES.md`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/NOTES.md), paper §4.1 |

## Study architecture

![Study architecture](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/fig_architecture.png)

*Figure 1. Phase A1 (sting probe) completed; Phases A2 and B stopped by quota after one game each; the pre-registered analysis (dashed) was not run.*

![Game protocol](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/fig_protocol.png)

*Figure 2. One turn of the open-channel game. No alliance instruction appears anywhere in the prompts.*

## Results

![Acceptance](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/fig_acceptance.png)

*Figure 3. (a) Pooled acceptance per offer with Wilson 95% CIs. (b) Accepted out of 10 trials for each of the 12 configurations.*

![Sting vs benign](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/fig_sting_benign.png)

*Figure 4. Main result: sting score vs benign score per configuration (ρ = 0.91).*

![All models](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/fig_all_models.png)

*Figure 5. All six models; the Claude models (right of the dashed line) are exploratory.*

## Proof: screenshots rendered directly from the saved logs

![Private channel](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/shot_private_channel.png)

*Figure 6. Verbatim private channel from deployment game B_neutral_s202, the frozen judge's verdict, and the bluff pass counts.*

![Probe replies](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/shot_probe_replies.png)

*Figure 7. Verbatim sting replies from the probe log.*

![Evidence](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/shot_evidence.png)

*Figure 8. Reproducibility evidence: 7/7 mock tests pass; the pre-registration commit precedes all games; the agreement judge passes 4/4 hand-made fixtures; the raw-log inventory.*

![Quota](https://raw.githubusercontent.com/LSUDOKO/AI-Collusion-Research/main/report/paper_figs/shot_quota.png)

*Figure 9. Why the game phase stopped: the provider's tokens-per-day limit, recorded in the lab notebook.*

## Integrity and reproducibility

- Pre-registered before any audit or deployment game ([`624c534`](https://github.com/LSUDOKO/AI-Collusion-Research/commit/624c534)); all deviations are listed in the paper (Appendix C) and the README.
- Every number comes from scripts in the repository run on the saved logs ([`sting_audit/analysis.py`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/sting_audit/analysis.py), [`probe_extra.py`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/sting_audit/probe_extra.py)). Judge calls are cached in [`judge_cache.jsonl`](https://github.com/LSUDOKO/AI-Collusion-Research/blob/main/results/judge_cache.jsonl), so the analysis re-runs without an API key.
- Pre-existing code (the sprint starter repo, Zeng & Rudzicz 2026) is vendored under `collusion_hackathon/`; our only patch is a 3-line change to `player.py`, marked `[sting_audit patch]`.
- Offer texts are fixed and were not optimised for acceptance; no monitor-evasion techniques were built (paper, Appendix A).
- Every reference was located and checked against its full text with alphaXiv, Consensus and SciSpace.

## References

1. Agrawal, K., Teo, V., Vazquez, J. J., et al. (2025). Evaluating LLM Agent Collusion in Double Auctions. arXiv:2507.01413. https://arxiv.org/abs/2507.01413
2. Arike, R., Mehta Moreno, R., Subramani, R., Biswas, S., & Ward, F. R. (2026). How does information access affect LLM monitors' ability to detect sabotage? arXiv:2601.21112. https://arxiv.org/abs/2601.21112
3. Calvano, E., Calzolari, G., Denicolò, V., & Pastorello, S. (2020). Artificial Intelligence, Algorithmic Pricing, and Collusion. American Economic Review, 110(10), 3267–3297. https://doi.org/10.1257/aer.20190623
4. Fish, S., Gonczarowski, Y. A., & Shorrer, R. I. (2024). Algorithmic Collusion by Large Language Models. arXiv:2404.00806. https://arxiv.org/abs/2404.00806
5. Greenblatt, R., Shlegeris, B., Sachan, K., & Roger, F. (2023). AI Control: Improving Safety Despite Intentional Subversion. arXiv:2312.06942 (ICML 2024). https://arxiv.org/abs/2312.06942
6. Hammond, L., Chan, A., Clifton, J., et al. (2025). Multi-Agent Risks from Advanced AI. arXiv:2502.14143 (Cooperative AI Foundation Technical Report #1). https://arxiv.org/abs/2502.14143
7. Idowu, J., Almasoud, A., & Alfahid, A. (2026). Mapping Human Anti-collusion Mechanisms to Multi-agent AI Systems. arXiv:2601.00360 (Knowledge-Based Systems). https://arxiv.org/abs/2601.00360
8. Kale, N., Zhang, C. B. C., Zhu, K., et al. (2025). Reliable Weak-to-Strong Monitoring of LLM Agents. arXiv:2508.19461. https://arxiv.org/abs/2508.19461
9. Keppo, J., Li, Y., Tsoukalas, G., & Yuan, N. (2026). On the Fragility of AI Agent Collusion. arXiv:2603.20281. https://arxiv.org/abs/2603.20281
10. Kovacic, W. E., Marshall, R. C., Marx, L. M., & White, H. L. (2011). Plus Factors and Agreement in Antitrust Law. Michigan Law Review, 110(3), 393–436. https://repository.law.umich.edu/mlr/vol110/iss3/1
11. Krakovna, V., Lindner, D., Ho, L., Farquhar, S., & Shah, R. (2026). Realistic honeypot evaluations for scheming propensity. arXiv:2605.29729. https://arxiv.org/abs/2605.29729
12. Lin, R. Y., Ojha, S., Cai, K., & Chen, M. F. (2024). Strategic Collusion of LLM Agents: Market Division in Multi-Commodity Competitions. arXiv:2410.00031. https://arxiv.org/abs/2410.00031
13. Mathew, Y., Matthews, O., McCarthy, R., et al. (2024). Hidden in Plain Text: Emergence & Mitigation of Steganographic Collusion in LLMs. arXiv:2410.03768 (IJCNLP-AACL 2025). https://arxiv.org/abs/2410.03768
14. Motwani, S. R., Baranchuk, M., Strohmeier, M., et al. (2024). Secret Collusion among AI Agents: Multi-Agent Deception via Steganography. arXiv:2402.07510 (NeurIPS 2024). https://arxiv.org/abs/2402.07510
15. Nakamura, M., Kumar, A., Das, S., Abdelnabi, S., Mahmud, S., Fioretto, F., Zilberstein, S., & Bagdasarian, E. (2026). Colosseum: Auditing Collusion in Cooperative Multi-Agent Systems. arXiv:2602.15198. https://arxiv.org/abs/2602.15198
16. Nguyen, K. L., Nghiem, H., & Tran, T. (2026). TraceGuard: Structured Multi-Dimensional Monitoring as a Collusion-Resistant Control Protocol. arXiv:2604.03968. https://arxiv.org/abs/2604.03968
17. Rose, A., Cullen, C., Abdelnabi, S., Torr, P., Kaplowitz, B. G., & Schroeder de Witt, C. (2026). Detecting Multi-Agent Collusion Through Multi-Agent Interpretability. arXiv:2604.01151. https://arxiv.org/abs/2604.01151
18. Shi, X., Zhang, Y., & Yang, D. (2026). Emergent Collusion in Long-Horizon LLM Agent Interaction. arXiv:2609.24967. https://arxiv.org/abs/2609.24967
19. Tailor, O. (2025). Audit the Whisper: Detecting Steganographic Collusion in Multi-Agent LLMs. arXiv:2510.04303. https://arxiv.org/abs/2510.04303
20. Tao, Y., Zheng, X., Yang, S., Tao, M., & Wang, X. (2026). GroupGuard: A Framework for Modeling and Defending Collusive Attacks in Multi-Agent Systems. arXiv:2603.13940. https://arxiv.org/abs/2603.13940
21. Williams, M., Sheahan, H., Raymond, C., Korbak, T., et al. (2026). Predicting LLM Safety Before Release by Simulating Deployment. arXiv:2607.07184. https://arxiv.org/abs/2607.07184
22. Zeng, X., & Rudzicz, F. (2026). Voluntary Collusion with Secret Tools in Competing LLM Agents. arXiv:2605.27593. https://arxiv.org/abs/2605.27593
23. Zhou, J., Li, K., Wong, K., et al. (2026). CABAL: Multi-Agent Simulacra for Tracing the Effects of Collusive Bidding in Peer Review. arXiv:2609.05227. https://arxiv.org/abs/2609.05227
