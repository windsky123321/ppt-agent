import type { ParsedPaper } from "../types";
import { labelFor, sectionLabels } from "../utils/labels";

type Props = {
  parsedPaper: ParsedPaper | null;
  paperSummary?: Record<string, unknown> | null;
  targetLanguage?: string;
};

export function OutlinePreview({ parsedPaper, paperSummary, targetLanguage = "zh" }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">论文结构预览</h2>
      {parsedPaper ? (
        <>
          <p className="mt-2 text-sm text-slate-600">{parsedPaper.title}</p>
          <div className="mt-5 space-y-3">
            {parsedPaper.sections.slice(0, 8).map((section) => (
              <div key={`${section.title}-${section.page_start}`} className="rounded-2xl bg-slate-50 px-4 py-3">
                <div className="text-sm font-semibold text-ink">{labelFor(sectionLabels, section.title)}</div>
                <div className="mt-1 text-xs text-slate-500">
                  p.{section.page_start} - p.{section.page_end}
                </div>
                <p className="mt-2 text-sm text-slate-600">{previewText(section.title, section.text, paperSummary, targetLanguage)}</p>
              </div>
            ))}
          </div>
        </>
      ) : (
        <p className="mt-2 text-sm text-slate-500">上传并解析 PDF 后，这里会显示论文标题和主要章节结构。</p>
      )}
    </section>
  );
}

function previewText(title: string, text: string, paperSummary: Record<string, unknown> | null | undefined, targetLanguage: string) {
  if (targetLanguage !== "zh" || !paperSummary) {
    return shorten(text);
  }
  const map: Record<string, string> = {
    Abstract: String(paperSummary.one_sentence_summary ?? ""),
    Introduction: String(paperSummary.problem ?? ""),
    Method: String(paperSummary.method_overview ?? ""),
    Experiments: String(paperSummary.experiment_setup ?? ""),
    Results: Array.isArray(paperSummary.main_results) ? String((paperSummary.main_results as string[]).join("；")) : "",
    Conclusion: String(paperSummary.conclusion ?? ""),
  };
  return shorten(map[title] || text);
}

function shorten(text: string) {
  if (text.length <= 180) {
    return text;
  }
  return `${text.slice(0, 180)}…`;
}
