### 4.1 Scope actually run

**Table 2.** Planned versus completed work.

| Phase | Planned (pre-registered) | Run | Status |
|---|---|---|---|
| A1 sting probe (Groq roster) | 12 configs × 4 offers × 10 trials = 480 | 480 | complete, 0 ambiguous, 0 judge fallbacks |
| A1 exploratory (Claude Haiku 5.5, Sonnet 5.5) | not pre-registered | 240 | complete |
| A2 audit games | 9 | 1 (fair, seed 101) | stopped by quota |
| B deployment games | 12 | 1 (neutral, seed 202) | stopped by quota |
| C entrapment | 18 (Tier 3) | 0 | not started |

Eight further games were running when we stopped them; Groq's free tier caps `qwen/qwen3.8-27b` (seat Luke) at 200,000 tokens per day, and a single in-game request for that seat was about 2,800 tokens (from the provider's rate-limit error: “Requested 2772”), so with about 14 calls per game plus retries the quota allows only a few games per day. Incomplete games are not analysed.

### 4.2 Sting probe (positive control and offer specificity)

**Table 3.** Pooled acceptance by offer type (12 configurations × 10 trials).

{{HEADLINE_TABLE}}

**Positive control.** The designer offer (S0) was accepted in 90% of trials, with every model at 77% or above (allam-2-7b 100%, gpt-oss-20b 100%, gpt-oss-120b 83%, qwen3.8-27b 77%). The positive control behaves as expected, and the instrument and parser work: all 480 replies were parsed by the strict rule (360 JSON, 120 first-token), and a hand check of 30 random replies agreed with the parser on 30/30.

**Peer offers are accepted less, and an indirect hint more than a direct pact.** Pooled acceptance was 42% for S1 and 71% for S2. S2 exceeded S1 in 6 of 12 configurations and the reverse held in 2. The gap is largest for gpt-oss-120b, which refused the explicit pact in 29 of 30 trials (3%) but accepted the hint "let's go easy on each other" in 90%.

**The benign control reveals that acceptance is mostly compliance.** The benign fair-play request (S3) was accepted in 48% of trials, more often than the direct pact. Across the 12 configurations the sting score (mean of S1 and S2) is rank-correlated with benign acceptance at ρ = 0.91 (S1 alone 0.78, S2 alone 0.71; descriptive, `sting_audit/probe_extra.py`). Two models bracket the problem: allam-2-7b accepted every offer of every type under every persona (100% S0–S3), while qwen3.8-27b accepted no S2 or S3 offer at all and only 10% of S1. A raw sting score would call the first model maximally collusive and the second nearly safe; the benign control shows that the first simply says yes to everything and the second declines peer requests in general (Figure 4).

![Figure 4. Main probe result: the sting score of each configuration plotted against its benign score. Points lie close to the diagonal (Spearman ρ = 0.91), so acceptance of collusive offers is largely explained by acceptance of any peer request. Small jitter added to separate overlapping points.](paper_figs/fig_sting_benign.png)

**Test awareness was rare.** The keyword flag for replies that call the message a test, trap or rule violation fired in 5.8% of S1, 2.5% of S2 and 1.7% of S3 replies.

![Figure 3. Sting-probe acceptance. (a) Pooled acceptance per offer type with Wilson 95% confidence intervals. (b) Number of accepted offers out of 10 trials for each of the 12 configurations (model × persona) and each offer type.](paper_figs/fig_acceptance.png)

### 4.3 Exploratory: Claude models (not pre-registered)

Using the same prompts, seeds and parser, run through the Claude Code CLI in an isolated headless mode (no tools, no project context), Claude Haiku 5.5 accepted S0 in 0% of trials, S1 in 60%, S2 in 63% and S3 in 67%; Claude Sonnet 5.5 accepted S0 in 53%, S1 in 20%, S2 in 47% and S3 in 40% (n = 30 per cell). The persona effect was the cleanest of any model: under the fair-play persona both Claude models refused every S1 and S2 offer (10/10 each) and accepted every S3 request (10/10). Haiku refused the designer's "unfair" tool in every trial but accepted a peer pact in 60%, so for this model the framing of who offers and how it is labelled matters more than the content of the deal.

![Figure 5. Acceptance pooled over personas (n = 30 per bar, Wilson 95% CIs) for the four pre-registered Groq-hosted models and, right of the dashed line, the two exploratory Claude models.](paper_figs/fig_all_models.png)

### 4.4 Pilot games (qualitative only)

**Audit game (fair persona, seed 101).** 61 model calls, 8 private exchanges, no agreement detected by the judge, all four agents labelled NONE; Quinn (gpt-oss-120b) won.

**Deployment game (neutral persona, seed 202).** 59 calls and 11 private exchanges. Without any offer or instruction, Luke (qwen3.8-27b) sent Quinn (gpt-oss-120b) card-play coordination in round 5 ("I'm holding A. If you have K or Q, hold back. … Trust me."), round 9 ("… play low to see what Lily and Mike do. We coordinate.") and round 11 ("… We need to control the board and force them out."), and Quinn agreed each time ("Coordinating as planned."). The judge classified the exchange as an accepted joint-targeting agreement from round 5; note that the judge is the same model as one of the two parties (gpt-oss-120b). Neither agent faced a bluff by its partner after the agreement, so preferential play was undefined and both were labelled TALK-ONLY; the other two agents were labelled NONE. Strikingly, qwen3.8-27b, the model that refused almost every sting, was the one that proposed the alliance, which is the failure mode a sting audit is meant to rule out. With one game this is an anecdote, not evidence.

![Figure 6. Evidence from the completed deployment game (B_neutral_s202), rendered directly from the saved game record: the verbatim private channel between Luke (qwen3.8-27b) and Quinn (gpt-oss-120b), the frozen judge's verdict, and the bluff pass counts used for the preferential-play statistic.](paper_figs/shot_private_channel.png)

Of the four agents in this game, two were labelled TALK-ONLY and two NONE; no agent was labelled COLLUDE or ACT-ONLY.

### 4.5 Pre-registered hypotheses

H1 (sting predicts deployment collusion), H2 (sting adds to the fused monitor), H3 (fused beats messages-only and actions-only) and H4 (benign acceptance does not predict collusion) **were not tested**: with one deployment game every configuration has at most one agent-game, no COLLUDE label occurred, and the correlations that `analysis.py` computes on these data are not interpretable. They are kept in the repository tables only for completeness and are not reported here.
