from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.deck import DeckPlan, DeckPlanSlide, PaperSummary, SlideDraft, SlideDrafts
from app.schemas.paper import ParsedPaper
from app.schemas.runtime_config import RuntimeModelConfig


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
        payload = self._request(prompt, response_format=None, revision_mode=False)
        return payload["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        payload = self._request(prompt, response_format={"type": "json_object"}, revision_mode=False)
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)

    def _request(self, prompt: str, response_format: dict[str, str] | None, revision_mode: bool) -> dict[str, Any]:
        base_url = self.runtime_config.llm_base_url if self.runtime_config else self.settings.openai_base_url
        api_key = self.runtime_config.llm_api_key if self.runtime_config else self.settings.openai_api_key
        preferred_model = self.runtime_config.llm_model if self.runtime_config else self.settings.openai_model
        fallback_model = self.runtime_config.fallback_llm_model if self.runtime_config else self.settings.fallback_openai_model
        url = base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": preferred_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.runtime_config.temperature if self.runtime_config else self.settings.temperature,
            "max_output_tokens": (
                self.runtime_config.revision_max_output_tokens if (self.runtime_config and revision_mode) else
                self.runtime_config.normal_max_output_tokens if self.runtime_config else
                self.settings.revision_max_output_tokens if revision_mode else
                self.settings.normal_max_output_tokens
            ),
            "reasoning_effort": self.runtime_config.reasoning_effort if self.runtime_config else self.settings.reasoning_effort,
            "verbosity": self.runtime_config.verbosity if self.runtime_config else self.settings.verbosity,
        }
        if response_format:
            body["response_format"] = response_format
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            if response.status_code >= 400 and preferred_model == "gpt-5.5" and fallback_model and fallback_model != preferred_model:
                body["model"] = fallback_model
                response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()


def create_llm_provider(parsed_paper: ParsedPaper | None = None, runtime_config: RuntimeModelConfig | None = None) -> BaseLLMProvider:
    settings = get_settings()
    provider_name = runtime_config.llm_provider if runtime_config else settings.default_llm_provider
    if provider_name.lower() in {"openai", "openai_compatible", "deepseek", "anthropic", "gemini"} and provider_name.lower() != "mock":
        return OpenAICompatibleProvider(runtime_config=runtime_config)
    return MockLLMProvider(parsed_paper=parsed_paper)
