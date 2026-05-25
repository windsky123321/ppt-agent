import { makeUsageExportUrl } from "../api/client";
import type { UsageSummary, UsageTaskDetail } from "../types";

type Props = {
  summary: UsageSummary | null;
  tasks: UsageTaskDetail[];
  onRefresh: () => Promise<void>;
  onClear: () => Promise<void>;
};

export function TokenUsagePanel({ summary, tasks, onRefresh, onClear }: Props) {
  return (
    <section className="rounded-lg bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Token 使用详情</h2>
          <p className="text-sm text-slate-600">仅记录统计信息，不记录完整 prompt、API Key 或 PDF 全文。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="rounded-md bg-slate-800 px-3 py-2 text-sm text-white" onClick={() => void onRefresh()}>
            刷新统计
          </button>
          <a className="rounded-md bg-white px-3 py-2 text-sm ring-1 ring-slate-300" href={makeUsageExportUrl("csv")}>
            导出 CSV
          </a>
          <a className="rounded-md bg-white px-3 py-2 text-sm ring-1 ring-slate-300" href={makeUsageExportUrl("json")}>
            导出 JSON
          </a>
          <button className="rounded-md bg-rose-50 px-3 py-2 text-sm text-rose-700 ring-1 ring-rose-200" onClick={() => void onClear()}>
            清空统计
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-4">
        <MetricCard label="总记录数" value={String(summary?.total_records ?? 0)} />
        <MetricCard label="总 Token" value={summary?.total_tokens == null ? "unknown" : String(summary.total_tokens)} />
        <MetricCard label="总请求数" value={String(summary?.total_request_count ?? 0)} />
        <MetricCard label="估算成本" value={summary?.total_estimated_cost == null ? "unknown" : `${summary.total_estimated_cost}`} />
      </div>
      <p className="mt-3 text-xs text-slate-500">该费用为估算，实际费用以服务商账单为准。</p>

      <div className="mt-6">
        <h3 className="font-medium">按任务查看</h3>
        <div className="mt-3 space-y-3">
          {tasks.length === 0 ? <p className="text-sm text-slate-500">暂无统计数据</p> : null}
          {tasks.map((task) => {
            const total = task.records.reduce((sum, item) => sum + (item.total_tokens ?? 0), 0);
            return (
              <div key={task.task_id} className="rounded-lg border border-slate-200 p-4">
                <div>
                  <strong>{task.task_id}</strong>
                  <p className="mt-1 text-sm text-slate-600">本次任务记录 {task.records.length} 条，汇总 Token：{total || "unknown"}</p>
                </div>
                <div className="mt-3 overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="text-slate-500">
                      <tr>
                        <th className="pb-2 pr-4">阶段</th>
                        <th className="pb-2 pr-4">模型</th>
                        <th className="pb-2 pr-4">输入 Token</th>
                        <th className="pb-2 pr-4">输出 Token</th>
                        <th className="pb-2 pr-4">总 Token</th>
                        <th className="pb-2 pr-4">模式</th>
                      </tr>
                    </thead>
                    <tbody>
                      {task.records.map((record, index) => (
                        <tr key={`${task.task_id}-${index}`} className="border-t border-slate-100">
                          <td className="py-2 pr-4">{record.stage || "未命名阶段"}</td>
                          <td className="py-2 pr-4">{record.model || "unknown"}</td>
                          <td className="py-2 pr-4">{record.prompt_tokens ?? "unknown"}</td>
                          <td className="py-2 pr-4">{record.completion_tokens ?? "unknown"}</td>
                          <td className="py-2 pr-4">{record.total_tokens ?? "unknown"}</td>
                          <td className="py-2 pr-4">{record.mock ? "Mock 模式" : record.mode}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-slate-50 p-4">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}
