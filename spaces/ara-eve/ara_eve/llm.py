"""OpenAI-compatible chat via Hugging Face Inference Providers. LLM never writes affect."""

from __future__ import annotations

import os
from collections.abc import Sequence

from .persona import SAMPLING

DEFAULT_MODELS = [
    ("Qwen/Qwen2.5-7B-Instruct", "Qwen 2.5 7B Instruct"),
    ("meta-llama/Llama-3.1-8B-Instruct", "Llama 3.1 8B Instruct"),
    ("google/gemma-2-9b-it", "Gemma 2 9B IT"),
    ("HuggingFaceH4/zephyr-7b-beta", "Zephyr 7B (less censored)"),
]

LOCAL_UNCENSORED_HINT = "Gemma-4-E4B-Uncensored-HauhauCS-Aggressive (Ollama Modelfile / local GGUF)"


def list_models() -> list[str]:
    extra = os.environ.get("ARA_EVE_MODELS", "")
    ids = [m[0] for m in DEFAULT_MODELS]
    if extra:
        ids = [x.strip() for x in extra.split(",") if x.strip()] + ids
    return ids


def complete(
    messages: Sequence[dict],
    model: str,
    *,
    token: str | None = None,
) -> str:
    key = token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if not key:
        raise RuntimeError("no_hf_token")
    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError("huggingface_hub missing") from exc

    client = InferenceClient(model=model, token=key)
    response = client.chat_completion(
        messages=list(messages),
        max_tokens=900,
        temperature=SAMPLING["temperature"],
        top_p=SAMPLING["top_p"],
    )
    choice = response.choices[0].message
    content = getattr(choice, "content", None) or ""
    if isinstance(content, list):
        content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return str(content).strip()
