"""Claude models via the Claude Code CLI in headless mode (`claude -p`), using the user's logged-in subscription (no API key).

Same chat(messages, model) -> (content, "") contract as the other clients. Each call is isolated so the model sees only
our prompt: the Claude Code system prompt is REPLACED (--system-prompt), all tools are disabled (--tools ""), no settings
/hooks/CLAUDE.md are loaded (--setting-sources "", run from an empty cwd), no MCP servers, no session persistence.
Used only for the exploratory Claude extension of the Phase A1 probe (not for the pre-registered games).
"""
import json
import subprocess
import tempfile
import threading
import time

ALIASES = {"claude-haiku": "haiku", "claude-sonnet": "sonnet", "claude-opus": "opus"}


class ClaudeCLIClient:
    MODEL_MAP = ALIASES

    def __init__(self):
        self.cwd = tempfile.mkdtemp(prefix="sting_claude_")
        self.lock = threading.Lock()
        self.canonical = {}  # alias -> canonical model id reported by the CLI

    def chat(self, messages, model="claude-haiku", max_new_tokens=4096):
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system") or "You are a helpful assistant."
        turns = [m for m in messages if m["role"] != "system"]
        if len(turns) == 1:
            prompt = turns[0]["content"]
        else:  # flatten a short multi-turn exchange (only used by the probe's single JSON-format retry)
            prompt = "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in turns)
        cmd = ["claude", "-p", prompt, "--model", ALIASES.get(model, model), "--system-prompt", system,
               "--tools", "", "--setting-sources", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--no-session-persistence", "--exclude-dynamic-system-prompt-sections", "--output-format", "json"]
        for attempt in range(4):
            try:
                out = subprocess.run(cmd, cwd=self.cwd, capture_output=True, text=True, timeout=240)
                d = json.loads(out.stdout)
                if d.get("is_error"):
                    raise RuntimeError(str(d.get("result"))[:200])
                with self.lock:
                    for k in d.get("modelUsage", {}):
                        self.canonical[model] = k
                return (d.get("result") or "").strip(), ""
            except Exception as e:  # noqa: BLE001
                print(f"[claude-cli] {model} attempt {attempt+1} failed: {str(e)[:160]}")
                time.sleep(10 * (attempt + 1))
        return "", ""
