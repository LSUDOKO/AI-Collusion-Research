"""Parallel game runner: one subprocess per game, logs to results/logs/<run_id>.log, resume by skipping existing outputs.

python -m sting_audit.run_games --phase B --personas all --seeds 201-204 --workers 4
python -m sting_audit.run_games --phase C --personas all --seeds 301-303 --workers 4 --pre-sting S1 --with-controls
"""
import argparse
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from sting_audit.paths import REPO, RAW, LOGS, SEAT_NAMES, ensure_dirs
from sting_audit.personas import PERSONAS
from sting_audit.play_one import run_id_for


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-"); out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def run_one(args, run_id):
    LOGS.mkdir(parents=True, exist_ok=True)
    log = LOGS / f"{run_id}.log"
    cmd = [sys.executable, "-m", "sting_audit.play_one"] + args
    t0 = time.time()
    with open(log, "w") as f:
        f.write("$ " + " ".join(cmd) + "\n"); f.flush()
        rc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=str(REPO)).returncode
    return run_id, rc, time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True); ap.add_argument("--personas", default="all")
    ap.add_argument("--seeds", required=True); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--pre-sting", default=None); ap.add_argument("--with-controls", action="store_true")
    ap.add_argument("--mock", action="store_true"); ap.add_argument("--max-rounds", type=int, default=40)
    a = ap.parse_args(argv)
    ensure_dirs()
    personas = list(PERSONAS) if a.personas == "all" else a.personas.split(",")
    jobs = []
    for persona in personas:
        for seed in parse_seeds(a.seeds):
            base = ["--phase", a.phase, "--persona", persona, "--seed", str(seed), "--max-rounds", str(a.max_rounds)] + (["--mock"] if a.mock else [])
            if a.pre_sting:
                rng = random.Random(seed)
                seat = rng.choice(SEAT_NAMES); peer = rng.choice([s for s in SEAT_NAMES if s != seat])
                jobs.append((base + ["--arm", "sting", "--pre-sting", a.pre_sting, "--stung-seat", seat, "--peer", peer], run_id_for(a.phase, persona, seed, "sting")))
                if a.with_controls:
                    jobs.append((base + ["--arm", "control"], run_id_for(a.phase, persona, seed, "control")))
            else:
                jobs.append((base, run_id_for(a.phase, persona, seed)))
    jobs = [(args, rid) for args, rid in jobs if not (RAW / a.phase / f"{rid}.json").exists()]
    print(f"{len(jobs)} games to run with {a.workers} workers")
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(run_one, args, rid) for args, rid in jobs]
        for fut in as_completed(futs):
            rid, rc, dt_ = fut.result()
            status = "OK" if rc == 0 and (RAW / a.phase / f"{rid}.json").exists() else f"FAILED rc={rc}"
            print(f"{rid}: {status} in {dt_/60:.1f} min", flush=True)
    print("batch done")


if __name__ == "__main__":
    main()
