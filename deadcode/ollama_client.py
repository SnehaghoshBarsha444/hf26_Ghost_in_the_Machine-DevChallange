"""Minimal optional client for a locally running Ollama instance."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


DEFAULT_MODEL = "qwen2.5-coder:3b"
DEFAULT_HOST = "http://localhost:11434"


class OllamaError(RuntimeError):
    """Raised when the local model cannot be reached or returns an error."""


def explain_with_ollama(source: str, language: str, model: str = DEFAULT_MODEL) -> str:
    host = os.environ.get("OLLAMA_HOST", DEFAULT_HOST).rstrip("/")
    prompt = f"""You are DeadCode, a careful legacy-code preservation assistant.
Explain the following {language} source for a developer who may be unfamiliar with it.
Use these headings:
1. What it appears to do
2. Walkthrough of important statements
3. Questions or risks to verify
4. Preservation note

Rules:
- Do not claim to have executed or compiled the code.
- Distinguish observations from guesses.
- Do not invent missing business context.
- Mention dialect/version uncertainty when relevant.
- Keep the explanation concise and refer to line numbers where possible.

SOURCE START
{source[:18000]}
SOURCE END
"""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }).encode("utf-8")
    request = urllib.request.Request(
        f"{host}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaError(
            f"Could not reach Ollama at {host}. Is Ollama running and the model downloaded? Details: {exc}"
        ) from exc
    except (json.JSONDecodeError, TimeoutError) as exc:
        raise OllamaError(f"Ollama returned an invalid response or timed out: {exc}") from exc

    text = result.get("response", "").strip()
    if not text:
        raise OllamaError("The local model returned an empty explanation.")
    return text
