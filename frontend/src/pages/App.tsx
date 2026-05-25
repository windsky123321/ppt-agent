import { useEffect, useState } from "react";

import {
  clearUsage,
  deleteSkill,
  disableSkill,
  enableSkill,
  fetchArtifacts,
  fetchHealth,
  fetchJsonArtifact,
  fetchProfiles,
  fetchPromptTemplates,
  fetchSkills,
  fetchUsageSummary,
  fetchUsageTasks,
  getModelConfig,
  importSkill,
  parseInstruction,
  regenerateSlides,
  saveModelConfig,
  saveProfile,
  savePromptTemplate,
  searchSkills,
  testModelConfig,
  testSkill,
  uploadPaper,
} from "../api/client";
import { ArtifactsPanel } from "../components/ArtifactsPanel";
import { InstructionStudioPanel } from "../components/InstructionStudioPanel";
import { ModelConfigPanel } from "../components/ModelConfigPanel";
import { OutlinePreview } from "../components/OutlinePreview";
import { ProfilePanel } from "../components/ProfilePanel";
import { RegeneratePanel } from "../components/RegeneratePanel";
import { SettingsPanel } from "../components/SettingsPanel";
import { SkillLibraryPanel } from "../components/SkillLibraryPanel";
import { StatusPanel } from "../components/StatusPanel";
import { TokenUsagePanel } from "../components/TokenUsagePanel";
import { UploadPanel } from "../components/UploadPanel";
import { WarningsPanel } from "../components/WarningsPanel";
import { useAppState } from "../stores/useAppState";
import type { CriticReport, GroundingReport, PromptTemplate, RuntimeModelConfig, RuntimeModelConfigView, UserProfile } from "../types";

type TabKey = "workspace" | "model" | "skills" | "usage" | "output" | "logs" | "about";

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
    skills_enabled: true,
    auto_select_skills: true,
    max_skills_per_task: 3,
    max_skill_context_tokens: 800,
    allow_skill_scripts: false,
    allowed_skill_risk_level: "low",
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
    skills_enabled: view.skills_enabled,
    auto_select_skills: view.auto_select_skills,
    max_skills_per_task: view.max_skills_per_task,
    max_skill_context_tokens: view.max_skill_context_tokens,
    allow_skill_scripts: view.allow_skill_scripts,
    allowed_skill_risk_level: view.allowed_skill_risk_level,
  };
}

function hasSavedMaskedKey(masked: string | null | undefined): boolean {
  return Boolean(masked && masked.trim());
}

export function App() {
  const state = useAppState();
  const [activeTab, setActiveTab] = useState<TabKey>("workspace");

  useEffect(() => {
    Promise.allSettled([
      fetchHealth(),
      fetchProfiles(),
      fetchPromptTemplates(),
      getModelConfig(),
      fetchSkills(),
      fetchUsageSummary(),
      fetchUsageTasks(),
    ]).then((results) => {
      const [healthResult, profilesResult, templatesResult, modelResult, skillsResult, usageSummaryResult, usageTasksResult] = results;

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

      if (skillsResult.status === "fulfilled") {
        state.setSkills(skillsResult.value);
      }

      if (usageSummaryResult.status === "fulfilled") {
        state.setUsageSummary(usageSummaryResult.value);
      }

      if (usageTasksResult.status === "fulfilled") {
        state.setUsageTasks(usageTasksResult.value);
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

  async function refreshUsage() {
    const [summary, tasks] = await Promise.all([fetchUsageSummary(), fetchUsageTasks()]);
    state.setUsageSummary(summary);
    state.setUsageTasks(tasks);
  }

  async function refreshSkills() {
    state.setSkills(await fetchSkills());
  }

  const activeProfileName = state.profiles.find((profile) => profile.id === state.activeProfileId)?.name ?? "";
  const isMockMode = state.modelConfig.llm_provider === "mock" || state.modelConfig.vision_provider === "mock";
  const llmNeedsKey = state.modelConfig.llm_provider !== "mock";
  const apiKeyReady = !llmNeedsKey || Boolean(state.modelConfig.llm_api_key.trim() || hasSavedMaskedKey(state.modelConfigView?.llm_api_key_masked));
  const canGenerate = state.backendConnected && Boolean(state.selectedFile) && apiKeyReady && !state.loading;
  const generateHint = !state.backendConnected
    ? "请先双击运行 PPT-Agent.exe，并确认浏览器已自动打开。"
    : !apiKeyReady
      ? "请先在模型配置中填写 API Key，或切换到 Mock 模式进行流程测试。"
      : !state.selectedFile
        ? "请先上传论文 PDF。"
        : "检查模板与设置后点击“生成 PPT”。如果质量检查未通过，系统会提示继续精修。";

  async function handleGenerate() {
    if (!state.backendConnected) {
      state.setError("后端未连接，请先启动 PPT-Agent.exe。");
      return;
    }
    if (!state.selectedFile) {
      state.setError("请先选择一篇 PDF 论文。");
      return;
    }
    if (!apiKeyReady) {
      state.setError("请先在模型配置中填写 API Key，或切换到 Mock 模式进行流程测试。");
      return;
    }

    state.setLoading(true);
    state.setError("");
    try {
      const result = await uploadPaper(state.selectedFile, state.settings, state.activeProfileId || undefined, state.deckMode);
      state.setResult(result);
      await Promise.all([refreshArtifacts(result.job.deck_id), refreshUsage()]);
      state.setModelStatus(result.job.mock_mode ? `模拟生成完成：${result.job.deck_id}` : `生成完成：${result.job.deck_id}`);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "生成失败，请查看日志后重试。");
    } finally {
      state.setLoading(false);
    }
  }

  async function handleSaveProfile() {
    if (!state.editingProfile) {
      return;
    }
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
    if (!state.result?.job.deck_id) {
      return;
    }
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
      await Promise.all([refreshArtifacts(state.result.job.deck_id), refreshUsage()]);
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
      state.setPromptTemplates(await fetchPromptTemplates());
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "保存需求模板失败。");
    }
  }

  async function handleSearchSkills(keyword: string) {
    try {
      const results = await searchSkills({ keyword, tags: [], capabilities: [] });
      state.setSkillSearchResults(results);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "搜索技能失败。");
    }
  }

  async function handleImportZip(file: File) {
    try {
      const formData = new FormData();
      formData.append("file", file);
      const result = await importSkill(formData);
      await refreshSkills();
      state.setModelStatus(`技能已导入：${result.skill.name}`);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "导入技能失败。");
    }
  }

  async function handleImportFolder(folderPath: string) {
    try {
      const formData = new FormData();
      formData.append("folder_path", folderPath);
      const result = await importSkill(formData);
      await refreshSkills();
      state.setModelStatus(`技能已导入：${result.skill.name}`);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "导入技能失败。");
    }
  }

  async function handleImportUrl(url: string) {
    try {
      const formData = new FormData();
      if (url.includes("github.com")) {
        formData.append("github_repo", url);
      } else {
        formData.append("source_url", url);
      }
      const result = await importSkill(formData);
      await refreshSkills();
      state.setModelStatus(`技能已导入：${result.skill.name}`);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "导入技能失败。");
    }
  }

  async function handleToggleSkill(skillId: string, enabled: boolean) {
    try {
      if (enabled) {
        await disableSkill(skillId);
      } else {
        await enableSkill(skillId);
      }
      await refreshSkills();
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "更新技能状态失败。");
    }
  }

  async function handleDeleteSkill(skillId: string) {
    try {
      await deleteSkill(skillId);
      await refreshSkills();
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "删除技能失败。");
    }
  }

  async function handleTestSkill(skillId: string) {
    try {
      const result = await testSkill(skillId);
      state.setModelStatus(result.message);
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "测试技能失败。");
    }
  }

  async function handleClearUsage() {
    try {
      await clearUsage();
      await refreshUsage();
    } catch (error) {
      state.setError(error instanceof Error ? error.message : "清空统计失败。");
    }
  }

  return (
    <main className="min-h-screen bg-[#f6f7fb] px-4 py-6 text-ink md:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-5 border-b border-slate-200 pb-4">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-semibold tracking-normal">PPT Agent v0.2.0-dev</h1>
              <p className="mt-1 text-sm text-slate-600">上传 PDF，生成中文 PPT，并管理技能库与 Token 使用详情。</p>
            </div>
            <div className="rounded-md bg-white px-3 py-2 text-sm text-slate-700 shadow-sm">{state.backendConnected ? "服务已连接" : "服务未连接"}</div>
          </div>
          <nav className="mt-4 flex flex-wrap gap-2">
            <TabButton active={activeTab === "workspace"} onClick={() => setActiveTab("workspace")} label="工作台" />
            <TabButton active={activeTab === "model"} onClick={() => setActiveTab("model")} label="模型配置" />
            <TabButton active={activeTab === "skills"} onClick={() => setActiveTab("skills")} label="技能库" />
            <TabButton active={activeTab === "usage"} onClick={() => setActiveTab("usage")} label="Token 使用详情" />
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
                  isMockMode={isMockMode}
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
                    if (template) {
                      state.setSettings({ ...state.settings, long_instruction: template.content });
                    }
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
                <ArtifactsPanel job={state.result?.job ?? null} artifacts={state.artifacts} onContinueRefine={() => setActiveTab("workspace")} />
                <WarningsPanel criticReport={state.criticReport} groundingReport={state.groundingReport} />
                <OutlinePreview parsedPaper={state.result?.parsed_paper ?? null} paperSummary={state.result?.paper_summary ?? null} targetLanguage={state.settings.language} />
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

        {activeTab === "skills" ? (
          <SkillLibraryPanel
            installedSkills={state.skills}
            searchResults={state.skillSearchResults}
            onSearch={handleSearchSkills}
            onImportZip={handleImportZip}
            onImportFolder={handleImportFolder}
            onImportUrl={handleImportUrl}
            onEnable={(skillId) => handleToggleSkill(skillId, false)}
            onDisable={(skillId) => handleToggleSkill(skillId, true)}
            onDelete={handleDeleteSkill}
            onTest={handleTestSkill}
          />
        ) : null}

        {activeTab === "usage" ? <TokenUsagePanel summary={state.usageSummary} tasks={state.usageTasks} onRefresh={refreshUsage} onClear={handleClearUsage} /> : null}

        {activeTab === "output" ? (
          <InfoPanel
            title="输出目录"
            rows={[
              "默认输出目录：storage/decks",
              `当前配置：${state.modelConfig.output_dir}`,
              "质量通过时会生成 final_deck.pptx；未通过时只保留 draft_deck.pptx。",
              "如需继续精修，请查看 quality_report.json 中的 Critic 结果。",
            ]}
          />
        ) : null}

        {activeTab === "logs" ? (
          <InfoPanel
            title="日志"
            rows={[
              "启动日志：logs/launcher.log",
              "后端日志：logs/backend.log",
              "质量报告：storage/decks/<job_id>/quality_report.json",
              "如果启动或生成失败，请优先查看 launcher.log、backend.log 和 quality_report.json。",
            ]}
          />
        ) : null}

        {activeTab === "about" ? (
          <InfoPanel
            title="关于"
            rows={[
              "PPT Agent 当前开发版本：v0.2.0-dev",
              "Mock 模式仅用于测试上传、生成、下载流程。",
              "正式生成前请先配置 API Key，并确认质量检查已通过。",
              "如果结果仍不满意，请使用继续精修或 Round 2 / Round 3 功能。",
            ]}
          />
        ) : null}
      </div>
    </main>
  );
}

function QuickStartPanel() {
  const steps = [
    "第一步：在模型配置中填写 API Key，或切换到 Mock 模式测试流程。",
    "第二步：上传论文 PDF。",
    "第三步：选择汇报模式、主题和输出设置。",
    "第四步：点击“生成 PPT”并等待完成。",
    "第五步：质量通过后下载正式 PPT；未通过时先继续精修。",
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
