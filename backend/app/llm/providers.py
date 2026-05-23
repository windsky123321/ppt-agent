from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.runtime_config import RuntimeModelConfig
from app.schemas.deck import DeckPlan, DeckPlanSlide, PaperSummary, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        raise NotImplementedError


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, parsed_paper: ParsedPaper | None = None) -> None:
        self.parsed_paper = parsed_paper

    def bind_paper(self, parsed_paper: ParsedPaper) -> "MockLLMProvider":
        self.parsed_paper = parsed_paper
        return self

    def generate_text(self, prompt: str) -> str:
        return f"Mock response for prompt: {prompt[:80]}"

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        raise ValueError(f"Unsupported schema_name: {schema_name}")


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, runtime_config: RuntimeModelConfig | None = None) -> None:
        self.settings = get_settings()
        self.runtime_config = runtime_config
        api_key = runtime_config.llm_api_key if runtime_config else self.settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for openai-compatible provider.")

    def generate_text(self, prompt: str) -> str:
        payload = self._request(prompt, response_format=None)
        return payload["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        payload = self._request(prompt, response_format={"type": "json_object"})
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)

    def _request(self, prompt: str, response_format: dict[str, str] | None) -> dict[str, Any]:
        base_url = self.runtime_config.llm_base_url if self.runtime_config else self.settings.openai_base_url
        api_key = self.runtime_config.llm_api_key if self.runtime_config else self.settings.openai_api_key
        model = self.runtime_config.llm_model if self.runtime_config else self.settings.openai_model
        url = base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        if response_format:
            body["response_format"] = response_format
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()


def create_llm_provider(parsed_paper: ParsedPaper | None = None, runtime_config: RuntimeModelConfig | None = None) -> BaseLLMProvider:
    settings = get_settings()
    provider_name = runtime_config.llm_provider if runtime_config else settings.default_llm_provider
    if provider_name.lower() in {"openai", "openai_compatible", "deepseek", "anthropic", "gemini"} and provider_name.lower() != "mock":
        return OpenAICompatibleProvider(runtime_config=runtime_config)
    return MockLLMProvider(parsed_paper=parsed_paper)
