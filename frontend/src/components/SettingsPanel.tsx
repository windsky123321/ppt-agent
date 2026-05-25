import type { GenerationSettings } from "../types";
import { audienceLabels, deckModeLabels, goalLabels, labelFor, themeLabels, toneLabels } from "../utils/labels";

type Props = {
  settings: GenerationSettings;
  deckMode: string;
  onDeckModeChange: (value: string) => void;
  onChange: (settings: GenerationSettings) => void;
};

const deckModeOptions = ["reading_group", "thesis_defense", "research_report", "business_report", "teaching"];
const languageOptions = [
  { value: "zh", label: "中文" },
  { value: "en", label: "英文" },
  { value: "bilingual", label: "中英双语" },
];
const audienceOptions = ["general", "undergraduate", "graduate", "expert", "investor"];
const themeOptions = ["academic_clean", "dark_modern", "minimalist_white"];
const goalOptions = ["summarize", "explain", "teach", "persuade", "critique"];
const toneOptions = ["academic", "concise", "visual", "technical", "storytelling"];
const mathOptions = [
  { value: "simplified", label: "简化" },
  { value: "balanced", label: "平衡" },
  { value: "detailed", label: "详细讲解" },
];

export function SettingsPanel({ settings, deckMode, onDeckModeChange, onChange }: Props) {
  const patch = <K extends keyof GenerationSettings>(key: K, value: GenerationSettings[K]) => {
    onChange({ ...settings, [key]: value });
  };

  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">生成设置</h2>
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <SelectField
          label="汇报模式"
          value={deckMode}
          onChange={onDeckModeChange}
          options={deckModeOptions.map((option) => ({ value: option, label: labelFor(deckModeLabels, option) }))}
        />
        <SelectField
          label="语言"
          value={settings.language}
          onChange={(v) => patch("language", v as GenerationSettings["language"])}
          options={languageOptions}
        />
        <SelectField
          label="听众"
          value={settings.audience}
          onChange={(v) => patch("audience", v as GenerationSettings["audience"])}
          options={audienceOptions.map((option) => ({ value: option, label: labelFor(audienceLabels, option) }))}
        />
        <label className="text-sm text-slate-700">
          目标页数
          <input
            className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2"
            type="number"
            min={5}
            max={30}
            value={settings.slide_count}
            onChange={(event) => patch("slide_count", Number(event.target.value))}
          />
        </label>
        <SelectField
          label="主题"
          value={settings.theme}
          onChange={(v) => patch("theme", v as GenerationSettings["theme"])}
          options={themeOptions.map((option) => ({ value: option, label: labelFor(themeLabels, option) }))}
        />
        <SelectField
          label="生成目标"
          value={settings.presentation_goal}
          onChange={(v) => patch("presentation_goal", v as GenerationSettings["presentation_goal"])}
          options={goalOptions.map((option) => ({ value: option, label: labelFor(goalLabels, option) }))}
        />
        <SelectField
          label="表达风格"
          value={settings.tone}
          onChange={(v) => patch("tone", v as GenerationSettings["tone"])}
          options={toneOptions.map((option) => ({ value: option, label: labelFor(toneLabels, option) }))}
        />
        <SelectField
          label="数学深度"
          value={settings.math_level}
          onChange={(v) => patch("math_level", v as GenerationSettings["math_level"])}
          options={mathOptions}
        />
      </div>
      <div className="mt-4 space-y-3">
        <Checkbox label="包含演讲备注" checked={settings.include_speaker_notes} onChange={(value) => patch("include_speaker_notes", value)} />
        <Checkbox label="包含来源页脚" checked={settings.include_source_footers} onChange={(value) => patch("include_source_footers", value)} />
        <Checkbox label="包含局限性" checked={settings.include_limitations} onChange={(value) => patch("include_limitations", value)} />
        <Checkbox label="包含讨论问题" checked={settings.include_discussion_questions} onChange={(value) => patch("include_discussion_questions", value)} />
      </div>
    </section>
  );
}

function SelectField({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: { value: string; label: string }[] }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
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
