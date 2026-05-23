import type { CriticReport, GroundingReport } from "../types";

type Props = {
  criticReport: CriticReport | null;
  groundingReport: GroundingReport | null;
};

export function WarningsPanel({ criticReport, groundingReport }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">Critic 与 Grounding</h2>
      <div className="mt-4 space-y-3">
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <div className="text-sm font-semibold text-ink">Critic 结果</div>
          <p className="mt-1 text-sm text-slate-600">
            {criticReport ? `${criticReport.summary} Score: ${criticReport.deck_score}。Approved: ${criticReport.approved ? "yes" : "no"}。` : "尚未生成 critic 报告。"}
          </p>
        </div>
        {criticReport?.issues.slice(0, 6).map((issue) => (
          <div key={`${issue.slide_id}-${issue.description}`} className="rounded-2xl border border-slate-200 px-4 py-3">
            <div className="text-sm font-semibold text-ink">
              {issue.slide_id} | {issue.severity} | {issue.category}
            </div>
            <p className="mt-1 text-sm text-slate-600">{issue.description}</p>
            <p className="mt-1 text-xs text-slate-500">{issue.suggested_fix}</p>
          </div>
        ))}
        <div className="rounded-2xl bg-slate-50 px-4 py-3">
          <div className="text-sm font-semibold text-ink">Grounding 警告</div>
          {groundingReport?.warnings.length ? (
            groundingReport.warnings.slice(0, 6).map((warning) => (
              <p key={`${warning.slide_id}-${warning.message}`} className="mt-2 text-sm text-slate-600">
                {warning.slide_id}: {warning.message}
              </p>
            ))
          ) : (
            <p className="mt-1 text-sm text-slate-600">当前没有 grounding 警告。</p>
          )}
        </div>
      </div>
    </section>
  );
}
