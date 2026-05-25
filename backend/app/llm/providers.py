from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import get_settings
from app.schemas.paper import ParsedPaper
from app.schemas.runtime_config import RuntimeModelConfig
from app.schemas.usage import UsageRecord
from app.storage.usage_storage import UsageStorage


class BaseLLMProvider(ABC):
    def __init__(self) -> None:
        self.usage_storage = UsageStorage()
        self.usage_context: dict[str, Any] = {
            "task_id": "",
            "session_id": "",
            "stage": "",
            "round": 1,
            "mode": "normal",
            "slide_count": 0,
            "output_file": "",
        }

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        raise NotImplementedError

    def set_usage_context(self, **context: Any) -> None:
        self.usage_context.update(context)

    def record_usage(
        self,
        *,
        model: str,
        fallback_model: str,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        total_tokens: int | None,
        cached_tokens: int | None,
        reasoning_tokens: int | None,
        duration_ms: int,
        mock: bool,
        provider_usage_available: bool,
        request_count: int = 1,
        error_count: int = 0,
    ) -> None:
        record = UsageRecord(
            task_id=self.usage_context.get("task_id", ""),
            session_id=self.usage_context.get("session_id", ""),
            model=model,
            fallback_model=fallback_model,
            stage=self.usage_context.get("stage", ""),
            round=int(self.usage_context.get("round", 1) or 1),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
            request_count=request_count,
            error_count=error_count,
            duration_ms=duration_ms,
            mode=self.usage_context.get("mode", "normal"),
            slide_count=int(self.usage_context.get("slide_count", 0) or 0),
            output_file=self.usage_context.get("output_file", ""),
            mock=mock,
            provider_usage_available=provider_usage_available,
        )
        self.usage_storage.record(record)


class MockLLMProvider(BaseLLMProvider):
    def __init__(self, parsed_paper: ParsedPaper | None = None) -> None:
        super().__init__()
        self.parsed_paper = parsed_paper

    def bind_paper(self, parsed_paper: ParsedPaper) -> "MockLLMProvider":
        self.parsed_paper = parsed_paper
        return self

    def generate_text(self, prompt: str) -> str:
        self.record_usage(
            model="mock",
            fallback_model="",
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            cached_tokens=None,
            reasoning_tokens=None,
            duration_ms=0,
            mock=True,
            provider_usage_available=False,
        )
        return f"Mock response for prompt: {prompt[:80]}"

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        self.record_usage(
            model="mock",
            fallback_model="",
            prompt_tokens=None,
            completion_tokens=None,
            total_tokens=None,
            cached_tokens=None,
            reasoning_tokens=None,
            duration_ms=0,
            mock=True,
            provider_usage_available=False,
        )
        raise ValueError(f"Unsupported schema_name: {schema_name}")


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self, runtime_config: RuntimeModelConfig | None = None) -> None:
        super().__init__()
        self.settings = get_settings()
        self.runtime_config = runtime_config
        api_key = runtime_config.llm_api_key if runtime_config else self.settings.openai_api_key
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for openai-compatible provider.")

    def generate_text(self, prompt: str) -> str:
        payload = self._request(prompt, response_format=None, revision_mode=False)
        return payload["choices"][0]["message"]["content"]

    def generate_json(self, prompt: str, schema_name: str) -> dict[str, Any]:
        _ = schema_name
        payload = self._request(prompt, response_format={"type": "json_object"}, revision_mode=False)
        content = payload["choices"][0]["message"]["content"]
        return json.loads(content)

    def _request(self, prompt: str, response_format: dict[str, str] | None, revision_mode: bool) -> dict[str, Any]:
        base_url = self.runtime_config.llm_base_url if self.runtime_config else self.settings.openai_base_url
        api_key = self.runtime_config.llm_api_key if self.runtime_config else self.settings.openai_api_key
        preferred_model = self.runtime_config.llm_model if self.runtime_config else self.settings.openai_model
        fallback_model = (
            self.runtime_config.fallback_llm_model if self.runtime_config else self.settings.fallback_openai_model
        )
        url = base_url.rstrip("/") + "/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        config = self.runtime_config
        body: dict[str, Any] = {
            "model": preferred_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.temperature if config else self.settings.temperature,
            "max_output_tokens": (
                config.revision_max_output_tokens
                if config and revision_mode
                else config.normal_max_output_tokens
                if config
                else self.settings.revision_max_output_tokens
                if revision_mode
                else self.settings.normal_max_output_tokens
            ),
            "reasoning_effort": config.reasoning_effort if config else self.settings.reasoning_effort,
            "verbosity": config.verbosity if config else self.settings.verbosity,
        }
        if response_format:
            body["response_format"] = response_format
        started = time.perf_counter()
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, headers=headers, json=body)
            if (
                response.status_code >= 400
                and preferred_model == "gpt-5.5"
                and fallback_model
                and fallback_model != preferred_model
            ):
                body["model"] = fallback_model
                response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
        usage = payload.get("usage", {}) if isinstance(payload, dict) else {}
        prompt_details = usage.get("prompt_tokens_details", {}) if isinstance(usage, dict) else {}
        completion_details = usage.get("completion_tokens_details", {}) if isinstance(usage, dict) else {}
        self.record_usage(
            model=str(body["model"]),
            fallback_model=fallback_model,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            total_tokens=usage.get("total_tokens"),
            cached_tokens=prompt_details.get("cached_tokens"),
            reasoning_tokens=completion_details.get("reasoning_tokens"),
            duration_ms=int((time.perf_counter() - started) * 1000),
            mock=False,
            provider_usage_available=bool(usage),
        )
        return payload


def create_llm_provider(
    parsed_paper: ParsedPaper | None = None,
    runtime_config: RuntimeModelConfig | None = None,
) -> BaseLLMProvider:
    settings = get_settings()
    provider_name = runtime_config.llm_provider if runtime_config else settings.default_llm_provider
    if provider_name.lower() in {"openai", "openai_compatible", "deepseek", "anthropic", "gemini"} and provider_name.lower() != "mock":
        return OpenAICompatibleProvider(runtime_config=runtime_config)
    return MockLLMProvider(parsed_paper=parsed_paper)
