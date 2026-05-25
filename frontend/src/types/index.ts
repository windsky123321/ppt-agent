export type GenerationSettings = {
  language: "zh" | "en" | "bilingual";
  audience: "general" | "undergraduate" | "graduate" | "expert" | "investor" | "lab_meeting" | "thesis_defense";
  slide_count: number;
  include_speaker_notes: boolean;
  include_source_footers: boolean;
  theme: "academic_clean" | "dark_modern" | "minimalist_white";
  presentation_goal: "summarize" | "explain" | "teach" | "critique" | "persuade" | "compare";
  tone: "academic" | "concise" | "visual" | "storytelling" | "technical";
  math_level: "simplified" | "balanced" | "detailed";
  include_limitations: boolean;
  include_discussion_questions: boolean;
  talk_duration_minutes: number;
  visual_density: string;
  long_instruction: string;
};

export type HealthStatus = {
  status: string;
  backend: string;
  version: string;
  storage_dir: string;
  llm_configured: boolean;
  vision_configured: boolean;
};

export type SkillManifest = {
  id: string;
  name: string;
  description: string;
  version: string;
  source: string;
  author: string;
  homepage: string;
  license: string;
  tags: string[];
  capabilities: string[];
  entrypoints: string[];
  enabled: boolean;
  trusted: boolean;
  risk_level: "low" | "medium" | "high" | "unknown";
  installed_at: string;
  last_used_at: string;
  checksum: string;
  suggestions: string[];
  templates: string[];
  constraints: string[];
};

export type SkillSearchRequest = {
  keyword: string;
  tags: string[];
  capabilities: string[];
};

export type SkillSearchResult = {
  id: string;
  name: string;
  description: string;
  source: string;
  author: string;
  updated_at: string;
  license: string;
  tags: string[];
  capabilities: string[];
  risk_level: "low" | "medium" | "high" | "unknown";
  preview_url: string;
  installable: boolean;
};

export type SkillImportResponse = {
  skill: SkillManifest;
  warnings: string[];
  preview_only: boolean;
};

export type SkillTestResponse = {
  skill_id: string;
  ok: boolean;
  message: string;
  suggestions: string[];
  constraints: string[];
};

export type UsageRecord = {
  task_id: string;
  session_id: string;
  created_at: string;
  model: string;
  fallback_model: string;
  stage: string;
  round: number;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
  cached_tokens: number | null;
  reasoning_tokens: number | null;
  estimated_cost: number | null;
  request_count: number;
  retry_count: number;
  error_count: number;
  duration_ms: number;
  mode: "normal" | "revision" | "patch" | "mock";
  slide_count: number;
  output_file: string;
  mock: boolean;
  provider_usage_available: boolean;
};

export type UsageSummary = {
  total_records: number;
  total_prompt_tokens: number | null;
  total_completion_tokens: number | null;
  total_tokens: number | null;
  total_request_count: number;
  total_retry_count: number;
  total_error_count: number;
  total_estimated_cost: number | null;
  unknown_usage_records: number;
};

export type UsageTaskDetail = {
  task_id: string;
  records: UsageRecord[];
};

export type UserProfile = {
  id: string;
  name: string;
  audience: GenerationSettings["audience"];
  presentation_goal: GenerationSettings["presentation_goal"];
  preferred_language: GenerationSettings["language"];
  tone: GenerationSettings["tone"];
  slide_count_target: number;
  talk_duration_minutes: number;
  math_level: GenerationSettings["math_level"];
  include_speaker_notes: boolean;
  include_limitations: boolean;
  include_discussion_questions: boolean;
  include_source_footers: boolean;
  theme_id: GenerationSettings["theme"];
  brand_colors: string[];
  title_font: string;
  body_font: string;
  custom_instructions: string;
  long_generation_instruction: string;
};

export type ArtifactItem = {
  name: string;
  path: string;
  exists: boolean;
  modified_time?: number | null;
  download_url?: string | null;
};

export type JobStatus = {
  job_id: string;
  status: string;
  paper_id: string;
  deck_id: string;
  message: string;
  artifacts: ArtifactItem[];
  profile_id?: string | null;
  current_stage?: string;
  critic_approved?: boolean | null;
  grounding_warning_count?: number | null;
};

export type ParsedPaper = {
  paper_id: string;
  title: string;
  authors: string[];
  abstract: string;
  sections: { title: string; text: string; page_start: number; page_end: number }[];
};

export type UploadResponse = {
  job: JobStatus;
  parsed_paper: ParsedPaper;
  artifacts_url: string;
  download_url: string;
};

export type GroundingWarning = {
  slide_id: string;
  severity: string;
  message: string;
};

export type GroundingReport = {
  slide_count: number;
  warnings: GroundingWarning[];
};

export type CriticIssue = {
  slide_id: string;
  severity: "low" | "medium" | "high";
  category: string;
  description: string;
  suggested_fix: string;
  requires_regeneration: boolean;
};

export type CriticReport = {
  deck_score: number;
  summary: string;
  issues: CriticIssue[];
  approved: boolean;
};

export type ArtifactResponse = {
  deck_id: string;
  artifacts: ArtifactItem[];
  deck_status: string;
  grounding_status?: number | null;
  critic_approval_status?: boolean | null;
};

export type RuntimeModelConfigView = {
  llm_provider: string;
  llm_base_url: string;
  llm_api_key_masked: string;
  llm_model: string;
  fallback_llm_model: string;
  vision_provider: string;
  vision_base_url: string;
  vision_api_key_masked: string;
  vision_model: string;
  enable_vision: boolean;
  enable_critic: boolean;
  enable_repair: boolean;
  max_repair_loops: number;
  reasoning_effort: string;
  verbosity: string;
  temperature: number;
  patch_mode: boolean;
  revision_max_output_tokens: number;
  normal_max_output_tokens: number;
  output_dir: string;
  skills_enabled: boolean;
  auto_select_skills: boolean;
  max_skills_per_task: number;
  max_skill_context_tokens: number;
  allow_skill_scripts: boolean;
  allowed_skill_risk_level: string;
};

export type RuntimeModelConfig = {
  llm_provider: string;
  llm_base_url: string;
  llm_api_key: string;
  llm_model: string;
  fallback_llm_model: string;
  vision_provider: string;
  vision_base_url: string;
  vision_api_key: string;
  vision_model: string;
  enable_vision: boolean;
  enable_critic: boolean;
  enable_repair: boolean;
  max_repair_loops: number;
  reasoning_effort: string;
  verbosity: string;
  temperature: number;
  patch_mode: boolean;
  revision_max_output_tokens: number;
  normal_max_output_tokens: number;
  output_dir: string;
  skills_enabled: boolean;
  auto_select_skills: boolean;
  max_skills_per_task: number;
  max_skill_context_tokens: number;
  allow_skill_scripts: boolean;
  allowed_skill_risk_level: string;
};

export type ParsedInstructionSpec = {
  detected_language: string;
  audience?: string | null;
  presentation_goal?: string | null;
  preferred_language?: string | null;
  tone?: string | null;
  slide_count_target?: number | null;
  talk_duration_minutes?: number | null;
  math_level?: string | null;
  include_speaker_notes?: boolean | null;
  include_limitations?: boolean | null;
  include_discussion_questions?: boolean | null;
  include_source_footers?: boolean | null;
  visual_preference?: string | null;
  sections_to_emphasize: string[];
  sections_to_reduce: string[];
  must_include: string[];
  avoid: string[];
  style_requirements: string[];
  special_requests: string[];
  unclear_requirements: string[];
  conflict_warnings: string[];
  compressed_summary: string;
};

export type PromptTemplate = {
  id: string;
  name: string;
  description: string;
  language: string;
  content: string;
  created_at: string;
  updated_at: string;
};
