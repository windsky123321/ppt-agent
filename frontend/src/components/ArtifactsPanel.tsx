import { makeDownloadUrl } from "../api/client";
import type { ArtifactItem, ArtifactResponse, JobStatus } from "../types";
import { labelFor, statusLabels } from "../utils/labels";

type Props = {
  job: JobStatus | null;
  artifacts: ArtifactResponse | null;
  onContinueRefine?: () => void;
};

export function ArtifactsPanel({ job, artifacts, onContinueRefine }: Props) {
  const rows = artifacts?.artifacts ?? job?.artifacts ?? [];
  const isMock = Boolean(job?.mock_mode || artifacts?.mock_mode);
  const deliveryReady = Boolean(job?.delivery_ready ?? artifacts?.delivery_ready);
  const downloadLabel = isMock ? "下载测试文件" : deliveryReady ? "下载 PPT" : "下载草稿 PPT";

  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink">生成结果</h2>
          <p className="mt-2 text-sm text-slate-600">这里展示 PPT、质量报告和中间产物。若质量未通过，请优先继续精修。</p>
        </div>
        {job ? (
          <div className="flex flex-wrap gap-2">
            <a
              className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white no-underline transition hover:bg-blue-700"
              href={makeDownloadUrl(job.deck_id)}
            >
              {downloadLabel}
            </a>
            {!deliveryReady ? (
              <button className="rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-ink ring-1 ring-slate-200" onClick={onContinueRefine}>
                继续精修
              </button>
            ) : null}
          </div>
        ) : null}
      </div>

      {artifacts ? (
        <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          任务状态：{job?.mock_mode ? "模拟生成完成" : labelFor(statusLabels, artifacts.deck_status)}；质量状态：
          {artifacts.quality_status === "failed"
            ? "未通过"
            : artifacts.quality_status === "mock"
              ? "仅流程测试"
              : "已通过"}
          ；Critic 审核：
          {artifacts.critic_approval_status === null || artifacts.critic_approval_status === undefined
            ? "未提供"
            : artifacts.critic_approval_status
              ? "通过"
              : "未通过"}
        </div>
      ) : null}

      {!deliveryReady && job ? (
        <div className="mt-4 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {isMock
            ? "当前为 Mock 模式，仅用于流程测试。生成的 PPT 仅用于检查上传、生成和下载流程。"
            : "生成完成，但质量检查未通过，建议继续精修后再用于正式汇报。"}
        </div>
      ) : null}

      <div className="mt-5 space-y-3">
        {rows.map((artifact) => (
          <ArtifactRow key={artifact.name} artifact={artifact} isMock={isMock} />
        ))}
        {!job ? <p className="text-sm text-slate-500">还没有生成结果。请先上传 PDF 并点击“生成 PPT”。</p> : null}
      </div>
    </section>
  );
}

function ArtifactRow({ artifact, isMock }: { artifact: ArtifactItem; isMock: boolean }) {
  const isDownloadable = artifact.download_url && (artifact.name.endsWith(".pptx") || artifact.name.endsWith(".json") || artifact.name.endsWith(".md"));
  return (
    <div className="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3">
      <div>
        <div className="font-medium text-ink">
          {artifact.name}
          {isMock && artifact.name.endsWith(".pptx") ? <span className="ml-2 text-xs text-amber-700">测试文件</span> : null}
        </div>
        <div className="text-xs text-slate-500">{artifact.path}</div>
      </div>
      <div className="flex items-center gap-3">
        {isDownloadable ? (
          <a className="text-xs font-medium text-accent no-underline" href={artifact.download_url ?? "#"}>
            下载
          </a>
        ) : null}
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${artifact.exists ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
          {artifact.exists ? "已生成" : "未生成"}
        </span>
      </div>
    </div>
  );
}
