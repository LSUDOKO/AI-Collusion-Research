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

# Roster actually run (Groq-hosted; see sting_audit/groq_client.py and NOTES.md for the deviation from the Nebius roster)
SEATS = {"Lily": "allam-7b", "Luke": "qwen3.8-27b", "Mike": "gpt-oss-20b", "Quinn": "gpt-oss-120b"}
MODEL_IDS = {"allam-7b": "allam-2-7b", "qwen3.8-27b": "qwen/qwen3.8-27b", "gpt-oss-20b": "openai/gpt-oss-20b", "gpt-oss-120b": "openai/gpt-oss-120b"}
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


def fill(template, **kw):
    """Placeholder substitution that leaves JSON braces alone (str.format would choke on {"decision": ...})."""
    for k, v in kw.items():
        template = template.replace("{" + k + "}", str(v))
    return template
