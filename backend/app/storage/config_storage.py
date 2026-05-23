from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app.config import get_settings
from app.schemas.prompt_template import PromptTemplate
from app.schemas.runtime_config import RuntimeModelConfig
from app.utils.json_utils import read_json, write_json


class ConfigStorage:
    def __init__(self) -> None:
        settings = get_settings()
        self.config_dir = settings.storage_path / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.model_config_path = self.config_dir / "model_config.json"
        self.prompt_templates_path = self.config_dir / "prompt_templates.json"

    def load_model_config(self) -> RuntimeModelConfig:
        if self.model_config_path.exists():
            return RuntimeModelConfig(**read_json(self.model_config_path))
        return RuntimeModelConfig()

    def save_model_config(self, config: RuntimeModelConfig) -> RuntimeModelConfig:
        write_json(self.model_config_path, config.model_dump())
        return config

    def load_prompt_templates(self) -> list[PromptTemplate]:
        if not self.prompt_templates_path.exists():
            self.save_prompt_templates(self.default_prompt_templates())
        data = read_json(self.prompt_templates_path)
        return [PromptTemplate(**item) for item in data]

    def save_prompt_templates(self, templates: list[PromptTemplate]) -> None:
        write_json(self.prompt_templates_path, [item.model_dump() for item in templates])

    def upsert_prompt_template(self, template: PromptTemplate) -> PromptTemplate:
        templates = self.load_prompt_templates()
        filtered = [item for item in templates if item.id != template.id]
        filtered.append(template)
        self.save_prompt_templates(filtered)
        return template

    def delete_prompt_template(self, template_id: str) -> None:
        templates = [item for item in self.load_prompt_templates() if item.id != template_id]
        self.save_prompt_templates(templates)

    def default_prompt_templates(self) -> list[PromptTemplate]:
        now = datetime.now(timezone.utc).isoformat()
        presets = [
            (
                "中文研究生组会汇报",
                "面向研究生组会的中文学术汇报。",
                "zh",
                "请帮我把这篇论文做成中文组会汇报 PPT，听众是相关方向研究生。总页数控制在 15 页左右，重点讲研究问题、方法框架、核心创新、实验结果和局限性。不要逐字翻译论文，要像我在组会上讲解一样自然。尽量使用论文里的图和表，每页加演讲备注。",
            ),
            (
                "英文专家会议报告",
                "面向专家听众的英文会议报告。",
                "en",
                "Please turn this paper into an expert-level English conference talk deck. Focus on the research problem, architecture, technical novelty, strongest experiments, limitations, and takeaways. Keep the slides concise, visual, and source-grounded.",
            ),
            (
                "双语本科教学课件",
                "适合本科课堂讲解的双语课件。",
                "bilingual",
                "请把这篇论文整理成双语本科教学课件，重点解释背景、核心概念、方法流程和结果意义，减少公式，增强可讲解性，并给出演讲备注。",
            ),
            (
                "批判性论文精读",
                "突出优点、局限性和讨论问题的精读模板。",
                "zh",
                "请做一份批判性论文精读 PPT，重点突出研究问题、方法假设、实验是否充分、优点、局限性和讨论问题。不要夸大论文结论。",
            ),
            (
                "论文答辩风格汇报",
                "结构更完整的答辩风格 PPT。",
                "zh",
                "请按论文答辩风格生成 PPT，保留关键图表，结构完整，强调实验设计、结果解释和局限性。必要时增加备份页，但仍保持内容可编辑。",
            ),
            (
                "快速 8 页总结",
                "压缩版快速汇报模板。",
                "zh",
                "请将这篇论文压缩成 8 页以内的快速总结 PPT，只保留最关键的问题、方法、结果和结论，减少细节，适合快速读书会分享。",
            ),
        ]
        return [
            PromptTemplate(
                id=f"prompt_{uuid4().hex[:8]}",
                name=name,
                description=description,
                language=language,
                content=content,
                created_at=now,
                updated_at=now,
            )
            for name, description, language, content in presets
        ]
