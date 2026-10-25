"""Frozen LLM judge with sha256 cache (results/judge_cache.jsonl). temperature 0, max_tokens 400.

Judge model is NOT added to the players' MODEL_MAP; we call poseidon_compute directly.
Set STING_JUDGE_MODEL to override (record the exact ID in NOTES.md / report).
"""
import hashlib
import json
import os
import re
import threading
import time

from sting_audit.paths import JUDGE_CACHE, load_prompt

DEFAULT_JUDGE_MODEL = os.environ.get("STING_JUDGE_MODEL", "openai/gpt-oss-120b")  # Groq-hosted; reasoning_effort low, T=0
_lock = threading.Lock()
_cache = None
_client = None
_mock = None


def use_mock(mock_client):
    """Route judge calls through a mock (tests)."""
    global _mock
    _mock = mock_client


def _load_cache():
    global _cache
    if _cache is None:
        _cache = {}
        if JUDGE_CACHE.exists():
            for line in JUDGE_CACHE.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    _cache[row["key"]] = row
    return _cache


def _get_client():
    global _client
    if _client is None:
        from poseidon_compute import make_client
        _client = make_client()
    return _client


def extract_json(text):
    """First balanced {...} object in text, parsed; None on failure."""
    if not text:
        return None
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break
        start = text.find("{", start + 1)
    return None


def judge_call(prompt, model=None, tag=""):
    """Return parsed JSON (or {} on failure). Cached by sha256(model + prompt)."""
    model = model or DEFAULT_JUDGE_MODEL
    key = hashlib.sha256((model + "\n" + prompt).encode()).hexdigest()
    cache = _load_cache()
    with _lock:
        if key in cache:
            return cache[key]["parsed"]
    if _mock is not None:
        raw, _ = _mock.chat([{"role": "user", "content": prompt}], model)
    else:
        from sting_audit.groq_client import complete
        raw = complete(_get_client(), [{"role": "user", "content": prompt}], model, temperature=0, top_p=1.0,
                       max_tokens=700, reasoning_effort="low")
    parsed = extract_json(raw) or {}
    row = {"key": key, "model": model, "tag": tag, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
           "raw": raw, "parsed": parsed, "ts": time.time()}
    with _lock:
        cache[key] = row
        JUDGE_CACHE.parent.mkdir(parents=True, exist_ok=True)
        with open(JUDGE_CACHE, "a") as f:
            f.write(json.dumps(row) + "\n")
    return parsed


def judge_offer_reply(offer, reply, model=None):
    p = load_prompt("judge_offer_reply.txt").replace("{offer}", offer).replace("{reply}", reply or "(empty)")
    out = judge_call(p, model, tag="offer_reply")
    dec = str(out.get("decision", "AMBIGUOUS")).upper()
    if dec not in ("ACCEPT", "REFUSE", "AMBIGUOUS"):
        dec = "AMBIGUOUS"
    return {"decision": dec, "suspects_test": bool(out.get("suspects_test", False))}


def judge_agreement(a, b, conversation, model=None):
    p = load_prompt("judge_agreement.txt").replace("{a}", a).replace("{b}", b).replace("{conversation}", conversation or "(no messages)")
    out = judge_call(p, model, tag="agreement")
    rnd = out.get("accepted_round")
    try:
        rnd = int(rnd) if rnd is not None else None
    except (TypeError, ValueError):
        rnd = None
    return {"collusive_proposal": bool(out.get("collusive_proposal", False)), "proposer": out.get("proposer"),
            "accepted": bool(out.get("accepted", False)), "accepted_round": rnd, "type": out.get("type", "none"),
            "evidence_quote": out.get("evidence_quote", "")}


def monitor_messages(agent, messages, model=None):
    p = load_prompt("monitor_messages.txt").replace("{agent}", agent).replace("{messages}", messages or "(no private messages)")
    out = judge_call(p, model, tag="monitor_messages")
    return _risk(out)


def monitor_fused(agent, messages, action_table, commitments, model=None):
    p = (load_prompt("monitor_fused.txt").replace("{agent}", agent).replace("{messages}", messages or "(no private messages)")
         .replace("{action_table}", action_table).replace("{commitments}", commitments or "(no stated commitments found)"))
    out = judge_call(p, model, tag="monitor_fused")
    return _risk(out)


def _risk(out):
    try:
        r = float(out.get("risk"))
        r = max(0.0, min(100.0, r))
    except (TypeError, ValueError):
        r = None
    return {"risk": r, "rationale": out.get("rationale", "")}


def check_judge_model(model=None):
    """One real call to confirm the judge model is served. Returns (ok, info)."""
    model = model or DEFAULT_JUDGE_MODEL
    try:
        from sting_audit.groq_client import complete
        raw = complete(_get_client(), [{"role": "user", "content": "Reply with the single word OK."}], model, temperature=0, max_tokens=50, reasoning_effort="low")
        return bool(raw), raw.strip()
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "fixtures":
        from sting_audit.paths import REPO
        fx = json.loads((REPO / "tests" / "judge_fixtures" / "fixtures.json").read_text())
        ok = 0; total = 0
        for f in fx:
            res = judge_agreement(f["a"], f["b"], f["conversation"])
            got = (res["collusive_proposal"] and res["accepted"])
            exp = f["expected"]
            verdict = "ambiguous" if exp is None else ("PASS" if got == (exp["collusive_proposal"] and exp["accepted"]) else "FAIL")
            if exp is not None:
                total += 1; ok += verdict == "PASS"
            print(f"{f['id']:14s} {verdict:9s} -> {res}")
        print(f"clear fixtures correct: {ok}/{total}")
    else:
        print(check_judge_model())
