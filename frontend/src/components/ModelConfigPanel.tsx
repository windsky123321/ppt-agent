import type { RuntimeModelConfig, RuntimeModelConfigView } from "../types";

const LOW_TOKEN_DEFAULTS = {
  fallback_llm_model: "gpt-4.1-mini",
  reasoning_effort: "low",
  verbosity: "low",
  temperature: 0.2,
  patch_mode: true,
  revision_max_output_tokens: 1200,
  normal_max_output_tokens: 4000,
  output_dir: "storage/decks",
};

const PRESETS: Record<string, Partial<RuntimeModelConfig>> = {
  mock: {
    llm_provider: "mock",
    llm_base_url: "",
    llm_model: "gpt-5.5",
    vision_provider: "mock",
    vision_base_url: "",
    vision_model: "gpt-4.1-mini",
    ...LOW_TOKEN_DEFAULTS,
  },
  openai: {
    llm_provider: "openai",
    llm_base_url: "https://api.openai.com/v1",
    llm_model: "gpt-5.5",
    vision_provider: "openai",
    vision_base_url: "https://api.openai.com/v1",
    vision_model: "gpt-4.1-mini",
    ...LOW_TOKEN_DEFAULTS,
  },
};

type Props = {
  config: RuntimeModelConfig;
  savedView: RuntimeModelConfigView | null;
  status: string;
  onChange: (config: RuntimeModelConfig) => void;
  onSave: () => void;
  onTest: () => void;
  onUseMock: () => void;
};

export function ModelConfigPanel({ config, savedView, status, onChange, onSave, onTest, onUseMock }: Props) {
  const patch = <K extends keyof RuntimeModelConfig>(key: K, value: RuntimeModelConfig[K]) => onChange({ ...config, [key]: value });
  const applyPreset = (preset: string) => onChange({ ...config, ...PRESETS[preset] });
  const isMockMode = config.llm_provider === "mock" || config.vision_provider === "mock";
  const missingKey = config.llm_provider !== "mock" && !config.llm_api_key && !savedView?.llm_api_key_masked;

  return (
    <section className="rounded-lg bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">模型配置</h2>
          <p className="mt-1 text-sm text-slate-600">在这里配置 API Key、模型和测试模式。Mock 只用于流程测试，不代表正式生成质量。</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button className="rounded-md bg-slate-100 px-3 py-2 text-sm font-medium text-ink" onClick={onUseMock}>
            切换到 Mock 测试
          </button>
          <button className="rounded-md bg-white px-3 py-2 text-sm font-medium text-ink ring-1 ring-slate-200" onClick={onTest}>
            测试连接
          </button>
          <button className="rounded-md bg-accent px-3 py-2 text-sm font-semibold text-white" onClick={onSave}>
            保存配置
          </button>
        </div>
      </div>

      <div className={`mt-4 rounded-md px-3 py-2 text-sm ${isMockMode ? "bg-amber-50 text-amber-800" : "bg-emerald-50 text-emerald-800"}`}>
        当前模式：{isMockMode ? "Mock 模式：流程测试" : "真实模式：正式生成"}
      </div>
      {isMockMode ? (
        <div className="mt-3 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Mock 模式不会调用真实模型，只用于测试上传、生成、下载流程。
        </div>
      ) : null}
      {missingKey ? (
        <div className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          请填写 API Key 后再进行正式生成。
        </div>
      ) : null}

      <label className="mt-4 block text-sm text-slate-700">
        常用预设
        <select className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2" defaultValue="" onChange={(event) => event.target.value && applyPreset(event.target.value)}>
          <option value="">请选择预设</option>
          <option value="mock">Mock 测试</option>
          <option value="openai">正式生成（OpenAI）</option>
        </select>
      </label>

      <div className="mt-5 grid gap-4 md:grid-cols-2">
        <Field label="LLM Provider" value={config.llm_provider} onChange={(value) => patch("llm_provider", value)} />
        <Field label="LLM Base URL" value={config.llm_base_url} onChange={(value) => patch("llm_base_url", value)} />
        <PasswordField label="LLM API Key" value={config.llm_api_key} maskedValue={savedView?.llm_api_key_masked ?? ""} onChange={(value) => patch("llm_api_key", value)} />
        <Field label="LLM Model" value={config.llm_model} onChange={(value) => patch("llm_model", value)} />
        <Field label="Fallback Model" value={config.fallback_llm_model} onChange={(value) => patch("fallback_llm_model", value)} />
        <Field label="Vision Provider" value={config.vision_provider} onChange={(value) => patch("vision_provider", value)} />
        <Field label="Vision Base URL" value={config.vision_base_url} onChange={(value) => patch("vision_base_url", value)} />
        <PasswordField label="Vision API Key" value={config.vision_api_key} maskedValue={savedView?.vision_api_key_masked ?? ""} onChange={(value) => patch("vision_api_key", value)} />
        <Field label="Vision Model" value={config.vision_model} onChange={(value) => patch("vision_model", value)} />
        <Field label="输出目录" value={config.output_dir} onChange={(value) => patch("output_dir", value)} />
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <Checkbox label="启用 Vision" checked={config.enable_vision} onChange={(value) => patch("enable_vision", value)} />
        <Checkbox label="启用 Critic" checked={config.enable_critic} onChange={(value) => patch("enable_critic", value)} />
        <Checkbox label="启用 Repair" checked={config.enable_repair} onChange={(value) => patch("enable_repair", value)} />
        <Checkbox label="启用 Patch Mode" checked={config.patch_mode} onChange={(value) => patch("patch_mode", value)} />
        <NumberField label="最大修复轮数" value={config.max_repair_loops} min={0} max={5} onChange={(value) => patch("max_repair_loops", value)} />
        <NumberField label="正式生成 Tokens" value={config.normal_max_output_tokens} min={1000} max={12000} onChange={(value) => patch("normal_max_output_tokens", value)} />
        <NumberField label="精修 Tokens" value={config.revision_max_output_tokens} min={300} max={4000} onChange={(value) => patch("revision_max_output_tokens", value)} />
        <NumberField label="Temperature" value={config.temperature} min={0} max={1} step={0.1} onChange={(value) => patch("temperature", value)} />
      </div>

      {status ? <p className="mt-4 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">{status}</p> : null}
    </section>
  );
}

function Field({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <input className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2" value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function PasswordField({ label, value, maskedValue, onChange }: { label: string; value: string; maskedValue: string; onChange: (value: string) => void }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <input className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2" type="password" value={value} placeholder={maskedValue || "未保存"} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function NumberField({ label, value, min, max, step = 1, onChange }: { label: string; value: number; min: number; max: number; step?: number; onChange: (value: number) => void }) {
  return (
    <label className="text-sm text-slate-700">
      {label}
      <input className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2" type="number" min={min} max={max} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

function Checkbox({ label, checked, onChange }: { label: string; checked: boolean; onChange: (value: boolean) => void }) {
  return (
    <label className="flex items-center gap-3 rounded-md bg-slate-50 px-3 py-2 text-sm text-slate-700">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
    </label>
  );
}
