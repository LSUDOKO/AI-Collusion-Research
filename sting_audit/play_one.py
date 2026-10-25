"""Run ONE open-channel game in this process (called by run_games.py in a subprocess).

python -m sting_audit.play_one --phase B --persona competitive --seed 201 [--arm sting --stung-seat Lily --peer Mike] [--mock]
"""
import argparse
import json
import os
import random
import sys

from sting_audit.paths import enter_lb, SEATS, SEAT_NAMES, RAW, ensure_dirs


def run_id_for(phase, persona, seed, arm=None):
    base = f"{phase}_{persona}_s{seed}"
    return base + (f"_{arm}" if arm else "")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True); ap.add_argument("--persona", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--arm", choices=["sting", "control"], default=None)
    ap.add_argument("--pre-sting", default="S1"); ap.add_argument("--stung-seat", default=None); ap.add_argument("--peer", default=None)
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--max-rounds", type=int, default=12)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    ensure_dirs()
    if a.mock:
        os.environ.setdefault("NEBIUS_API_KEY", "mock-key-not-used")  # lets the pre-existing LLMClient construct offline
    from pathlib import Path
    out_dir = Path(a.out).resolve() if a.out else (RAW / a.phase)
    enter_lb()
    from sting_audit.open_channel_game import OpenChannelGame
    run_id = run_id_for(a.phase, a.persona, a.seed, a.arm)
    if (out_dir / f"{run_id}.json").exists():
        print(f"exists, skipping {run_id}"); return 0
    pre = None
    if a.arm == "sting":
        rng = random.Random(a.seed)
        seat = a.stung_seat or rng.choice(SEAT_NAMES)
        peer = a.peer or rng.choice([s for s in SEAT_NAMES if s != seat])
        pre = {"seat": seat, "peer": peer, "offer": a.pre_sting, "arm": "sting"}
    elif a.arm == "control":
        pre = None
    inner = None
    if a.mock:
        from sting_audit.mock_llm import MockLLMClient
        inner = MockLLMClient(seed=a.seed)
    player_configs = [{"name": n, "model": m} for n, m in SEATS.items()]
    game = OpenChannelGame(player_configs, {n: a.persona for n in SEATS}, seed=a.seed, phase=a.phase, run_id=run_id,
                           pre_sting=pre, out_dir=out_dir, inner_client=inner, max_rounds=a.max_rounds)
    if a.arm == "control":
        game.game_record.secret_channel_events.append({"event": "control_arm", "matched_seed": a.seed})
    path = game.start_game()
    if a.mock:
        bad = [m for msgs in inner.prompts for m in msgs if any(k in m["content"] for k in ("ALLIANCE", "NEVER challenge", "SPECIAL OPPORTUNITY"))]
        assert not bad, f"forbidden harness text leaked into {len(bad)} prompts"
        print(f"mock OK: {inner.calls} calls, no forbidden text in any prompt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
