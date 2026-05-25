import { useState } from "react";

import type {
  ArtifactResponse,
  CriticReport,
  GenerationSettings,
  GroundingReport,
  HealthStatus,
  ParsedInstructionSpec,
  PromptTemplate,
  RuntimeModelConfig,
  RuntimeModelConfigView,
  SkillManifest,
  SkillSearchResult,
  UploadResponse,
  UsageSummary,
  UsageTaskDetail,
  UserProfile,
} from "../types";

const defaultSettings: GenerationSettings = {
  language: "zh",
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
  long_instruction: "",
};

const defaultModelConfig: RuntimeModelConfig = {
  llm_provider: "mock",
  llm_base_url: "https://api.openai.com/v1",
  llm_api_key: "",
  llm_model: "gpt-5.5",
  fallback_llm_model: "gpt-4.1-mini",
  vision_provider: "mock",
  vision_base_url: "https://api.openai.com/v1",
  vision_api_key: "",
  vision_model: "gpt-4.1-mini",
  enable_vision: true,
  enable_critic: true,
  enable_repair: true,
  max_repair_loops: 2,
  reasoning_effort: "low",
  verbosity: "low",
  temperature: 0.2,
  patch_mode: true,
  revision_max_output_tokens: 1200,
  normal_max_output_tokens: 4000,
  output_dir: "storage/decks",
  skills_enabled: true,
  auto_select_skills: true,
  max_skills_per_task: 3,
  max_skill_context_tokens: 800,
  allow_skill_scripts: false,
  allowed_skill_risk_level: "low",
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
  const [regenLongInstruction, setRegenLongInstruction] = useState("");
  const [regenSlideId, setRegenSlideId] = useState("slide_02");
  const [deckMode, setDeckMode] = useState("reading_group");
  const [modelConfig, setModelConfig] = useState<RuntimeModelConfig>(defaultModelConfig);
  const [modelConfigView, setModelConfigView] = useState<RuntimeModelConfigView | null>(null);
  const [modelStatus, setModelStatus] = useState("");
  const [backendConnected, setBackendConnected] = useState(false);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [parsedInstruction, setParsedInstruction] = useState<ParsedInstructionSpec | null>(null);
  const [promptTemplates, setPromptTemplates] = useState<PromptTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [skills, setSkills] = useState<SkillManifest[]>([]);
  const [skillSearchResults, setSkillSearchResults] = useState<SkillSearchResult[]>([]);
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null);
  const [usageTasks, setUsageTasks] = useState<UsageTaskDetail[]>([]);

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
    regenLongInstruction,
    setRegenLongInstruction,
    regenSlideId,
    setRegenSlideId,
    deckMode,
    setDeckMode,
    modelConfig,
    setModelConfig,
    modelConfigView,
    setModelConfigView,
    modelStatus,
    setModelStatus,
    backendConnected,
    setBackendConnected,
    health,
    setHealth,
    parsedInstruction,
    setParsedInstruction,
    promptTemplates,
    setPromptTemplates,
    selectedTemplateId,
    setSelectedTemplateId,
    loading,
    setLoading,
    error,
    setError,
    skills,
    setSkills,
    skillSearchResults,
    setSkillSearchResults,
    usageSummary,
    setUsageSummary,
    usageTasks,
    setUsageTasks,
  };
}
