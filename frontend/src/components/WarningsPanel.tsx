import type { CriticReport, GroundingReport } from "../types";

type Props = {
  criticReport: CriticReport | null;
  groundingReport: GroundingReport | null;
};

export function WarningsPanel({ criticReport, groundingReport }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">质量检查</h2>
      <div className="mt-4 space-y-3">
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <div className="text-sm font-semibold text-ink">Critic 结果</div>
          <p className="mt-1 text-sm text-slate-600">
            {criticReport
              ? `${criticReport.zh_summary ?? criticReport.summary}；评分：${criticReport.deck_score}；审核：${criticReport.approved ? "通过" : "未通过"}`
              : "尚未生成质量检查报告。"}
          </p>
        </div>
        {criticReport?.issues.slice(0, 6).map((issue) => (
          <div key={`${issue.slide_id}-${issue.description}`} className="rounded-2xl border border-slate-200 px-4 py-3">
            <div className="text-sm font-semibold text-ink">
              {issue.slide_id} | {issue.severity} | {issue.category}
            </div>
            <p className="mt-1 text-sm text-slate-600">{issue.zh_message || issue.description}</p>
            <p className="mt-1 text-xs text-slate-500">{issue.suggested_fix}</p>
          </div>
        ))}
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <div className="text-sm font-semibold text-ink">来源依据检查</div>
          {groundingReport?.warnings.length ? (
            groundingReport.warnings.slice(0, 6).map((warning) => (
              <p key={`${warning.slide_id}-${warning.message}`} className="mt-2 text-sm text-slate-600">
                {warning.slide_id}: {warning.zh_message || warning.message}
              </p>
            ))
          ) : (
            <p className="mt-1 text-sm text-slate-600">当前没有来源依据警告。</p>
          )}
        </div>
      </div>
    </section>
  );
}
