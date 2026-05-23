import type {
  ArtifactResponse,
  GenerationSettings,
  HealthStatus,
  ParsedInstructionSpec,
  PromptTemplate,
  RuntimeModelConfig,
  RuntimeModelConfigView,
  UploadResponse,
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
  deckMode = "Reading Group",
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (profileId) formData.append("profile_id", profileId);
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
