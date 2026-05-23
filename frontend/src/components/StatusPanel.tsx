import type { HealthStatus, JobStatus } from "../types";

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
}: Props) {
  return (
    <section className="rounded-3xl bg-ink p-6 text-white shadow-card">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">当前状态</h2>
          <p className="mt-2 text-sm text-slate-300">
            {loading ? `当前阶段：${job?.current_stage ?? "正在准备"}` : job?.message ?? "准备生成可编辑 PPTX。"}
          </p>
        </div>
        <button
          className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={onGenerate}
          disabled={disabled}
        >
          {loading ? "生成中..." : "生成 PPT"}
        </button>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Stat label="后端连接" value={backendConnected ? "已连接" : "未连接"} />
        <Stat label="模型状态" value={modelStatus || (apiKeyReady ? "可直接生成" : "请先配置 API Key 或切换 Mock")} />
        <Stat label="当前配置档" value={profileName || "未选择"} />
        <Stat label="Deck 模式" value={deckMode} />
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Stat label="Job ID" value={job?.job_id ?? "-"} />
        <Stat label="任务状态" value={job?.status ?? "idle"} />
        <Stat label="处理阶段" value={job?.current_stage ?? "ready"} />
        <Stat label="长需求" value={hasLongInstruction ? "已提供" : "未提供"} />
      </div>

      <div className="mt-4 rounded-2xl bg-white/10 px-4 py-3 text-sm text-slate-100">
        {generateHint}
      </div>

      {!backendConnected ? (
        <p className="mt-4 rounded-2xl bg-red-500/20 px-4 py-3 text-sm text-red-100">
          后端未连接。请重新双击运行 PPT-Agent.exe，或查看 `logs/launcher.log`。
        </p>
      ) : null}

      {health && !health.llm_configured ? (
        <p className="mt-4 rounded-2xl bg-amber-400/20 px-4 py-3 text-sm text-amber-100">
          当前未检测到可用 API Key。你可以去“模型配置”填写 API Key，或直接切换到 Mock 模式完成首轮验收。
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
