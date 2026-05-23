import type { ParsedInstructionSpec, PromptTemplate } from "../types";

type Props = {
  longInstruction: string;
  parsedInstruction: ParsedInstructionSpec | null;
  promptTemplates: PromptTemplate[];
  selectedTemplateId: string;
  onInstructionChange: (value: string) => void;
  onTemplateSelect: (templateId: string) => void;
  onParse: () => void;
  onClear: () => void;
  onSaveTemplate: () => void;
  onUseExample: () => void;
};

export function InstructionStudioPanel({
  longInstruction,
  parsedInstruction,
  promptTemplates,
  selectedTemplateId,
  onInstructionChange,
  onTemplateSelect,
  onParse,
  onClear,
  onSaveTemplate,
  onUseExample,
}: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-semibold text-ink">长需求 / Prompt Studio</h2>
          <p className="mt-2 text-sm text-slate-600">你可以直接输入完整需求，系统会先解析要求，再驱动现有 PPT 生成流程。</p>
        </div>
        <div className="text-sm text-slate-500">{longInstruction.length} 字符</div>
      </div>

      <label className="mt-4 block text-sm text-slate-700">
        需求模板
        <select className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2" value={selectedTemplateId} onChange={(event) => onTemplateSelect(event.target.value)}>
          <option value="">请选择内置或已保存模板</option>
          {promptTemplates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.name}
            </option>
          ))}
        </select>
      </label>

      <label className="mt-4 block text-sm text-slate-700">
        长需求输入
        <textarea
          className="mt-2 min-h-56 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm"
          value={longInstruction}
          onChange={(event) => onInstructionChange(event.target.value)}
          placeholder="例如：请把这篇论文做成中文组会汇报 PPT，控制在 12-15 页，重点讲研究问题、方法、实验结果和局限性，少堆文字，多解释图表。"
        />
      </label>

      <div className="mt-4 flex flex-wrap gap-3">
        <button className="rounded-2xl bg-ink px-4 py-2 text-sm font-semibold text-white" onClick={onParse}>解析需求</button>
        <button className="rounded-2xl bg-slate-100 px-4 py-2 text-sm font-medium text-ink" onClick={onClear}>清空</button>
        <button className="rounded-2xl bg-slate-100 px-4 py-2 text-sm font-medium text-ink" onClick={onSaveTemplate}>保存为模板</button>
        <button className="rounded-2xl bg-slate-100 px-4 py-2 text-sm font-medium text-ink" onClick={onUseExample}>使用示例</button>
      </div>

      {parsedInstruction ? (
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          <SpecCard label="语言" value={parsedInstruction.preferred_language || parsedInstruction.detected_language} />
          <SpecCard label="听众" value={parsedInstruction.audience || "未识别"} />
          <SpecCard label="目标" value={parsedInstruction.presentation_goal || "未识别"} />
          <SpecCard label="语气" value={parsedInstruction.tone || "未识别"} />
          <SpecCard label="页数" value={String(parsedInstruction.slide_count_target || "未识别")} />
          <SpecCard label="数学深度" value={parsedInstruction.math_level || "未识别"} />
          <SpecList label="必须包含" values={parsedInstruction.must_include} />
          <SpecList label="避免内容" values={parsedInstruction.avoid} />
          <SpecList label="风格要求" values={parsedInstruction.style_requirements} />
          <SpecList label="冲突警告" values={parsedInstruction.conflict_warnings} emptyText="无" />
        </div>
      ) : null}
    </section>
  );
}

function SpecCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-3">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-2 text-sm font-medium text-ink">{value}</div>
    </div>
  );
}

function SpecList({ label, values, emptyText = "未识别" }: { label: string; values: string[]; emptyText?: string }) {
  return (
    <div className="rounded-2xl bg-slate-50 px-4 py-3">
      <div className="text-xs uppercase tracking-[0.18em] text-slate-500">{label}</div>
      <div className="mt-2 text-sm text-ink">{values.length ? values.join(" / ") : emptyText}</div>
    </div>
  );
}
