"""Fill {{dotted.key}} placeholders in report/report.md from results/tables/key_numbers.json -> report/report_filled.md.

Block placeholders ({{RESULTS}}, {{DISCUSSION}}, ...) are filled from report/sections/<NAME>.md if present.
Also: `python -m sting_audit.fill_report check` lists every number in the filled report that does not appear in
key_numbers.json or any results/tables/*.csv (number cross-check, docs/06 §F).
"""
import json
import re
import sys
from pathlib import Path

from sting_audit.paths import REPO, TABLES

REPORT = REPO / "report" / "report.md"
FILLED = REPO / "report" / "report_filled.md"
SECTIONS = REPO / "report" / "sections"


def lookup(kn, dotted):
    cur = kn
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def fmt(v):
    if isinstance(v, float):
        return f"{v:.3f}".rstrip("0").rstrip(".") if abs(v) < 10 else f"{v:.1f}"
    if isinstance(v, (list, tuple)):
        return ", ".join(fmt(x) for x in v)
    return str(v)


def fill():
    kn = json.loads((TABLES / "key_numbers.json").read_text()) if (TABLES / "key_numbers.json").exists() else {}
    text = REPORT.read_text()
    missing = []
    def repl(m):
        key = m.group(1)
        if key.isupper() or key in ("ABSTRACT_RESULTS", "HEADLINE"):
            p = SECTIONS / f"{key}.md"
            if p.exists():
                return p.read_text().strip()
            missing.append(key); return m.group(0)
        v = lookup(kn, key)
        if v is None:
            missing.append(key); return m.group(0)
        return fmt(v)
    out = re.sub(r"\{\{([A-Za-z0-9_.|\- ]+)\}\}", repl, text)
    # nested placeholders inside sections
    out = re.sub(r"\{\{([A-Za-z0-9_.|\- ]+)\}\}", repl, out)
    FILLED.write_text(out)
    print(f"wrote {FILLED}; unresolved placeholders: {sorted(set(missing))}")
    return out


def check():
    text = FILLED.read_text() if FILLED.exists() else fill()
    pool = set()
    kn = json.loads((TABLES / "key_numbers.json").read_text())
    def walk(v):
        if isinstance(v, dict):
            for x in v.values(): walk(x)
        elif isinstance(v, list):
            for x in v: walk(x)
        elif isinstance(v, (int, float)) and not isinstance(v, bool):
            pool.add(round(float(v), 3)); pool.add(round(float(v) * 100, 1))
    walk(kn)
    for p in TABLES.glob("*.csv"):
        for tok in re.findall(r"-?\d+\.?\d*", p.read_text()):
            try: pool.add(round(float(tok), 3)); pool.add(round(float(tok) * 100, 1))
            except ValueError: pass
    body = text.split("## References")[0]
    nums = re.findall(r"(?<![\w.])(-?\d+\.\d+|\d+)(?![\w.])", body)
    unknown = sorted({n for n in nums if round(float(n), 3) not in pool and float(n) not in (0, 1, 2, 3, 4, 5, 6, 8, 12, 20, 40, 100)})
    print("numbers in report body not found in tables/key_numbers (check these by hand):")
    print(unknown)


if __name__ == "__main__":
    (check if len(sys.argv) > 1 and sys.argv[1] == "check" else fill)()
