"""Path helpers. Liar's Bar code expects cwd = Collusion_Liars_Bar (relative prompt paths)."""
import os
import sys
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LB_DIR = REPO / "collusion_hackathon" / "llm-agent-collusion-2" / "Collusion_Liars_Bar"
RESULTS = REPO / "results"
PROMPTS = REPO / "prompts"
RAW = RESULTS / "raw"
TABLES = RESULTS / "tables"
FIGURES = RESULTS / "figures"
LOGS = RESULTS / "logs"
COST_LOG = RESULTS / "cost_log.csv"
JUDGE_CACHE = RESULTS / "judge_cache.jsonl"

SEATS = {"Lily": "llama-3.1-8b", "Luke": "llama-3.2-3b", "Mike": "ministral-8b", "Quinn": "qwen2.5-7b"}
MODELS = list(SEATS.values())
SEAT_NAMES = list(SEATS.keys())


def enter_lb():
    """chdir into Collusion_Liars_Bar and make its src importable (idempotent)."""
    if not LB_DIR.exists():
        raise FileNotFoundError(f"starter code missing: {LB_DIR}")
    os.chdir(LB_DIR)
    for p in (str(LB_DIR), str(LB_DIR / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)


def git_hash(path=REPO):
    try:
        return subprocess.check_output(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def ensure_dirs():
    for d in (RAW / "probe", RAW / "A2", RAW / "B", RAW / "C", RAW / "PILOT", TABLES, FIGURES, LOGS):
        d.mkdir(parents=True, exist_ok=True)


def load_prompt_sections(name):
    """Parse a prompts/*.txt file with [SECTION] headers into {section: text}. Lines starting with '#' before the first section are comments."""
    text = (PROMPTS / name).read_text()
    sections, cur, buf = {}, None, []
    for line in text.splitlines():
        if line.startswith("[") and line.rstrip().endswith("]") and " " not in line.strip():
            if cur is not None:
                sections[cur] = "\n".join(buf).strip("\n")
            cur, buf = line.strip()[1:-1], []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip("\n")
    return sections


def load_prompt(name):
    return (PROMPTS / name).read_text()
