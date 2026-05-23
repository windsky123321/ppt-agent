from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import get_settings
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
    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required for openai-compatible provider.")

    def generate_text(self, prompt: str) -> str:
        payload = self._request(prompt, response_format=None)
        return payload["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        payload = self._request(prompt, response_format={"type": "json_object"})
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)

    def _request(self, prompt: str, response_format: dict[str, str] | None) -> dict[str, Any]:
        url = self.settings.openai_base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        body: dict[str, Any] = {
            "model": self.settings.openai_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        if response_format:
            body["response_format"] = response_format
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            return response.json()


def create_llm_provider(parsed_paper: ParsedPaper | None = None) -> BaseLLMProvider:
    settings = get_settings()
    if settings.default_llm_provider.lower() == "openai":
        return OpenAICompatibleProvider()
    return MockLLMProvider(parsed_paper=parsed_paper)
