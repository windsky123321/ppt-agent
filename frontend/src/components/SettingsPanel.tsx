import type { GenerationSettings } from "../types";

type Props = {
  settings: GenerationSettings;
  deckMode: string;
  onDeckModeChange: (value: string) => void;
  onChange: (settings: GenerationSettings) => void;
};

export function SettingsPanel({ settings, deckMode, onDeckModeChange, onChange }: Props) {
  const patch = <K extends keyof GenerationSettings>(key: K, value: GenerationSettings[K]) => {
    onChange({ ...settings, [key]: value });
  };

  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">生成设置</h2>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <SelectField label="Deck 模式" value={deckMode} onChange={onDeckModeChange} options={["Quick Summary", "Reading Group", "Conference Talk", "Thesis Defense Style", "Deep Technical"]} />
        <SelectField label="语言" value={settings.language} onChange={(v) => patch("language", v as GenerationSettings["language"])} options={["en", "zh", "bilingual"]} />
        <SelectField label="听众" value={settings.audience} onChange={(v) => patch("audience", v as GenerationSettings["audience"])} options={["general", "undergraduate", "graduate", "expert", "investor", "lab_meeting", "thesis_defense"]} />
        <label className="text-sm text-slate-700">
          页数目标
          <input className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" type="number" min={5} max={30} value={settings.slide_count} onChange={(event) => patch("slide_count", Number(event.target.value))} />
        </label>
        <SelectField label="主题" value={settings.theme} onChange={(v) => patch("theme", v as GenerationSettings["theme"])} options={["academic_clean", "dark_modern", "minimalist_white"]} />
        <SelectField label="目标" value={settings.presentation_goal} onChange={(v) => patch("presentation_goal", v as GenerationSettings["presentation_goal"])} options={["summarize", "explain", "teach", "critique", "persuade", "compare"]} />
        <SelectField label="风格" value={settings.tone} onChange={(v) => patch("tone", v as GenerationSettings["tone"])} options={["academic", "concise", "visual", "storytelling", "technical"]} />
        <SelectField label="数学深度" value={settings.math_level} onChange={(v) => patch("math_level", v as GenerationSettings["math_level"])} options={["simplified", "balanced", "detailed"]} />
      </div>
      <div className="mt-4 space-y-3">
        <Checkbox label="包含演讲稿" checked={settings.include_speaker_notes} onChange={(value) => patch("include_speaker_notes", value)} />
        <Checkbox label="包含来源页脚" checked={settings.include_source_footers} onChange={(value) => patch("include_source_footers", value)} />
        <Checkbox label="包含局限性" checked={settings.include_limitations} onChange={(value) => patch("include_limitations", value)} />
        <Checkbox label="包含讨论问题" checked={settings.include_discussion_questions} onChange={(value) => patch("include_discussion_questions", value)} />
      </div>
    </section>
  );
}

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: string[] }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}

function Checkbox({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center gap-3 text-sm text-slate-700">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
    </label>
  );
}
