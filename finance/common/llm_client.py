from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"
DEFAULT_MODEL = "glm-5.1"
MISSING_API_KEY_MESSAGE = (
    "未配置 FINANCE_LLM_API_KEY。请设置环境变量 FINANCE_LLM_API_KEY，或使用 --mode rule。"
)


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    base_url: str
    model: str


def get_llm_config() -> LLMConfig:
    api_key = _first_env(
        "FINANCE_LLM_API_KEY",
        "ARK_API_KEY",
        "VOLCANO_ENGINE_API_KEY",
        "OPENAI_API_KEY",
    )
    if not api_key:
        raise ValueError(MISSING_API_KEY_MESSAGE)

    base_url = _first_env(
        "FINANCE_LLM_BASE_URL",
        "ARK_BASE_URL",
        "OPENAI_BASE_URL",
    ) or DEFAULT_BASE_URL
    model = _first_env(
        "FINANCE_LLM_MODEL",
        "ARK_MODEL",
        "OPENAI_MODEL",
    ) or DEFAULT_MODEL

    return LLMConfig(api_key=api_key, base_url=base_url, model=model)


def chat_completion(
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int | None = None,
    config: LLMConfig | None = None,
) -> dict[str, Any]:
    llm_config = config or get_llm_config()
    payload: dict[str, Any] = {
        "model": llm_config.model,
        "messages": messages,
        "temperature": temperature,
    }
    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    request = urllib.request.Request(
        _chat_completions_url(llm_config.base_url),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {llm_config.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"LLM API request failed with status {error.code}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"LLM API request failed: {error.reason}") from error

    return json.loads(response_body)


def _first_env(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def _chat_completions_url(base_url: str) -> str:
    normalized = base_url.rstrip("/")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"
