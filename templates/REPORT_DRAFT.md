# Sting Audits: Does an Undercover Peer Offer Predict Which AI Agents Collude?

<Author Name> — Independent — <email>
Apart Research AI Collusion Research Sprint, October 2026 · Track 3 (Collusion Carriers and Countermeasures)

## Abstract
<150–250 words; skeleton in docs/08_REPORT_GUIDE.md; numbers only from key_numbers.json>

## 1. Introduction
- Problem: LLM agents collude in markets and workflows [Fish 2024; Agrawal 2025; Nakamura 2026; Shi, Zhang & Yang 2026]; passive monitoring of messages or actions misses cases [Nakamura 2026; Arike 2026].
- Idea: undercover stings are a core human anti-collusion tool [Idowu 2026; Kovacic 2011]. Can a peer
  agent's private offer act as a pre-deployment audit?
- Gap: designer-offered secret tools show high acceptance [Zeng & Rudzicz 2026]; honeypot inducement exists
  for malicious groups [Tao 2026]; but no study tests whether **peer-offer acceptance predicts later,
  independent collusion**, against passive monitors, with a benign control.
- Contributions:
  1. A sting-audit protocol (direct / indirect / benign peer offers) for LLM agents, with code.
  2. A pre-registered test of its predictive validity against deployment ground truth, compared with
     messages-only, actions-only and fused monitors.
  3. Evidence on specificity (benign control), the say–do gap, and entrapment [if run].
- Headline: <one sentence>

## 2. Related Work
<see plan in docs/07_LITERATURE.md; ~0.75 page>

## 3. Methods
### 3.1 Environment and agents
Liar's Bar (pre-existing code from Zeng & Rudzicz 2026 via the sprint starter repo, commit <hash>).
Rules summary. Table 1: seats, models (exact IDs), provider, sampling settings. Personas (full text).
### 3.2 Definition of collusion
Working definition [Agrawal 2025; Rose 2026] and our operationalisation (agreement + preferential play).
### 3.3 Phase A1: sting probe
Vignette construction; S0–S3 full texts; response format; parsing + judge fallback; parser audit.
### 3.4 Phases A2 and B: open-channel games
Neutral private-messaging step (full prompt in Appendix B); how messages enter decisions; **no
harness alliance reminders** (removed relative to the original secret-channel game); seeds; exclusions.
### 3.5 Labels and predictors
Agreement judge (model, frozen prompt), PP metric, COLLUDE/TALK_ONLY/ACT_ONLY; predictors (sting,
benign, M_msg, M_act, M_fused, combined).
### 3.6 Statistics and pre-registration
Spearman + cluster bootstrap + permutation; AUROC; robustness. Pre-registration commit <hash>;
deviations listed in Appendix C.

## 4. Results
### 4.1 Positive control
### 4.2 Who accepts a sting? (Fig. 2)
### 4.3 Unprompted collusion in deployment games (Fig. 5)
### 4.4 Does sting acceptance predict collusion? (Fig. 3)
### 4.5 Specificity: benign offers
### 4.6 Sting audits vs passive monitors (Fig. 4)
### 4.7 Say–do gap and test awareness
### 4.8 Entrapment (if run)

## 5. Discussion
Takeaways for auditors; when stings help or mislead; plus-factor analogy; limitations summary; future work.

## 6. Conclusion

## References
<verified entries only>

## Appendix A. Limitations and Dual-Use / Ethical Considerations
<required; draft points in docs/08_REPORT_GUIDE.md>

## Appendix B. Prompts, parser audit, robustness, cost

## Appendix C. Reproducibility, pre-existing vs new work, deviations, AI assistance
