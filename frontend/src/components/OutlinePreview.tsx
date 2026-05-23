import type { ParsedPaper } from "../types";

type Props = {
  parsedPaper: ParsedPaper | null;
};

export function OutlinePreview({ parsedPaper }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">论文结构预览</h2>
      {parsedPaper ? (
        <>
          <p className="mt-2 text-sm text-slate-600">{parsedPaper.title}</p>
          <div className="mt-5 space-y-3">
            {parsedPaper.sections.slice(0, 8).map((section) => (
              <div key={`${section.title}-${section.page_start}`} className="rounded-2xl bg-slate-50 px-4 py-3">
                <div className="text-sm font-semibold text-ink">{section.title}</div>
                <div className="mt-1 text-xs text-slate-500">
                  p.{section.page_start} - p.{section.page_end}
                </div>
                <p className="mt-2 text-sm text-slate-600">
                  {section.text.slice(0, 180)}
                  {section.text.length > 180 ? "..." : ""}
                </p>
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
