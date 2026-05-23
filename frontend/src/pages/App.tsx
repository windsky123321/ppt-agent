import { fetchArtifacts, fetchJsonArtifact, fetchProfiles, regenerateSlides, saveProfile, uploadPaper } from "../api/client";
import { ArtifactsPanel } from "../components/ArtifactsPanel";
import { OutlinePreview } from "../components/OutlinePreview";
import { ProfilePanel } from "../components/ProfilePanel";
import { RegeneratePanel } from "../components/RegeneratePanel";
import { SettingsPanel } from "../components/SettingsPanel";
import { StatusPanel } from "../components/StatusPanel";
import { UploadPanel } from "../components/UploadPanel";
import { WarningsPanel } from "../components/WarningsPanel";
import { useAppState } from "../stores/useAppState";
import type { CriticReport, GroundingReport, UserProfile } from "../types";
import { useEffect } from "react";

export function App() {
  const state = useAppState();

  useEffect(() => {
    fetchProfiles()
      .then((profiles) => {
        state.setProfiles(profiles);
        if (profiles[0] && !state.activeProfileId) {
          state.setActiveProfileId(profiles[0].id);
          state.setEditingProfile(profiles[0]);
        }
      })
      .catch((error) => state.setError(error instanceof Error ? error.message : "Failed to load profiles."));
  }, []);

  async function handleGenerate() {
    if (!state.selectedFile) {
      state.setError("Please choose a PDF file first.");
      return;
    }

    state.setLoading(true);
    state.setError("");
    try {
      const result = await uploadPaper(state.selectedFile, state.settings, state.activeProfileId || undefined);
      state.setResult(result);
      const [artifacts, criticReport, groundingReport] = await Promise.all([
        fetchArtifacts(result.job.deck_id),
        fetchJsonArtifact<CriticReport>(result.job.deck_id, "critic_report.json").catch(() => null),
        fetchJsonArtifact<GroundingReport>(result.job.deck_id, "grounding_report.json").catch(() => null),
      ]);
      state.setArtifacts(artifacts);
      state.setCriticReport(criticReport);
      state.setGroundingReport(groundingReport);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "Unknown error");
    } finally {
      state.setLoading(false);
    }
  }

  async function handleSaveProfile() {
    if (!state.editingProfile) return;
    try {
      const { id, ...rest } = state.editingProfile;
      const saved = await saveProfile(rest as Omit<UserProfile, "id">, id.startsWith("profile_preset_") ? undefined : id);
      const profiles = await fetchProfiles();
      state.setProfiles(profiles);
      state.setActiveProfileId(saved.id);
      state.setEditingProfile(saved);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "Failed to save profile.");
    }
  }

  async function handleRegenerateSlide() {
    if (!state.result?.job.deck_id) return;
    state.setLoading(true);
    state.setError("");
    try {
      const response = await regenerateSlides(state.result.job.deck_id, [state.regenSlideId], state.regenInstruction, state.activeProfileId || undefined);
      state.setResult((current) => (current ? { ...current, job: response.job } : current));
      const [artifacts, criticReport, groundingReport] = await Promise.all([
        fetchArtifacts(state.result.job.deck_id),
        fetchJsonArtifact<CriticReport>(state.result.job.deck_id, "critic_report.json").catch(() => null),
        fetchJsonArtifact<GroundingReport>(state.result.job.deck_id, "grounding_report.json").catch(() => null),
      ]);
      state.setArtifacts(artifacts);
      state.setCriticReport(criticReport);
      state.setGroundingReport(groundingReport);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "Regeneration failed.");
    } finally {
      state.setLoading(false);
    }
  }

  return (
    <main className="min-h-screen px-4 py-10 text-ink md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-8 rounded-[2rem] bg-white/75 p-8 shadow-card backdrop-blur">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-accent">Local-First MVP</p>
          <h1 className="mt-3 text-4xl font-semibold tracking-tight">Personalized Paper-to-PPT Agent</h1>
          <p className="mt-4 max-w-3xl text-base text-slate-600">
            Upload an academic paper PDF, generate grounded intermediate artifacts, and download an editable PowerPoint deck built with local file storage.
          </p>
        </header>

        <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <UploadPanel selectedFile={state.selectedFile} onFileChange={state.setSelectedFile} />
            <ProfilePanel
              profiles={state.profiles}
              activeProfileId={state.activeProfileId}
              editingProfile={state.editingProfile}
              onSelect={(profileId) => {
                state.setActiveProfileId(profileId);
                const selected = state.profiles.find((profile) => profile.id === profileId) ?? null;
                state.setEditingProfile(selected);
              }}
              onEditChange={state.setEditingProfile}
              onSave={handleSaveProfile}
            />
            <SettingsPanel settings={state.settings} onChange={state.setSettings} />
            <StatusPanel loading={state.loading} error={state.error} job={state.result?.job ?? null} onGenerate={handleGenerate} disabled={state.loading} />
            <RegeneratePanel
              deckId={state.result?.job.deck_id ?? null}
              slideId={state.regenSlideId}
              instruction={state.regenInstruction}
              onSlideIdChange={state.setRegenSlideId}
              onInstructionChange={state.setRegenInstruction}
              onRegenerate={handleRegenerateSlide}
              disabled={state.loading}
            />
          </div>
          <div className="space-y-6">
            <ArtifactsPanel job={state.result?.job ?? null} artifacts={state.artifacts} />
            <WarningsPanel criticReport={state.criticReport} groundingReport={state.groundingReport} />
            <OutlinePreview parsedPaper={state.result?.parsed_paper ?? null} />
          </div>
        </div>
      </div>
    </main>
  );
}
