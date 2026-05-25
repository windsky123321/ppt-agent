export const deckModeLabels: Record<string, string> = {
  reading_group: "论文精读",
  thesis_defense: "毕业答辩",
  research_report: "科研汇报",
  business_report: "商业汇报",
  teaching: "教学课件",
  "Reading Group": "论文精读",
  "Thesis Defense Style": "毕业答辩",
  "Quick Summary": "科研汇报",
  "Conference Talk": "科研汇报",
  "Deep Technical": "论文精读",
};

export const audienceLabels: Record<string, string> = {
  graduate: "研究生",
  expert: "专家评审",
  general: "普通听众",
  undergraduate: "本科生",
  executive: "管理层",
  investor: "管理层",
  lab_meeting: "组会汇报",
  thesis_defense: "答辩评审",
};

export const themeLabels: Record<string, string> = {
  academic_clean: "学术简洁",
  modern: "现代商务",
  dark: "深色科技",
  minimal: "极简",
  thesis: "答辩风格",
  dark_modern: "深色科技",
  minimalist_white: "极简",
};

export const toneLabels: Record<string, string> = {
  academic: "学术",
  concise: "简洁",
  visual: "图文并重",
  detailed: "详细讲解",
  defense: "答辩陈述",
  storytelling: "图文并重",
  technical: "详细讲解",
};

export const goalLabels: Record<string, string> = {
  explain: "讲清楚论文",
  persuade: "说服听众",
  teach: "教学讲解",
  summarize: "总结汇报",
  defend: "答辩展示",
  critique: "论文精读",
  compare: "对比分析",
};

export const statusLabels: Record<string, string> = {
  completed: "已完成",
  Complete: "已完成",
  completed_with_warnings: "已完成但需精修",
  quality_failed: "质量未通过",
  running: "生成中",
  failed: "失败",
  pending: "等待中",
  processing: "生成中",
  idle: "等待中",
  ready: "等待中",
};

export const stageLabels: Record<string, string> = {
  Uploading: "上传中",
  "Parsing paper": "解析论文",
  "Extracting figures and tables": "提取图表",
  "Summarizing paper": "整理摘要",
  "Planning deck": "规划结构",
  "Writing slides": "撰写页面",
  "Checking grounding": "检查依据",
  "Running critic": "质量检查",
  "Repairing issues": "自动精修",
  "Building PPTX": "导出 PPT",
  "Quality check": "质量门控",
  Complete: "已完成",
  ready: "等待中",
};

export const sectionLabels: Record<string, string> = {
  Abstract: "摘要",
  Introduction: "引言",
  Method: "方法",
  Methods: "方法",
  Experiments: "实验",
  Results: "结果",
  Conclusion: "结论",
  Discussion: "讨论",
  Limitations: "局限",
  Background: "背景",
};

export function labelFor(map: Record<string, string>, value: string): string {
  return map[value] ?? value;
}
