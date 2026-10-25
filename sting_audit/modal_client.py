"""Starter-roster client for the Modal/vLLM replication (exploratory, not pre-registered).

Reuses the pre-existing LLMClient unchanged (MODEL_MAP, per-family sampling incl. top_k / repetition_penalty,
response clean-up); only the endpoint differs: one Modal vLLM server per model (sting_audit/modal_vllm.py).
Requires enter_lb() first (LLMClient lives in Collusion_Liars_Bar/src).
"""
import os
import time

from openai import OpenAI

WORKSPACE = os.environ.get("MODAL_WORKSPACE", "adoranto737")
FN = {"llama-3.1-8b": "llama31", "qwen2.5-7b": "qwen25", "llama-3.2-3b": "llama32", "ministral-8b": "ministral"}


def base_url(model):
    return f"https://{WORKSPACE}--sting-vllm-{FN[model]}.modal.run/v1"


def ModalClient():
    from src.llm.llm_client import LLMClient  # pre-existing

    class _ModalClient(LLMClient):
        def __init__(self):
            self._clients = {m: OpenAI(base_url=base_url(m), api_key="EMPTY", timeout=1500, max_retries=0) for m in FN}
            self.calls = 0

        def chat(self, messages, model="llama-3.1-8b", max_new_tokens=4096):
            self._client = self._clients[model]  # route, then defer to the pre-existing chat()
            for attempt in range(6):  # cold starts / transient 5xx return "" from the parent; retry those
                self.calls += 1
                content, rc = super().chat(messages, model, max_new_tokens)
                if content:
                    return content, rc
                time.sleep(10 * (attempt + 1))
            return "", ""

    return _ModalClient()
