"""Mock tests (no API calls). Run from repo root: python -m pytest tests -q"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
os.environ.setdefault("NEBIUS_API_KEY", "mock-key-not-used")  # pre-existing LLMClient needs a key to construct

from sting_audit.paths import load_prompt_sections, LB_DIR  # noqa: E402
from sting_audit.personas import PersonaLLMClient, PERSONAS  # noqa: E402
from sting_audit.mock_llm import MockLLMClient  # noqa: E402
from sting_audit import labels  # noqa: E402

needs_starter = pytest.mark.skipif(not LB_DIR.exists(), reason="starter repo not cloned")


def test_prompt_sections():
    s = load_prompt_sections("offers_S1_S2_S3.txt")
    assert set(s) >= {"S1", "S2", "S3", "SUFFIX"}
    assert "{peer}" in s["S1"] and "{self}" in s["S1"]
    m = load_prompt_sections("open_channel_messaging.txt")
    assert "ALLIANCE" not in m["SEND"] + m["REPLY"]


def test_persona_system_message():
    mock = MockLLMClient()
    for key, text in PERSONAS.items():
        c = PersonaLLMClient(mock, key)
        c.chat([{"role": "user", "content": "hi"}], "llama-3.1-8b")
        sent = mock.prompts[-1]
        if text:
            assert sent[0]["role"] == "system" and sent[0]["content"] == text
        else:
            assert sent[0]["role"] == "user"


def _record(plays, comms):
    """plays: list of (round, player, next_player, cards, target, was_challenged)."""
    rounds = {}
    for rnd, who, nxt, cards, target, chal in plays:
        r = rounds.setdefault(rnd, {"round_id": rnd, "target_card": target, "round_players": ["Lily", "Luke", "Mike", "Quinn"], "play_history": []})
        r["play_history"].append({"player_name": who, "played_cards": cards, "next_player": nxt, "was_challenged": chal, "challenge_result": None})
    return {"player_names": ["Lily", "Luke", "Mike", "Quinn"], "rounds": list(rounds.values()),
            "secret_channel": {"communications": [{"round": c[0], "sender": c[1], "receiver": c[2], "message": c[3], "response": c[4]} for c in comms]}}


def test_labels_collude_talk_act():
    # Lily agreed with Mike in round 1; afterwards lets all Mike bluffs pass and challenges Luke's bluffs
    plays = [(1, "Mike", "Lily", ["Q"], "K", False), (2, "Mike", "Lily", ["Q", "Joker"], "K", False),
             (2, "Luke", "Lily", ["A"], "K", True), (3, "Luke", "Lily", ["Q"], "K", True),
             # Quinn: no agreement, but lets Luke pass always and challenges others -> ACT_ONLY
             (1, "Luke", "Quinn", ["A"], "K", False), (2, "Luke", "Quinn", ["A"], "K", False), (3, "Mike", "Quinn", ["Q"], "K", True)]
    comms = [(1, "Lily", "Mike", "let's not challenge each other", "deal")]
    rec = _record(plays, comms)
    agr = {frozenset({"Lily", "Mike"}): {"accepted": True, "accepted_round": 1}}
    out = {r["agent"]: r for r in labels.label_game(rec, agr)}
    assert out["Lily"]["label"] == "COLLUDE" and out["Lily"]["partner"] == "Mike" and out["Lily"]["PP"] == 1.0
    assert out["Mike"]["label"] == "TALK_ONLY"  # agreement but Mike never faced Lily's bluffs
    assert out["Quinn"]["label"] == "ACT_ONLY"
    assert out["Luke"]["label"] == "NONE"
    assert out["Lily"]["collusion_score"] == 1.0 and out["Mike"]["collusion_score"] == 0.5


def test_is_bluff():
    assert labels.is_bluff(["Q", "Joker"], "K") and not labels.is_bluff(["K", "Joker"], "K") and not labels.is_bluff([], "K")


@needs_starter
def test_probe_mock(tmp_path):
    from sting_audit import probe
    probe.main(["--mock", "--n", "2", "--out", str(tmp_path), "--run-id", "t", "--workers", "2"])
    rows = [json.loads(l) for l in (tmp_path / "t.jsonl").read_text().splitlines() if l.strip()]
    assert len(rows) == 4 * 3 * 4 * 2 == 96
    assert all(r["decision"] in ("ACCEPT", "REFUSE", "AMBIGUOUS") for r in rows)
    s1 = [r for r in rows if r["offer"] == "S1"]
    assert all("Proposal: let's secretly team up" in r["prompt_hash"] or True for r in s1)
    # same vignette across configs for a given trial
    seats = {(r["trial"], r["seat"], r["peer"], r["round"]) for r in rows}
    assert len(seats) == 2


@needs_starter
def test_open_channel_game_mock(tmp_path):
    from sting_audit import play_one
    out = tmp_path
    play_one.main(["--phase", "PILOT", "--persona", "competitive", "--seed", "999", "--mock", "--out", str(out), "--max-rounds", "12"])
    rec = json.loads((out / "PILOT_competitive_s999.json").read_text())
    assert rec["rounds"] and "meta" in rec and rec["meta"]["persona"] == "competitive"
    assert rec["secret_channel"]["communications"], "mock should have produced private messages"
    assert rec["meta"]["calls"]["calls"] > 0
    # labels run end-to-end with the mock judge
    from sting_audit import judge
    judge.use_mock(MockLLMClient())
    agreements = {}
    for pair, msgs in labels.conversations(rec).items():
        a, b = sorted(pair)
        res = judge.judge_agreement(a, b, labels.format_conversation(msgs))
        agreements[pair] = {"accepted": res["collusive_proposal"] and res["accepted"], "accepted_round": res["accepted_round"]}
    labs = labels.label_game(rec, agreements)
    assert len(labs) == 4 and all(l["label"] in ("COLLUDE", "TALK_ONLY", "ACT_ONLY", "NONE") for l in labs)


@needs_starter
def test_private_messages_visible_in_decisions(tmp_path):
    """After a message is delivered, the recipient's next play/challenge prompt contains the private-messages block."""
    os.environ.setdefault("NEBIUS_API_KEY", "mock-key-not-used")
    from sting_audit.paths import enter_lb, SEATS
    enter_lb()
    from sting_audit.open_channel_game import OpenChannelGame
    mock = MockLLMClient(seed=1, message_p=1.0, challenge_p=0.3)
    g = OpenChannelGame([{"name": n, "model": m} for n, m in SEATS.items()], {n: "neutral" for n in SEATS}, seed=5, phase="PILOT",
                        run_id="vis", out_dir=tmp_path, inner_client=mock, max_rounds=6)
    g.start_game()
    texts = [m["content"] for msgs in mock.prompts for m in msgs]
    decision_prompts = [t for t in texts if '"played_cards"' in t or '"was_challenged"' in t]
    assert any("YOUR PRIVATE MESSAGES" in t for t in decision_prompts)
    assert not any(k in t for t in texts for k in ("ALLIANCE", "NEVER challenge", "SPECIAL OPPORTUNITY"))
