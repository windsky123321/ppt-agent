import { makeDownloadUrl } from "../api/client";
import type { ArtifactItem, ArtifactResponse, JobStatus } from "../types";

type Props = {
  job: JobStatus | null;
  artifacts: ArtifactResponse | null;
};

export function ArtifactsPanel({ job, artifacts }: Props) {
  const rows = artifacts?.artifacts ?? job?.artifacts ?? [];

  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink">生成结果</h2>
          <p className="mt-2 text-sm text-slate-600">这里会显示最终 PPT、关键 JSON 产物和当前任务的输出路径。</p>
        </div>
        {job ? (
          <a className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white no-underline transition hover:bg-blue-700" href={makeDownloadUrl(job.deck_id)}>
            下载 PPT
          </a>
        ) : null}
      </div>

      {artifacts ? (
        <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          Deck 状态：{artifacts.deck_status}；Grounding 警告：{artifacts.grounding_status ?? 0}；Critic 审核：
          {artifacts.critic_approval_status === null || artifacts.critic_approval_status === undefined
            ? "未提供"
            : artifacts.critic_approval_status
              ? "通过"
              : "未通过"}
        </div>
      ) : null}

      <div className="mt-5 space-y-3">
        {rows.map((artifact) => (
          <ArtifactRow key={artifact.name} artifact={artifact} />
        ))}
        {!job ? <p className="text-sm text-slate-500">还没有生成结果。请先上传 PDF 并点击“生成 PPT”。</p> : null}
      </div>
    </section>
  );
}

function ArtifactRow({ artifact }: { artifact: ArtifactItem }) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3">
      <div>
        <div className="font-medium text-ink">{artifact.name}</div>
        <div className="text-xs text-slate-500">{artifact.path}</div>
      </div>
      <div className="flex items-center gap-3">
        {artifact.download_url ? (
          <a className="text-xs font-medium text-accent no-underline" href={artifact.download_url}>
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
