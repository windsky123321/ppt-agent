type Props = {
  deckId: string | null;
  slideId: string;
  instruction: string;
  longInstruction: string;
  onSlideIdChange: (value: string) => void;
  onInstructionChange: (value: string) => void;
  onLongInstructionChange: (value: string) => void;
  onRegenerate: () => void;
  disabled: boolean;
};

export function RegeneratePanel({
  deckId,
  slideId,
  instruction,
  longInstruction,
  onSlideIdChange,
  onInstructionChange,
  onLongInstructionChange,
  onRegenerate,
  disabled,
}: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">单页重生成</h2>
      <p className="mt-2 text-sm text-slate-600">只改选中的一页，同时保留当前 deck、来源引用和其余页内容。</p>
      <div className="mt-4 grid gap-4">
        <label className="text-sm text-slate-700">
          Slide ID
          <input className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={slideId} onChange={(event) => onSlideIdChange(event.target.value)} placeholder="slide_05" />
        </label>
        <label className="text-sm text-slate-700">
          短指令
          <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={instruction} onChange={(event) => onInstructionChange(event.target.value)} placeholder="Make this slide more visual and reduce text." />
        </label>
        <label className="text-sm text-slate-700">
          可选长需求
          <textarea className="mt-2 min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2" value={longInstruction} onChange={(event) => onLongInstructionChange(event.target.value)} placeholder="只对当前页生效的补充风格要求，例如：请更像组会讲法，少一点字，多用图表。" />
        </label>
      </div>
      <button className="mt-4 rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-50" onClick={onRegenerate} disabled={disabled || !deckId}>
        Regenerate This Slide
      </button>
    </section>
  );
}
