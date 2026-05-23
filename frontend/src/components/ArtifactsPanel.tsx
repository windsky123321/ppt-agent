import { makeDownloadUrl } from "../api/client";
import type { ArtifactItem, ArtifactResponse, JobStatus } from "../types";

type Props = {
  job: JobStatus | null;
  artifacts: ArtifactResponse | null;
};

export function ArtifactsPanel({ job, artifacts }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold text-ink">Artifacts</h2>
          <p className="mt-2 text-sm text-slate-600">所有中间 JSON、长需求产物和最终 PPTX 都保存在本地，便于排查和复用。</p>
        </div>
        {job ? (
          <a className="rounded-2xl bg-accent px-4 py-3 text-sm font-semibold text-white no-underline transition hover:bg-blue-700" href={makeDownloadUrl(job.deck_id)}>
            下载 PPTX
          </a>
        ) : null}
      </div>
      {artifacts ? (
        <div className="mt-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          Deck 状态：{artifacts.deck_status}。Grounding warnings：{artifacts.grounding_status ?? 0}。Critic approved：
          {artifacts.critic_approval_status === null || artifacts.critic_approval_status === undefined ? "n/a" : artifacts.critic_approval_status ? "yes" : "no"}。
        </div>
      ) : null}
      <div className="mt-5 space-y-3">
        {(artifacts?.artifacts ?? job?.artifacts ?? []).map((artifact) => (
          <ArtifactRow key={artifact.name} artifact={artifact} />
        ))}
        {!job ? <p className="text-sm text-slate-500">还没有 artifacts。</p> : null}
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
            打开
          </a>
        ) : null}
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${artifact.exists ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>
          {artifact.exists ? "ready" : "missing"}
        </span>
      </div>
    </div>
  );
}
