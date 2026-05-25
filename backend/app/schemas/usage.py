from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


UsageMode = Literal["normal", "revision", "patch", "mock"]


class UsageRecord(BaseModel):
    task_id: str
    session_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model: str = ""
    fallback_model: str = ""
    stage: str = ""
    round: int = 1
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cached_tokens: int | None = None
    reasoning_tokens: int | None = None
    estimated_cost: float | None = None
    request_count: int = 0
    retry_count: int = 0
    error_count: int = 0
    duration_ms: int = 0
    mode: UsageMode = "normal"
    slide_count: int = 0
    output_file: str = ""
    mock: bool = False
    provider_usage_available: bool = True


class UsageSummary(BaseModel):
    total_records: int = 0
    total_prompt_tokens: int | None = None
    total_completion_tokens: int | None = None
    total_tokens: int | None = None
    total_request_count: int = 0
    total_retry_count: int = 0
    total_error_count: int = 0
    total_estimated_cost: float | None = None
    unknown_usage_records: int = 0


class UsageTaskDetail(BaseModel):
    task_id: str
    records: list[UsageRecord] = Field(default_factory=list)


class UsageTasksResponse(BaseModel):
    tasks: list[UsageTaskDetail] = Field(default_factory=list)
