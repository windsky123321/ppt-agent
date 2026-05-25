import type { HealthStatus, JobStatus } from "../types";
import { deckModeLabels, labelFor, stageLabels, statusLabels } from "../utils/labels";

type Props = {
  loading: boolean;
  error: string;
  job: JobStatus | null;
  health: HealthStatus | null;
  backendConnected: boolean;
  modelStatus: string;
  profileName: string;
  deckMode: string;
  hasLongInstruction: boolean;
  onGenerate: () => void;
  disabled: boolean;
  generateHint: string;
  apiKeyReady: boolean;
  isMockMode: boolean;
};

export function StatusPanel({
  loading,
  error,
  job,
  health,
  backendConnected,
  modelStatus,
  profileName,
  deckMode,
  hasLongInstruction,
  onGenerate,
  disabled,
  generateHint,
  apiKeyReady,
  isMockMode,
}: Props) {
  const statusText = job?.mock_mode ? "模拟生成完成" : labelFor(statusLabels, job?.status ?? "idle");
  const statusMessage = loading
    ? `当前阶段：${labelFor(stageLabels, job?.current_stage ?? "ready")}`
    : job?.mock_mode
      ? "模拟生成完成，可用于检查上传、生成和下载流程。"
      : job?.delivery_ready === false
        ? "生成完成，但质量检查未通过，建议继续精修后再使用。"
        : job?.message ?? "准备生成可编辑 PPTX。";

  return (
    <section className="rounded-3xl bg-ink p-6 text-white shadow-card">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">当前状态</h2>
          <p className="mt-2 text-sm text-slate-300">{statusMessage}</p>
        </div>
        <button
          className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={onGenerate}
          disabled={disabled}
        >
          {loading ? "生成中..." : "生成 PPT"}
        </button>
      </div>

      {isMockMode ? (
        <div className="mt-4 rounded-2xl bg-amber-400/20 px-4 py-3 text-sm text-amber-100">
          当前为 Mock 模式，仅用于流程测试，生成内容不是正式质量。
        </div>
      ) : null}

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Stat label="后端连接" value={backendConnected ? "已连接" : "未连接"} />
        <Stat label="模型状态" value={modelStatus || (apiKeyReady ? "可开始生成" : "请先配置 API Key 或切换到 Mock")} />
        <Stat label="当前配置档" value={profileName || "未选择"} />
        <Stat label="汇报模式" value={labelFor(deckModeLabels, deckMode)} />
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Stat label="任务 ID" value={job?.job_id ?? "-"} />
        <Stat label="任务状态" value={statusText} />
        <Stat label="处理阶段" value={labelFor(stageLabels, job?.current_stage ?? "ready")} />
        <Stat label="长需求" value={hasLongInstruction ? "已提供" : "未提供"} />
      </div>

      <div className="mt-4 rounded-2xl bg-white/10 px-4 py-3 text-sm text-slate-100">{generateHint}</div>

      {!backendConnected ? (
        <p className="mt-4 rounded-2xl bg-red-500/20 px-4 py-3 text-sm text-red-100">
          后端未连接。请重新双击运行 PPT-Agent.exe，或查看 `logs/launcher.log`。
        </p>
      ) : null}

      {health && !health.llm_configured && !isMockMode ? (
        <p className="mt-4 rounded-2xl bg-amber-400/20 px-4 py-3 text-sm text-amber-100">
          请先在模型配置中填写 API Key，或切换到 Mock 模式进行流程测试。
        </p>
      ) : null}

      {error ? <p className="mt-4 rounded-2xl bg-red-500/20 px-4 py-3 text-sm text-red-100">{error}</p> : null}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-white/10 px-4 py-3">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-300">{label}</div>
      <div className="mt-1 break-all text-sm font-medium text-white">{value}</div>
    </div>
  );
}
