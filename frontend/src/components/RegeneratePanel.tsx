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
      <h2 className="text-xl font-semibold text-ink">Round 2 / Round 3 精修</h2>
      <p className="mt-2 text-sm text-slate-600">只修改指定页面，保留当前 deck 结构、其余页面和已有产物。</p>
      <div className="mt-4 grid gap-4">
        <label className="text-sm text-slate-700">
          Slide ID
          <input className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={slideId} onChange={(event) => onSlideIdChange(event.target.value)} placeholder="slide_05" />
        </label>
        <label className="text-sm text-slate-700">
          精修指令
          <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={instruction} onChange={(event) => onInstructionChange(event.target.value)} placeholder="例如：减少文字、增加图表对比、突出结论。" />
        </label>
        <label className="text-sm text-slate-700">
          可选长需求
          <textarea className="mt-2 min-h-28 w-full rounded-xl border border-slate-200 px-3 py-2" value={longInstruction} onChange={(event) => onLongInstructionChange(event.target.value)} placeholder="只对当前页面生效的补充要求，例如：更像组会汇报，语气更简洁。" />
        </label>
      </div>
      <button className="mt-4 rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-50" onClick={onRegenerate} disabled={disabled || !deckId}>
        精修指定页面
      </button>
    </section>
  );
}
