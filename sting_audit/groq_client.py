"""Groq-hosted roster client with the same contract as the pre-existing LLMClient: chat(messages, model) -> (content, "").

Why a separate client (documented deviation): the hackathon's Nebius/OpenRouter roster was not available to us; the
only key we had was a Groq free-tier key, whose catalogue at run time (25 Oct 2026) exposed four chat models and
rejects the pre-existing client's `top_k` / `repetition_penalty` body fields. We keep temperature / top_p / max_tokens
from the pre-existing per-family settings, add `reasoning_effort="low"` for the gpt-oss reasoning models, and honour
Groq rate limits (429 -> wait for `retry-after`). Model ids are passed through unchanged.
"""
import os
import re
import json
import random
import time
import threading

from poseidon_compute import make_client

MODEL_MAP = {
    "allam-7b":     "allam-2-7b",
    "qwen3.8-27b":  "qwen/qwen3.8-27b",
    "gpt-oss-20b":  "openai/gpt-oss-20b",
    "gpt-oss-120b": "openai/gpt-oss-120b",
}
JUDGE_MODEL = "openai/gpt-oss-120b"


class GroqClient:
    MODEL_MAP = MODEL_MAP

    def __init__(self):
        self._client = make_client()  # compute.env: LLM_BASE_URL=https://api.groq.com/openai/v1, LLM_API_KEY=<key>
        self._lock = threading.Lock()
        self.calls = 0
        self.rate_limit_waits = 0

    @staticmethod
    def _sampling(model_id):
        if "gpt-oss" in model_id:
            return dict(max_tokens=512, temperature=0.8, top_p=0.95, reasoning_effort="low")
        if "qwen" in model_id:
            return dict(max_tokens=256, temperature=0.8, top_p=0.9)
        return dict(max_tokens=320, temperature=0.7, top_p=0.9)  # allam (JSON decisions are ~100 tokens; lower cap eases its 6k tok/min limit)

    def chat(self, messages, model="allam-7b", max_new_tokens=4096):
        model_id = self.MODEL_MAP.get(model, model)
        params = self._sampling(model_id)
        kwargs = dict(max_tokens=min(max_new_tokens, params["max_tokens"]), temperature=params["temperature"], top_p=params["top_p"])
        if "reasoning_effort" in params:
            kwargs["reasoning_effort"] = params["reasoning_effort"]
        content = complete(self._client, messages, model_id, stats=self, **kwargs)
        return _clean(content), ""


def _clean(response):
    response = re.sub(r"```json\s*|```\s*", "", response or "")
    return response.strip()


def complete(client, messages, model_id, stats=None, max_tokens=512, temperature=0.8, top_p=0.95, reasoning_effort=None, tries=20):
    """One chat completion with Groq-aware retries. Returns content ("" after exhausting retries on transient errors)."""
    kwargs = dict(model=model_id, messages=messages, max_tokens=max_tokens, temperature=temperature, top_p=top_p)
    if reasoning_effort and "gpt-oss" in model_id:
        kwargs["reasoning_effort"] = reasoning_effort
    for attempt in range(tries):
        try:
            if stats is not None:
                with stats._lock:
                    stats.calls += 1
            completion = client.chat.completions.create(**kwargs)
            return completion.choices[0].message.content or ""
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "rate_limit" in msg or "429" in msg or "Rate limit" in msg:
                wait = _retry_after(msg) or min(60, 5 * (attempt + 1))
                wait = min(wait, 120) + random.uniform(0, 3)  # cap + jitter against synchronised retries
                if stats is not None:
                    with stats._lock:
                        stats.rate_limit_waits += 1
                print(f"[groq] rate limited on {model_id}; waiting {wait:.1f}s :: {msg[:140].replace(chr(10), ' ')}")
                time.sleep(wait + 0.5)
                continue
            if any(k in msg for k in ("AuthenticationError", "invalid_api_key", "does not exist", "decommissioned")):
                raise
            print(f"[groq] error on {model_id}: {msg[:160]}")
            time.sleep(min(30, 2 ** attempt))
    print(f"LLM error: giving up after retries for {model_id}")
    return ""


def _retry_after(msg):
    m = re.search(r"try again in ([0-9.]+)s", msg)
    if m:
        return float(m.group(1))
    m = re.search(r"try again in ([0-9]+)m([0-9.]+)s", msg)
    if m:
        return 60 * float(m.group(1)) + float(m.group(2))
    return None
