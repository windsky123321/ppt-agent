import { useState } from "react";

import type { ArtifactResponse, CriticReport, GenerationSettings, GroundingReport, UploadResponse, UserProfile } from "../types";

const defaultSettings: GenerationSettings = {
  language: "en",
  audience: "graduate",
  slide_count: 10,
  include_speaker_notes: true,
  include_source_footers: true,
  theme: "academic_clean",
  presentation_goal: "summarize",
  tone: "academic",
  math_level: "balanced",
  include_limitations: true,
  include_discussion_questions: true,
  talk_duration_minutes: 12,
  visual_density: "balanced",
};

export function useAppState() {
  const [settings, setSettings] = useState<GenerationSettings>(defaultSettings);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [profiles, setProfiles] = useState<UserProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string>("");
  const [editingProfile, setEditingProfile] = useState<UserProfile | null>(null);
  const [artifacts, setArtifacts] = useState<ArtifactResponse | null>(null);
  const [criticReport, setCriticReport] = useState<CriticReport | null>(null);
  const [groundingReport, setGroundingReport] = useState<GroundingReport | null>(null);
  const [regenInstruction, setRegenInstruction] = useState("");
  const [regenSlideId, setRegenSlideId] = useState("slide_02");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  return {
    settings,
    setSettings,
    selectedFile,
    setSelectedFile,
    result,
    setResult,
    profiles,
    setProfiles,
    activeProfileId,
    setActiveProfileId,
    editingProfile,
    setEditingProfile,
    artifacts,
    setArtifacts,
    criticReport,
    setCriticReport,
    groundingReport,
    setGroundingReport,
    regenInstruction,
    setRegenInstruction,
    regenSlideId,
    setRegenSlideId,
    loading,
    setLoading,
    error,
    setError,
  };
}
