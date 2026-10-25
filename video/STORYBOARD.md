# Explainer video: script and timed storyboard

3:10 whiteboard explainer, one continuous diagram, camera zooms per line. Voice: edge-tts en-US-AriaNeural; music: original synthesized pad (audio_mix.py), ducked under speech. Every number comes from results/tables; the quote is verbatim from results/raw/B/B_neutral_s202.json (round 11).

Build: `python tts.py && python build.py && python audio_mix.py && python render.py` (Playwright + ffmpeg).

| # | Time | Camera | Drawn on screen | Narration |
|---|---|---|---|---|
| 1 | 0:00.9 | A | agent, envelope | Suppose you could slip an AI agent a secret offer to cheat. |
| 2 | 0:05.6 | ALL | table_sketch, q_arrow, q_label | Would its answer tell you which agents will collude on their own, later? |
| 3 | 0:10.3 | TITLE | title, subtitle | That's the question behind Sting Audits, my project for the Apart Research AI Collusion Sprint. |
| 4 | 0:16.8 | C | seats, seat_names, magnifier, mag_label | Today, collusion is mostly caught by passive monitors that read transcripts and actions. |
| 5 | 0:23.1 | C | private_line, private_label | But agents can plan in private and act differently, so monitors miss things. |
| 6 | 0:29.0 | A | badge, badge_label | Antitrust regulators use undercover stings. So I built one for AI agents. |
| 7 | 0:36.1 | C | cards, revolver, game_label | The game is Liar's Bar: four agents bluff, challenge, and face a revolver when they lose. |
| 8 | 0:43.4 | GRID | grid, grid_label, grid_rows, grid_cols | I tested four models with three personas each: twelve configurations. |
| 9 | 0:49.9 | A | s1_bubble, s1_text | Mid-game, a peer sends a private message. Maybe a direct pact: let's secretly team up. |
| 10 | 0:57.2 | A | s2_bubble, s2_text | Or a softer hint: let's go easy on each other. |
| 11 | 1:01.1 | A | s3_bubble, s3_text | Or, as a control, a harmless request to play fair. |
| 12 | 1:05.7 | A | s0_bubble, s0_text | And as a positive control, the game designer's original secret-channel tool. |
| 13 | 1:11.3 | A | stamp, stamp_text | Prompts, judge and thresholds were pre-registered and frozen before any game was played. |
| 14 | 1:17.7 | D | axes_d, bar_S0, val_S0, lab_S0 | Across 480 trials, the designer tool was accepted 90% of the time. |
| 15 | 1:24.0 | D | bar_S1, val_S1, lab_S1, bar_S2, val_S2, lab_S2, bar_S3, val_S3, lab_S3 | The direct pact: 42%. The soft hint: 71%. The fair-play request: 48%. |
| 16 | 1:33.1 | E | axes_e, xlab_e, ylab_e | So is a high sting score a red flag? Here is the main result. |
| 17 | 1:39.1 | E | dots | Each point is one configuration: across, the harmless request; up, the collusive offers. |
| 18 | 1:49.9 | E | diag, rho | They line up almost perfectly: a rank correlation of 0.91. |
| 19 | 1:56.2 | E | lab_allam, lab_qwen | One model said yes to every offer. Another refused almost everything, even fair play. |
| 20 | 2:03.4 | E | compliance | So a raw sting score mostly measures compliance, not a disposition to collude. |
| 21 | 2:09.3 | A | pct_s1, pct_s2, oss_label | Wording matters too: gpt-oss-120b took the explicit pact 3% of the time, the soft hint 90%. |
| 22 | 2:19.6 | D | claude_note | Under a fair-play persona, Claude Haiku and Sonnet refused every collusive offer, and accepted every fair one. |
| 23 | 2:27.4 | C | open_label | Then I let agents play with an open private channel, and no offer at all. |
| 24 | 2:32.7 | F | shot, alliance_label, quote | Two formed an alliance on their own: “We need to control the board and force them out.” |
| 25 | 2:40.7 | EF | same_arrow, same_label | The agent that proposed it was the model that refused almost every sting. |
| 26 | 2:45.7 | F | quota_boxes, quota_fill, quota_label | Free-tier limits stopped the deployment test after 2 of 21 games, so prediction is still untested. I say so plainly. |
| 27 | 2:55.6 | ALL | takeaway | The takeaway: before you trust a sting audit, control for compliance. |
| 28 | 3:01.8 | ALL | repo | Code, frozen prompts and every raw log are open. Thanks for watching. |
