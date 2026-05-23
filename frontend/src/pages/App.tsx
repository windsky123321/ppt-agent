import { useEffect, useState } from "react";

import {
  fetchArtifacts,
  fetchHealth,
  fetchJsonArtifact,
  fetchProfiles,
  fetchPromptTemplates,
  getModelConfig,
  parseInstruction,
  regenerateSlides,
  saveModelConfig,
  saveProfile,
  savePromptTemplate,
  testModelConfig,
  uploadPaper,
} from "../api/client";
import { ArtifactsPanel } from "../components/ArtifactsPanel";
import { InstructionStudioPanel } from "../components/InstructionStudioPanel";
import { ModelConfigPanel } from "../components/ModelConfigPanel";
import { OutlinePreview } from "../components/OutlinePreview";
import { ProfilePanel } from "../components/ProfilePanel";
import { RegeneratePanel } from "../components/RegeneratePanel";
import { SettingsPanel } from "../components/SettingsPanel";
import { StatusPanel } from "../components/StatusPanel";
import { UploadPanel } from "../components/UploadPanel";
import { WarningsPanel } from "../components/WarningsPanel";
import { useAppState } from "../stores/useAppState";
import type { CriticReport, GroundingReport, PromptTemplate, RuntimeModelConfig, RuntimeModelConfigView, UserProfile } from "../types";

type TabKey = "workspace" | "model" | "output" | "logs" | "about";

function createPromptTemplateFromInstruction(content: string): PromptTemplate {
  const now = new Date().toISOString();
  return {
    id: `prompt_${Math.random().toString(36).slice(2, 10)}`,
    name: `自定义模板 ${new Date().toLocaleString()}`,
    description: "由当前长需求保存而来。",
    language: /[\u4e00-\u9fff]/.test(content) ? "zh" : "en",
    content,
    created_at: now,
    updated_at: now,
  };
}

function mockPreset(): RuntimeModelConfig {
  return {
    llm_provider: "mock",
    llm_base_url: "",
    llm_api_key: "",
    llm_model: "gpt-5.5",
    fallback_llm_model: "gpt-4.1-mini",
    vision_provider: "mock",
    vision_base_url: "",
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
  };
}

function viewToConfig(view: RuntimeModelConfigView): RuntimeModelConfig {
  return {
    llm_provider: view.llm_provider,
    llm_base_url: view.llm_base_url,
    llm_api_key: "",
    llm_model: view.llm_model,
    fallback_llm_model: view.fallback_llm_model,
    vision_provider: view.vision_provider,
    vision_base_url: view.vision_base_url,
    vision_api_key: "",
    vision_model: view.vision_model,
    enable_vision: view.enable_vision,
    enable_critic: view.enable_critic,
    enable_repair: view.enable_repair,
    max_repair_loops: view.max_repair_loops,
    reasoning_effort: view.reasoning_effort,
    verbosity: view.verbosity,
    temperature: view.temperature,
    patch_mode: view.patch_mode,
    revision_max_output_tokens: view.revision_max_output_tokens,
    normal_max_output_tokens: view.normal_max_output_tokens,
    output_dir: view.output_dir,
  };
}

function hasSavedMaskedKey(masked: string | null | undefined): boolean {
  return Boolean(masked && masked.trim());
}

export function App() {
  const state = useAppState();
  const [activeTab, setActiveTab] = useState<TabKey>("workspace");

  useEffect(() => {
    Promise.allSettled([fetchHealth(), fetchProfiles(), fetchPromptTemplates(), getModelConfig()]).then((results) => {
      const [healthResult, profilesResult, templatesResult, modelResult] = results;

      if (healthResult.status === "fulfilled") {
        state.setBackendConnected(true);
        state.setHealth(healthResult.value);
      } else {
        state.setBackendConnected(false);
      }

      if (profilesResult.status === "fulfilled") {
        state.setProfiles(profilesResult.value);
        if (profilesResult.value[0] && !state.activeProfileId) {
          state.setActiveProfileId(profilesResult.value[0].id);
          state.setEditingProfile(profilesResult.value[0]);
        }
      }

      if (templatesResult.status === "fulfilled") {
        state.setPromptTemplates(templatesResult.value);
      }

      if (modelResult.status === "fulfilled") {
        state.setModelConfigView(modelResult.value);
        state.setModelConfig(viewToConfig(modelResult.value));
      }
    });
  }, []);

  async function refreshArtifacts(deckId: string) {
    const [artifacts, criticReport, groundingReport] = await Promise.all([
      fetchArtifacts(deckId),
      fetchJsonArtifact<CriticReport>(deckId, "critic_report.json").catch(() => null),
      fetchJsonArtifact<GroundingReport>(deckId, "grounding_report.json").catch(() => null),
    ]);
    state.setArtifacts(artifacts);
    state.setCriticReport(criticReport);
    state.setGroundingReport(groundingReport);
  }

  async function handleGenerate() {
    if (!state.backendConnected) {
      state.setError("后端未连接，请确认 PPT-Agent.exe 已启动，或查看 launcher 日志。");
      return;
    }
    if (!state.selectedFile) {
      state.setError("请先选择一篇 PDF 论文。");
      return;
    }
    if (!apiKeyReady) {
      state.setError("当前未配置可用模型。请前往“模型配置”填写 API Key，或切换到 Mock 模式后重试。");
      return;
    }

    state.setLoading(true);
    state.setError("");
    try {
      const result = await uploadPaper(state.selectedFile, state.settings, state.activeProfileId || undefined, state.deckMode);
      state.setResult(result);
      await refreshArtifacts(result.job.deck_id);
      state.setModelStatus(`生成完成：${result.job.deck_id}`);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "生成失败。请查看日志后重试。");
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
      state.setError(error instanceof Error ? error.message : "保存配置档失败。");
    }
  }

  async function handleRegenerateSlide() {
    if (!state.result?.job.deck_id) return;
    state.setLoading(true);
    state.setError("");
    try {
      const response = await regenerateSlides(
        state.result.job.deck_id,
        [state.regenSlideId],
        state.regenInstruction,
        state.activeProfileId || undefined,
        state.regenLongInstruction,
      );
      state.setResult((current) => (current ? { ...current, job: response.job } : current));
      await refreshArtifacts(state.result.job.deck_id);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "单页精修失败。");
    } finally {
      state.setLoading(false);
    }
  }

  async function handleSaveModelConfig() {
    try {
      const saved = await saveModelConfig(state.modelConfig);
      state.setModelConfigView(saved);
      state.setModelConfig(viewToConfig(saved));
      state.setModelStatus("模型配置已保存。");
      const health = await fetchHealth();
      state.setHealth(health);
      state.setBackendConnected(true);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "模型配置保存失败。");
    }
  }

  async function handleTestModelConfig() {
    try {
      const result = await testModelConfig(state.modelConfig);
      state.setModelStatus(result.message);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "模型连接测试失败。");
    }
  }

  async function handleParseInstruction() {
    if (!state.settings.long_instruction.trim()) {
      state.setError("请先输入长需求。");
      return;
    }
    try {
      const parsed = await parseInstruction(state.settings.long_instruction, state.settings.language);
      state.setParsedInstruction(parsed);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "需求解析失败。");
    }
  }

  async function handleSavePromptTemplate() {
    if (!state.settings.long_instruction.trim()) {
      state.setError("当前没有可保存的长需求模板。");
      return;
    }
    try {
      await savePromptTemplate(createPromptTemplateFromInstruction(state.settings.long_instruction));
      const templates = await fetchPromptTemplates();
      state.setPromptTemplates(templates);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "保存需求模板失败。");
    }
  }

  const activeProfileName = state.profiles.find((profile) => profile.id === state.activeProfileId)?.name ?? "";
  const llmNeedsKey = state.modelConfig.llm_provider !== "mock";
  const apiKeyReady = !llmNeedsKey || Boolean(state.modelConfig.llm_api_key.trim() || hasSavedMaskedKey(state.modelConfigView?.llm_api_key_masked));
  const canGenerate = state.backendConnected && Boolean(state.selectedFile) && apiKeyReady && !state.loading;
  const generateHint = !state.backendConnected
    ? "请先双击运行 PPT-Agent.exe，确认浏览器已自动打开。"
    : !apiKeyReady
      ? "第一步：去“模型配置”填写 API Key；如果只是验收流程，可直接切换到 Mock 模式。"
      : !state.selectedFile
        ? "第二步：上传论文 PDF。"
        : "第三步：检查模板与设置，然后点击“生成 PPT”。生成完成后可在右侧下载结果。";

  return (
    <main className="min-h-screen bg-[#f6f7fb] px-4 py-6 text-ink md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-5 border-b border-slate-200 pb-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-normal">PPT 智能体</h1>
              <p className="mt-1 text-sm text-slate-600">上传论文 PDF，生成可编辑的专业中文或双语汇报 PPT。</p>
            </div>
            <div className="rounded-md bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">
              {state.backendConnected ? "服务已连接" : "服务未连接"}
            </div>
          </div>
          <nav className="mt-4 flex flex-wrap gap-2">
            <TabButton active={activeTab === "workspace"} onClick={() => setActiveTab("workspace")} label="工作台" />
            <TabButton active={activeTab === "model"} onClick={() => setActiveTab("model")} label="模型配置" />
            <TabButton active={activeTab === "output"} onClick={() => setActiveTab("output")} label="输出目录" />
            <TabButton active={activeTab === "logs"} onClick={() => setActiveTab("logs")} label="日志" />
            <TabButton active={activeTab === "about"} onClick={() => setActiveTab("about")} label="关于" />
          </nav>
        </header>

        {activeTab === "workspace" ? (
          <>
            <QuickStartPanel />
            <div className="mt-5 grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
              <div className="space-y-5">
                <StatusPanel
                  loading={state.loading}
                  error={state.error}
                  job={state.result?.job ?? null}
                  health={state.health}
                  backendConnected={state.backendConnected}
                  modelStatus={state.modelStatus}
                  profileName={activeProfileName}
                  deckMode={state.deckMode}
                  hasLongInstruction={Boolean(state.settings.long_instruction.trim())}
                  onGenerate={handleGenerate}
                  disabled={!canGenerate}
                  generateHint={generateHint}
                  apiKeyReady={apiKeyReady}
                />
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
                <SettingsPanel settings={state.settings} deckMode={state.deckMode} onDeckModeChange={state.setDeckMode} onChange={state.setSettings} />
                <InstructionStudioPanel
                  longInstruction={state.settings.long_instruction}
                  parsedInstruction={state.parsedInstruction}
                  promptTemplates={state.promptTemplates}
                  selectedTemplateId={state.selectedTemplateId}
                  onInstructionChange={(value) => state.setSettings({ ...state.settings, long_instruction: value })}
                  onTemplateSelect={(templateId) => {
                    state.setSelectedTemplateId(templateId);
                    const template = state.promptTemplates.find((item) => item.id === templateId);
                    if (template) state.setSettings({ ...state.settings, long_instruction: template.content });
                  }}
                  onParse={handleParseInstruction}
                  onClear={() => {
                    state.setSettings({ ...state.settings, long_instruction: "" });
                    state.setParsedInstruction(null);
                  }}
                  onSaveTemplate={handleSavePromptTemplate}
                  onUseExample={() => {
                    const example = state.promptTemplates[0];
                    if (example) {
                      state.setSelectedTemplateId(example.id);
                      state.setSettings({ ...state.settings, long_instruction: example.content });
                    }
                  }}
                />
                <RegeneratePanel
                  deckId={state.result?.job.deck_id ?? null}
                  slideId={state.regenSlideId}
                  instruction={state.regenInstruction}
                  longInstruction={state.regenLongInstruction}
                  onSlideIdChange={state.setRegenSlideId}
                  onInstructionChange={state.setRegenInstruction}
                  onLongInstructionChange={state.setRegenLongInstruction}
                  onRegenerate={handleRegenerateSlide}
                  disabled={state.loading}
                />
              </div>

              <div className="space-y-5">
                <ArtifactsPanel job={state.result?.job ?? null} artifacts={state.artifacts} />
                <WarningsPanel criticReport={state.criticReport} groundingReport={state.groundingReport} />
                <OutlinePreview parsedPaper={state.result?.parsed_paper ?? null} />
              </div>
            </div>
          </>
        ) : null}

        {activeTab === "model" ? (
          <ModelConfigPanel
            config={state.modelConfig}
            savedView={state.modelConfigView}
            status={state.modelStatus}
            onChange={state.setModelConfig}
            onSave={handleSaveModelConfig}
            onTest={handleTestModelConfig}
            onUseMock={() => {
              state.setModelConfig(mockPreset());
              state.setModelStatus("已切换到 Mock 模式。");
            }}
          />
        ) : null}

        {activeTab === "output" ? (
          <InfoPanel
            title="输出目录"
            rows={[
              "默认输出目录：storage/decks",
              `当前配置：${state.modelConfig.output_dir}`,
              "每次生成都会保存 PPTX 和中间 JSON。",
              "如果你找不到结果，请先查看右侧“生成结果”里的 final_deck.pptx 路径。",
            ]}
          />
        ) : null}

        {activeTab === "logs" ? (
          <InfoPanel
            title="日志"
            rows={[
              "启动日志：logs/launcher.log",
              "后端日志：logs/backend.log",
              "前端日志：logs/frontend.log",
              "如果启动或生成失败，请先查看 launcher.log 和 backend.log。",
            ]}
          />
        ) : null}

        {activeTab === "about" ? (
          <InfoPanel
            title="关于"
            rows={[
              "PPT 智能体 Windows 发布候选版",
              "默认启用 High-Quality Low-Token Mode",
              "默认模型：gpt-5.5；fallback：gpt-4.1-mini",
              "Mock 模式无需 API Key，可用于首轮验收和回归测试",
            ]}
          />
        ) : null}
      </div>
    </main>
  );
}

function QuickStartPanel() {
  const steps = [
    "第一步：去“模型配置”填写 API Key，或切换到 Mock 模式。",
    "第二步：上传论文 PDF。",
    "第三步：选择模板、Deck 模式和输出设置。",
    "第四步：点击“生成 PPT”等待完成。",
    "第五步：在右侧下载 PPT 或查看产物路径。",
  ];
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">首次使用指引</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-5">
        {steps.map((step) => (
          <div key={step} className="rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
            {step}
          </div>
        ))}
      </div>
    </section>
  );
}

function TabButton({ active, label, onClick }: { active: boolean; label: string; onClick: () => void }) {
  return (
    <button className={`rounded-md px-3 py-2 text-sm font-medium ${active ? "bg-accent text-white" : "bg-white text-slate-700 ring-1 ring-slate-200"}`} onClick={onClick}>
      {label}
    </button>
  );
}

function InfoPanel({ title, rows }: { title: string; rows: string[] }) {
  return (
    <section className="rounded-lg bg-white p-5 shadow-card">
      <h2 className="text-lg font-semibold">{title}</h2>
      <div className="mt-4 space-y-2">
        {rows.map((row) => (
          <p key={row} className="rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">
            {row}
          </p>
        ))}
      </div>
    </section>
  );
}
