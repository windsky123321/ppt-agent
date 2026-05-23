import type { ArtifactResponse, GenerationSettings, UploadResponse, UserProfile } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function uploadPaper(file: File, settings: GenerationSettings, profileId?: string): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (profileId) {
    formData.append("profile_id", profileId);
  }
  formData.append("language", settings.language);
  formData.append("audience", settings.audience);
  formData.append("slide_count", String(settings.slide_count));
  formData.append("include_speaker_notes", String(settings.include_speaker_notes));
  formData.append("include_source_footers", String(settings.include_source_footers));
  formData.append("theme", settings.theme);

  const response = await fetch(`${API_BASE}/api/papers/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "Upload failed.");
  }

  return response.json();
}

export function makeDownloadUrl(deckId: string): string {
  return `${API_BASE}/api/decks/${deckId}/download`;
}

export async function fetchProfiles(): Promise<UserProfile[]> {
  const response = await fetch(`${API_BASE}/api/profiles`);
  if (!response.ok) {
    throw new Error("Failed to load profiles.");
  }
  const payload = await response.json();
  return payload.profiles;
}

export async function saveProfile(profile: Omit<UserProfile, "id">, profileId?: string): Promise<UserProfile> {
  const response = await fetch(profileId ? `${API_BASE}/api/profiles/${profileId}` : `${API_BASE}/api/profiles`, {
    method: profileId ? "PUT" : "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  if (!response.ok) {
    throw new Error("Failed to save profile.");
  }
  return response.json();
}

export async function fetchArtifacts(deckId: string): Promise<ArtifactResponse> {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/artifacts`);
  if (!response.ok) {
    throw new Error("Failed to load artifacts.");
  }
  return response.json();
}

export async function fetchJsonArtifact<T>(deckId: string, artifactName: string): Promise<T> {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/artifacts/${artifactName}`);
  if (!response.ok) {
    throw new Error(`Failed to load ${artifactName}.`);
  }
  return response.json();
}

export async function regenerateSlides(deckId: string, slideIds: string[], instruction: string, profileId?: string) {
  const response = await fetch(`${API_BASE}/api/decks/${deckId}/regenerate-slide`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slide_ids: slideIds, instruction, profile_id: profileId }),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? "Failed to regenerate slide.");
  }
  return response.json();
}
