import type { JobStatus } from "../types";

type Props = {
  loading: boolean;
  error: string;
  job: JobStatus | null;
  onGenerate: () => void;
  disabled: boolean;
};

export function StatusPanel({ loading, error, job, onGenerate, disabled }: Props) {
  return (
    <section className="rounded-3xl bg-ink p-6 text-white shadow-card">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-xl font-semibold">Progress</h2>
          <p className="mt-2 text-sm text-slate-300">
            {loading ? `Running stage: ${job?.current_stage ?? "starting"}.` : job?.message ?? "Ready to generate an editable PPTX deck."}
          </p>
        </div>
        <button
          className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-ink transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
          onClick={onGenerate}
          disabled={disabled}
        >
          {loading ? "Generating..." : "Generate Deck"}
        </button>
      </div>
      {job && (
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          <Stat label="Job ID" value={job.job_id} />
          <Stat label="Status" value={job.status} />
          <Stat label="Deck ID" value={job.deck_id} />
          <Stat label="Stage" value={job.current_stage ?? "ready"} />
        </div>
      )}
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
