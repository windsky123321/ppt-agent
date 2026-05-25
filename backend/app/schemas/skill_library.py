from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high", "unknown"]


class SkillManifest(BaseModel):
    id: str
    name: str
    description: str = ""
    version: str = "0.1.0"
    source: str = ""
    author: str = ""
    homepage: str = ""
    license: str = ""
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    entrypoints: list[str] = Field(default_factory=list)
    enabled: bool = False
    trusted: bool = False
    risk_level: RiskLevel = "unknown"
    installed_at: str = ""
    last_used_at: str = ""
    checksum: str = ""
    suggestions: list[str] = Field(default_factory=list)
    templates: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class SkillRegistry(BaseModel):
    skills: list[SkillManifest] = Field(default_factory=list)


class SkillSearchRequest(BaseModel):
    keyword: str = ""
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)


class SkillSearchResult(BaseModel):
    id: str
    name: str
    description: str
    source: str
    author: str = ""
    updated_at: str = ""
    license: str = ""
    tags: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = "unknown"
    preview_url: str = ""
    installable: bool = True


class SkillSearchResponse(BaseModel):
    query: SkillSearchRequest
    results: list[SkillSearchResult] = Field(default_factory=list)


class SkillImportResponse(BaseModel):
    skill: SkillManifest
    warnings: list[str] = Field(default_factory=list)
    preview_only: bool = False


class SkillTestResponse(BaseModel):
    skill_id: str
    ok: bool
    message: str
    suggestions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class SkillUsageRecord(BaseModel):
    skill_id: str
    stage: str
    used_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    suggestions: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
