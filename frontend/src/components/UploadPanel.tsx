type Props = {
  selectedFile: File | null;
  onFileChange: (file: File | null) => void;
};

export function UploadPanel({ selectedFile, onFileChange }: Props) {
  return (
    <section className="rounded-3xl bg-white/85 p-6 shadow-card backdrop-blur">
      <h2 className="text-xl font-semibold text-ink">上传 PDF 论文</h2>
      <p className="mt-2 text-sm text-slate-600">上传一篇学术论文 PDF，系统会在本地生成中间 artifacts 和可编辑 PPTX。</p>
      <label className="mt-5 flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition hover:border-accent hover:bg-blue-50">
        <span className="text-sm font-medium text-slate-700">{selectedFile ? selectedFile.name : "点击选择 PDF 文件"}</span>
        <span className="mt-2 text-xs text-slate-500">所有中间结果都会保存在本地 storage 目录中。</span>
        <input className="hidden" type="file" accept="application/pdf" onChange={(event) => onFileChange(event.target.files?.[0] ?? null)} />
      </label>
    </section>
  );
}
