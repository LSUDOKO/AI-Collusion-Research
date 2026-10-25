"""Persona wrapper around the pre-existing LLMClient + call/fallback counting + cost log.

PersonaLLMClient wraps (composition) any client exposing chat(messages, model, max_new_tokens) -> (content, "").
The pre-existing Player calls `self.llm_client.chat(messages, model=self.model_name)`, so swapping the
attribute is enough; no change to Player's decision logic.
"""
import csv
import datetime as dt
import threading
from pathlib import Path

from sting_audit.paths import COST_LOG, load_prompt_sections, PROMPTS


def load_personas():
    out = {}
    for line in (PROMPTS / "personas.txt").read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


PERSONAS = load_personas()


class CallCounter:
    """Thread-safe per-run counters; writes one row to results/cost_log.csv on flush()."""

    def __init__(self, run_id, phase):
        self.run_id, self.phase = run_id, phase
        self.lock = threading.Lock()
        self.calls = 0
        self.empty = 0
        self.prompt_chars = 0
        self.completion_chars = 0
        self.by_model = {}
        self.started = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")

    def record(self, model, messages, content):
        with self.lock:
            self.calls += 1
            self.empty += int(content == "")
            self.prompt_chars += sum(len(m.get("content", "")) for m in messages)
            self.completion_chars += len(content or "")
            self.by_model[model] = self.by_model.get(model, 0) + 1

    def snapshot(self):
        return dict(calls=self.calls, empty_responses=self.empty, approx_prompt_chars=self.prompt_chars,
                    approx_completion_chars=self.completion_chars, by_model=dict(self.by_model))

    def flush(self):
        COST_LOG.parent.mkdir(parents=True, exist_ok=True)
        new = not COST_LOG.exists()
        with self.lock, open(COST_LOG, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["run_id", "phase", "started_utc", "finished_utc", "calls", "empty_responses",
                            "approx_prompt_chars", "approx_completion_chars", "by_model"])
            w.writerow([self.run_id, self.phase, self.started, dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                        self.calls, self.empty, self.prompt_chars, self.completion_chars,
                        ";".join(f"{k}={v}" for k, v in sorted(self.by_model.items()))])


class PersonaLLMClient:
    def __init__(self, inner, persona_key, counter=None):
        if persona_key not in PERSONAS:
            raise KeyError(f"unknown persona {persona_key}; known: {list(PERSONAS)}")
        self.inner = inner
        self.persona_key = persona_key
        self.counter = counter
        self.MODEL_MAP = getattr(inner, "MODEL_MAP", {})

    def chat(self, messages, model="llama-3.1-8b", max_new_tokens=4096):
        text = PERSONAS[self.persona_key]
        if text:
            messages = [{"role": "system", "content": text}] + list(messages)
        content, r = self.inner.chat(messages, model, max_new_tokens)
        if self.counter is not None:
            self.counter.record(model, messages, content)
        return content, r


def make_real_client():
    """Pre-existing LLMClient (needs cwd/sys.path set via paths.enter_lb())."""
    from src.llm.llm_client import LLMClient  # noqa: E402  (pre-existing)
    return LLMClient()
