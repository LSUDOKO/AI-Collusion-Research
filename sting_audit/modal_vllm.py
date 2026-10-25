"""Modal app serving the starter roster (Zeng & Rudzicz-style 7-8B open-weight models) with vLLM's OpenAI server.

Exploratory replication only (not pre-registered). One L4 container per model, OpenAI-compatible endpoint at
https://<workspace>--sting-vllm-<fn>.modal.run/v1 ; the served model name is the Hugging Face id, so the
pre-existing LLMClient sampling (incl. top_k / repetition_penalty via extra_body) is used unchanged.

Deploy:  modal deploy sting_audit/modal_vllm.py     Stop:  modal app stop sting-vllm
"""
import subprocess

import modal

app = modal.App("sting-vllm")
image = (modal.Image.debian_slim(python_version="3.12")
         .uv_pip_install("vllm==0.10.1.1", "huggingface_hub[hf_transfer]")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"}))
hf_cache = modal.Volume.from_name("sting-hf-cache", create_if_missing=True)
vllm_cache = modal.Volume.from_name("sting-vllm-cache", create_if_missing=True)
COMMON = dict(image=image, gpu="L4", timeout=24 * 3600, scaledown_window=15 * 60, max_containers=1,
              secrets=[modal.Secret.from_name("huggingface-secret")],
              volumes={"/root/.cache/huggingface": hf_cache, "/root/.cache/vllm": vllm_cache})


def _serve(hf_id, extra=()):
    cmd = ["vllm", "serve", hf_id, "--served-model-name", hf_id, "--host", "0.0.0.0", "--port", "8000",
           "--max-model-len", "8192", "--gpu-memory-utilization", "0.92", *extra]
    subprocess.Popen(" ".join(cmd), shell=True)


@app.function(**COMMON)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=8000, startup_timeout=1200)
def llama31():
    _serve("meta-llama/Llama-3.1-8B-Instruct")


@app.function(**COMMON)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=8000, startup_timeout=1200)
def qwen25():
    _serve("Qwen/Qwen2.5-7B-Instruct")


@app.function(**COMMON)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=8000, startup_timeout=1200)
def llama32():
    _serve("meta-llama/Llama-3.2-3B-Instruct")


@app.function(**COMMON)
@modal.concurrent(max_inputs=32)
@modal.web_server(port=8000, startup_timeout=1200)
def ministral():
    _serve("mistralai/Ministral-8B-Instruct-2410",
           ["--tokenizer-mode", "mistral", "--config-format", "mistral", "--load-format", "mistral"])
