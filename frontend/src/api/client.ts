import type {
  ArtifactResponse,
  GenerationSettings,
  HealthStatus,
  ParsedInstructionSpec,
  PromptTemplate,
  RuntimeModelConfig,
  RuntimeModelConfigView,
  SkillImportResponse,
  SkillManifest,
  SkillSearchRequest,
  SkillSearchResult,
  SkillTestResponse,
  UploadResponse,
  UsageSummary,
  UsageTaskDetail,
  UserProfile,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseJsonOrThrow(response: Response, fallbackMessage: string) {
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? fallbackMessage);
  }
  return response.json();
}

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE}/api/health`);
  return parseJsonOrThrow(response, "后端健康检查失败。");
}

export async function uploadPaper(
  file: File,
  settings: GenerationSettings,
  profileId?: string,
  deckMode = "reading_group",
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (profileId) {
    formData.append("profile_id", profileId);
  }
  formData.append("deck_mode", deckMode);
  formData.append("long_instruction", settings.long_instruction);
  formData.append("language", settings.language);
  formData.append("audience", settings.audience);
  formData.append("slide_count", String(settings.slide_count));
  formData.append("include_speaker_notes", String(settings.include_speaker_notes));
  formData.append("include_source_footers", String(settings.include_source_footers));
  formData.append("theme", settings.theme);

  const response = await fetch(`${API_BASE}/api/papers/upload`, { method: "POST", body: formData });
  return parseJsonOrThrow(response, "PDF 上传失败。");
}

export function makeDownloadUrl(deckId: string): string {
  return `${API_BASE}/api/decks/${deckId}/download`;
}

export async function fetchProfiles(): Promise<UserProfile[]> {
  const response = await fetch(`${API_BASE}/api/profiles`);
  const payload = await parseJsonOrThrow(response, "读取配置档失败。");
  return payload.profiles;
}

export async function saveProfile(profile: Omit<UserProfile, "id">, profileId?: string): Promise<UserProfile> {
  const response = await fetch(profileId ? `${API_BASE}/api/profiles/${profileId}` : `${API_BASE}/api/profiles`, {
    method: profileId ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  return parseJsonOrThrow(response, "保存配置档失败。");
}

export async function fetchArtifacts(deckId: string): Promise<ArtifactResponse> {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/artifacts`);
  return parseJsonOrThrow(response, "读取产物列表失败。");
}

export async function fetchJsonArtifact<T>(deckId: string, artifactName: string): Promise<T> {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/artifacts/${artifactName}`);
  return parseJsonOrThrow(response, `读取 ${artifactName} 失败。`);
}

export async function regenerateSlides(
  deckId: string,
  slideIds: string[],
  instruction: string,
  profileId?: string,
  longInstruction = "",
) {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/regenerate-slide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slide_ids: slideIds, instruction, profile_id: profileId, long_instruction: longInstruction }),
  });
  return parseJsonOrThrow(response, "单页精修失败。");
}

export async function getModelConfig(): Promise<RuntimeModelConfigView> {
  const response = await fetch(`${API_BASE}/api/config/model`);
  return parseJsonOrThrow(response, "读取模型配置失败。");
}

export async function saveModelConfig(config: RuntimeModelConfig): Promise<RuntimeModelConfigView> {
  const response = await fetch(`${API_BASE}/api/config/model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  return parseJsonOrThrow(response, "模型配置保存失败。");
}

export async function testModelConfig(config: RuntimeModelConfig) {
  const response = await fetch(`${API_BASE}/api/config/model/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  });
  return parseJsonOrThrow(response, "模型连接测试失败。");
}

export async function parseInstruction(rawText: string, languageHint: string): Promise<ParsedInstructionSpec> {
  const response = await fetch(`${API_BASE}/api/instructions/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, language_hint: languageHint, save_as_preset: false }),
  });
  return parseJsonOrThrow(response, "需求解析失败。");
}

export async function fetchPromptTemplates(): Promise<PromptTemplate[]> {
  const response = await fetch(`${API_BASE}/api/prompt-templates`);
  const payload = await parseJsonOrThrow(response, "读取提示词模板失败。");
  return payload.templates;
}

export async function savePromptTemplate(template: PromptTemplate): Promise<PromptTemplate> {
  const response = await fetch(`${API_BASE}/api/prompt-templates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(template),
  });
  return parseJsonOrThrow(response, "保存提示词模板失败。");
}

export async function fetchSkills(): Promise<SkillManifest[]> {
  const response = await fetch(`${API_BASE}/api/skills`);
  const payload = await parseJsonOrThrow(response, "读取技能列表失败。");
  return payload.skills;
}

export async function searchSkills(payload: SkillSearchRequest): Promise<SkillSearchResult[]> {
  const response = await fetch(`${API_BASE}/api/skills/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await parseJsonOrThrow(response, "搜索技能失败。");
  return data.results;
}

export async function importSkill(formData: FormData): Promise<SkillImportResponse> {
  const response = await fetch(`${API_BASE}/api/skills/import`, {
    method: "POST",
    body: formData,
  });
  return parseJsonOrThrow(response, "导入技能失败。");
}

export async function enableSkill(skillId: string): Promise<SkillManifest> {
  const response = await fetch(`${API_BASE}/api/skills/${skillId}/enable`, { method: "POST" });
  return parseJsonOrThrow(response, "启用技能失败。");
}

export async function disableSkill(skillId: string): Promise<SkillManifest> {
  const response = await fetch(`${API_BASE}/api/skills/${skillId}/disable`, { method: "POST" });
  return parseJsonOrThrow(response, "禁用技能失败。");
}

export async function deleteSkill(skillId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/api/skills/${skillId}`, { method: "DELETE" });
  await parseJsonOrThrow(response, "删除技能失败。");
}

export async function testSkill(skillId: string): Promise<SkillTestResponse> {
  const response = await fetch(`${API_BASE}/api/skills/${skillId}/test`, { method: "POST" });
  return parseJsonOrThrow(response, "测试技能失败。");
}

export async function fetchUsageSummary(): Promise<UsageSummary> {
  const response = await fetch(`${API_BASE}/api/usage/summary`);
  const payload = await parseJsonOrThrow(response, "读取 Token 统计失败。");
  return payload.summary;
}

export async function fetchUsageTasks(): Promise<UsageTaskDetail[]> {
  const response = await fetch(`${API_BASE}/api/usage/tasks`);
  const payload = await parseJsonOrThrow(response, "读取任务统计失败。");
  return payload.tasks;
}

export async function fetchUsageTask(taskId: string): Promise<UsageTaskDetail> {
  const response = await fetch(`${API_BASE}/api/usage/tasks/${taskId}`);
  const payload = await parseJsonOrThrow(response, "读取任务明细失败。");
  return payload.task;
}

export function makeUsageExportUrl(kind: "csv" | "json"): string {
  return `${API_BASE}/api/usage/export.${kind}`;
}

export async function clearUsage(): Promise<void> {
  const response = await fetch(`${API_BASE}/api/usage`, { method: "DELETE" });
  await parseJsonOrThrow(response, "清空统计失败。");
}
