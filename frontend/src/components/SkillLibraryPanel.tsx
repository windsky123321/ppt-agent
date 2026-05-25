import { useState } from "react";

import type { SkillManifest, SkillSearchResult } from "../types";

type Props = {
  installedSkills: SkillManifest[];
  searchResults: SkillSearchResult[];
  onSearch: (keyword: string) => Promise<void>;
  onImportZip: (file: File) => Promise<void>;
  onImportFolder: (folderPath: string) => Promise<void>;
  onImportUrl: (url: string) => Promise<void>;
  onEnable: (skillId: string) => Promise<void>;
  onDisable: (skillId: string) => Promise<void>;
  onDelete: (skillId: string) => Promise<void>;
  onTest: (skillId: string) => Promise<void>;
};

const riskLabel: Record<SkillManifest["risk_level"], string> = {
  low: "低风险",
  medium: "中风险",
  high: "高风险",
  unknown: "未知风险",
};

export function SkillLibraryPanel(props: Props) {
  const [keyword, setKeyword] = useState("");
  const [folderPath, setFolderPath] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");

  return (
    <section className="rounded-lg bg-white p-5 shadow-card">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">技能库</h2>
          <p className="text-sm text-slate-600">外部技能默认不可信、默认禁用、默认不执行脚本。</p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-3">
        <div className="rounded-lg bg-slate-50 p-4">
          <h3 className="font-medium">搜索技能</h3>
          <input
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
            placeholder="输入关键词，例如 business-report"
            className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
          <button className="mt-3 rounded-md bg-accent px-4 py-2 text-sm text-white" onClick={() => void props.onSearch(keyword)}>
            搜索技能
          </button>
          <div className="mt-4 space-y-2">
            {props.searchResults.length === 0 ? <p className="text-sm text-slate-500">暂无搜索结果</p> : null}
            {props.searchResults.map((item) => (
              <div key={item.id} className="rounded-md border border-slate-200 bg-white p-3 text-sm">
                <div className="flex items-center justify-between gap-3">
                  <strong>{item.name}</strong>
                  <span className="text-xs text-slate-500">{riskLabel[item.risk_level]}</span>
                </div>
                <p className="mt-1 text-slate-600">{item.description}</p>
                <p className="mt-2 text-xs text-slate-500">来源：{item.source}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-lg bg-slate-50 p-4">
          <h3 className="font-medium">导入技能</h3>
          <div className="mt-3">
            <label className="block text-sm text-slate-700">从本地 zip 导入</label>
            <input
              type="file"
              accept=".zip"
              className="mt-2 block w-full text-sm"
              onChange={(event) => {
                const file = event.target.files?.[0];
                if (file) void props.onImportZip(file);
              }}
            />
          </div>
          <div className="mt-4">
            <label className="block text-sm text-slate-700">从本地文件夹导入</label>
            <input
              value={folderPath}
              onChange={(event) => setFolderPath(event.target.value)}
              placeholder="输入本机文件夹路径"
              className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
            <button className="mt-2 rounded-md bg-slate-800 px-4 py-2 text-sm text-white" onClick={() => void props.onImportFolder(folderPath)}>
              导入文件夹
            </button>
          </div>
          <div className="mt-4">
            <label className="block text-sm text-slate-700">从 URL 或 GitHub 仓库导入</label>
            <input
              value={sourceUrl}
              onChange={(event) => setSourceUrl(event.target.value)}
              placeholder="例如 mock://skill_business_report"
              className="mt-2 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            />
            <button className="mt-2 rounded-md bg-slate-800 px-4 py-2 text-sm text-white" onClick={() => void props.onImportUrl(sourceUrl)}>
              导入 URL
            </button>
          </div>
        </div>

        <div className="rounded-lg bg-slate-50 p-4">
          <h3 className="font-medium">风险提示</h3>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>来源未知，请谨慎启用。</li>
            <li>该技能包含可执行脚本时，默认不会运行。</li>
            <li>外部技能默认不能读取用户文件、不能联网、不能获得 API Key。</li>
            <li>启用后，PPT Agent 仅会读取静态建议、模板和约束。</li>
          </ul>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="font-medium">已安装技能</h3>
        <div className="mt-3 space-y-3">
          {props.installedSkills.length === 0 ? <p className="text-sm text-slate-500">暂无已安装技能</p> : null}
          {props.installedSkills.map((skill) => (
            <div key={skill.id} className="rounded-lg border border-slate-200 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <strong>{skill.name}</strong>
                    <span className={`rounded-full px-2 py-0.5 text-xs ${skill.enabled ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>
                      {skill.enabled ? "已启用" : "未启用"}
                    </span>
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700">{riskLabel[skill.risk_level]}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-600">{skill.description}</p>
                  <p className="mt-1 text-xs text-slate-500">来源：{skill.source || "本地"} ｜ 作者：{skill.author || "未知"}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {skill.enabled ? (
                    <button className="rounded-md bg-slate-200 px-3 py-1.5 text-sm" onClick={() => void props.onDisable(skill.id)}>
                      禁用技能
                    </button>
                  ) : (
                    <button className="rounded-md bg-accent px-3 py-1.5 text-sm text-white" onClick={() => void props.onEnable(skill.id)}>
                      启用技能
                    </button>
                  )}
                  <button className="rounded-md bg-white px-3 py-1.5 text-sm ring-1 ring-slate-300" onClick={() => void props.onTest(skill.id)}>
                    测试技能
                  </button>
                  <button className="rounded-md bg-rose-50 px-3 py-1.5 text-sm text-rose-700 ring-1 ring-rose-200" onClick={() => void props.onDelete(skill.id)}>
                    删除技能
                  </button>
                </div>
              </div>
              <div className="mt-3 grid gap-2 text-xs text-slate-600 md:grid-cols-3">
                <div>标签：{skill.tags.join("、") || "无"}</div>
                <div>能力：{skill.capabilities.join("、") || "无"}</div>
                <div>最近使用：{skill.last_used_at || "尚未使用"}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
