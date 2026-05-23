type Props = {
  deckId: string | null;
  slideId: string;
  instruction: string;
  onSlideIdChange: (value: string) => void;
  onInstructionChange: (value: string) => void;
  onRegenerate: () => void;
  disabled: boolean;
};

export function RegeneratePanel({ deckId, slideId, instruction, onSlideIdChange, onInstructionChange, onRegenerate, disabled }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">Selected-Slide Regeneration</h2>
      <p className="mt-2 text-sm text-slate-600">Regenerate one slide with an extra instruction while preserving the existing deck.</p>
      <div className="mt-4 grid gap-4">
        <label className="text-sm text-slate-700">
          Slide ID
          <input className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={slideId} onChange={(event) => onSlideIdChange(event.target.value)} placeholder="slide_05" />
        </label>
        <label className="text-sm text-slate-700">
          Instruction
          <textarea className="mt-2 min-h-24 w-full rounded-xl border border-slate-200 px-3 py-2" value={instruction} onChange={(event) => onInstructionChange(event.target.value)} placeholder="Make this slide more visual and reduce text." />
        </label>
      </div>
      <button className="mt-4 rounded-2xl bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-50" onClick={onRegenerate} disabled={disabled || !deckId}>
        Regenerate This Slide
      </button>
    </section>
  );
}
