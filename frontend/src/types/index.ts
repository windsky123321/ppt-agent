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
