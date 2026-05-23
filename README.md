# Personalized Paper-to-PPT Agent

Local-first web app for turning an academic paper PDF into an editable PowerPoint deck, with grounded summaries, multimodal paper assets, persistent user profiles, runtime model configuration, long instruction parsing, critic/repair checks, and selected-slide regeneration.

## Windows EXE Packaging

Windows 用户现在可以直接双击 `build_release_windows.bat` 一键构建发布包。脚本会自动执行环境检查、前端构建检查、PyInstaller 预检、EXE 打包、文档复制和 portable 兜底包生成。

关键输出：

- `release/PPT-Agent.exe`
- `release/PPT-Agent-Portable/`
- `logs/build_windows.log`

如果当前机器未安装 PyInstaller，脚本会优先自动安装；若在线安装失败，会给出明确中文提示，并建议手动执行：

```bash
python -m pip install pyinstaller
```

如果存在 `packaging/wheelhouse/`，脚本会优先从本地 wheel 离线安装 PyInstaller。

也可以通过 GitHub Actions 自动生成 Windows 发布包：

- 打开仓库的 `Actions`
- 运行 `Build Windows EXE`
- 下载 artifact `PPT-Agent-Windows-Release`

安全说明：

- EXE 不会内置真实 API Key
- `.env.example` 只保留空占位
- 发布包不会包含 `.env`、`logs`、`storage`、`outputs`、`temp` 中的用户文件

## 功能概览

当前版本支持：

- 上传论文 PDF 并解析为结构化 `parsed_paper.json`
- 从论文正文生成 grounded `paper_summary.json`
- 结合用户 Profile、Deck Mode 和长自然语言需求生成 PPT
- 提取图表资产并保存 `extracted_assets.json`
- 生成 `grounding_report.json`、`critic_report.json`、`repair_history.json`
- 生成可编辑的 `final_deck.pptx`
- 选择单页重新生成，并保留整 deck 的其余内容
- 使用本地 JSON 文件保存配置、模板和 artifacts
- Mock 模式下无需付费 API key 即可完整跑通

## 技术栈

- Backend: Python 3.11+, FastAPI, Pydantic, PyMuPDF, python-pptx, Pillow
- Frontend: React, TypeScript, Vite, Tailwind CSS
- Storage: local filesystem JSON artifacts, no database

## 项目结构

```text
backend/
  app/
    api/
    agents/
    llm/
    parser/
    ppt/
    prompts/
    schemas/
    storage/
    utils/
    vision/
  scripts/
  tests/
frontend/
  src/
examples/
storage/
logs/
start_windows.bat
stop_windows.bat
check_windows_env.bat
run_smoke_windows.bat
WINDOWS_QUICKSTART.md
README.md
```

## Windows 一键启动

Windows 用户优先使用根目录脚本，不需要手工分别启动前后端。

前置软件：

- Python 3.11+
- Node.js 18+

启动步骤：

1. 双击 [start_windows.bat](C:/Users/windysky/Documents/ppt%20agent/start_windows.bat)
2. 脚本会自动：
   - 检查 Python / Node / npm
   - 创建 `backend/.venv`
   - 安装后端依赖
   - 安装前端依赖
   - 在缺少 `.env` 时从 `.env.example` 复制
   - 启动后端 `http://127.0.0.1:8000`
   - 构建或复用 `frontend/dist`
   - 由后端直接托管前端静态页面
   - 等待健康检查完成并自动打开浏览器
3. 浏览器打开后进入 Web UI
4. 用 [stop_windows.bat](C:/Users/windysky/Documents/ppt%20agent/stop_windows.bat) 停止服务

日志位置：

- `logs/startup.log`
- `logs/backend.log`
- `logs/frontend.log`

环境检查：

- 双击 [check_windows_env.bat](C:/Users/windysky/Documents/ppt%20agent/check_windows_env.bat)

Windows 烟雾测试：

- 双击 [run_smoke_windows.bat](C:/Users/windysky/Documents/ppt%20agent/run_smoke_windows.bat)

更详细的中文说明见 [WINDOWS_QUICKSTART.md](C:/Users/windysky/Documents/ppt%20agent/WINDOWS_QUICKSTART.md)。

## Windows 桌面应用与发布包

当前产品化入口：

- `desktop/launcher.py`：中文桌面启动器，负责启动后端、检测端口、健康检查、打开浏览器、停止服务和写日志。
- `build_release_windows.bat`：一键构建发布包。
- `packaging/launcher.spec`：PyInstaller 打包配置。

发布构建：

```bash
build_release_windows.bat
```

GitHub Actions 构建：

1. 打开 GitHub 仓库的 `Actions`
2. 选择 `Build Windows EXE`
3. 点击 `Run workflow`
4. 构建完成后下载 artifact `PPT-Agent-Windows-Release`

输出目录：

- `release/PPT-Agent.exe`
- `release/PPT-Agent-Portable/`

说明：

- 当前版本采用“桌面启动器 + 默认浏览器”的稳定方案。
- 如果 `frontend/dist` 已存在，后端会直接托管静态前端。
- API Key 不会写入发布包，用户可在 Web UI 的模型配置页保存本地运行时配置。
- GitHub Actions 也不会写入真实 API Key；该工作流只使用公开源码和本地构建依赖。

## 本地手工启动

后端：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端：

```bash
cd frontend
npm install
npm run dev
```

如果 PowerShell 阻止 `npm`，请使用 `npm.cmd`。

## 运行时模型配置

Web UI 提供“模型配置”面板，支持运行时修改：

- LLM provider
- LLM base URL
- LLM API key
- LLM model
- Vision provider
- Vision base URL
- Vision API key
- Vision model
- `enable_vision`
- `enable_critic`
- `enable_repair`
- `max_repair_loops`

后端接口：

- `GET /api/config/model`
- `POST /api/config/model`
- `POST /api/config/model/test`

运行时配置保存在：

- `storage/config/model_config.json`

说明：

- GET 响应会对 API key 做脱敏展示
- 不会在日志中打印完整 API key
- 如果同时存在 `.env` 和运行时配置，运行时配置优先
- Mock 模式无需 API key，可直接测试和生成

## Profile 系统

Profiles 以本地 JSON 持久化保存，可通过 API 或前端管理。

接口：

- `POST /api/profiles`
- `GET /api/profiles`
- `GET /api/profiles/{profile_id}`
- `PUT /api/profiles/{profile_id}`
- `DELETE /api/profiles/{profile_id}`

内置预设：

- Chinese Graduate Reading Group
- English Expert Conference Talk
- Bilingual Undergraduate Teaching
- Critical Review Lab Meeting

Profile 会影响：

- slide 数量
- 输出语言
- tone
- 数学细节程度
- 是否包含 speaker notes
- 是否包含 limitations / discussion
- 是否显示 source footers
- 主题和版式密度

## 长需求 / Prompt Studio

除了常规 Profile 生成，系统还支持直接粘贴一整段自然语言需求。

示例：

```text
请帮我把这篇论文做成中文组会汇报 PPT，听众是计算机视觉方向研究生。总页数控制在 15 页左右，重点讲研究问题、方法框架、核心创新、实验结果和局限性。不要逐字翻译论文，要像我在组会上讲一样自然。公式只保留最关键的一个，并用通俗语言解释。尽量使用论文里的图和表，每张图要说明它证明了什么。每页加演讲稿。最后加一页优点、一页局限性、一页讨论问题。风格简洁、学术、不要太花。
```

后端接口：

- `POST /api/instructions/parse`

生成时会合并：

1. selected profile
2. inline profile overrides
3. selected deck mode
4. long instruction
5. system defaults

冲突优先级：

`long instruction > inline profile > selected profile > deck mode > system defaults`

保存的相关 artifacts：

- `user_instruction_raw.md`
- `user_instruction_spec.json`
- `merged_generation_config.json`
- `prompt_merge_report.json`

约束：

- 论文仍然是唯一事实来源
- 长需求只能调整展示方式、结构和风格
- 若长需求要求论文中不存在的结论、实验结果或比较，系统会忽略、标记不支持或在 grounding/critic 中报警

## Prompt Template

系统支持本地保存和复用长需求模板。

接口：

- `GET /api/prompt-templates`
- `POST /api/prompt-templates`
- `PUT /api/prompt-templates/{template_id}`
- `DELETE /api/prompt-templates/{template_id}`

模板保存在：

- `storage/config/prompt_templates.json`

内置模板包括：

- 中文研究生组会汇报
- 英文专家会议报告
- 双语本科教学课件
- 批判性论文精读
- 论文答辩风格汇报
- 快速 8 页总结

## API 概览

- `GET /api/health`
- `GET /api/config/model`
- `POST /api/config/model`
- `POST /api/config/model/test`
- `POST /api/papers/upload`
- `GET /api/jobs/{job_id}`
- `GET /api/decks/{deck_id}/download`
- `GET /api/decks/{deck_id}/artifacts`
- `GET /api/decks/{deck_id}/artifacts/{artifact_name}`
- `POST /api/decks/{deck_id}/regenerate-slide`
- `POST /api/instructions/parse`
- `GET /api/prompt-templates`
- `POST /api/prompt-templates`
- `PUT /api/prompt-templates/{template_id}`
- `DELETE /api/prompt-templates/{template_id}`
- `GET /api/profiles`
- `POST /api/profiles`
- `GET /api/profiles/{profile_id}`
- `PUT /api/profiles/{profile_id}`
- `DELETE /api/profiles/{profile_id}`

## 图表资产

Figures 和 tables 会抽取为结构化资产并保存为：

- `extracted_assets.json`

每个 asset 包含：

- `id`
- `asset_type`
- `page_number`
- `original_caption`
- `nearby_text`
- `image_path`
- `short_visual_description`
- `technical_interpretation`
- `why_it_matters`
- `suggested_slide_usage`
- `importance_score`
- `source_reference`

Mock vision 模式无需外部 API，会基于 caption 和附近文字生成保守描述。

## Grounding / Critic / Repair

系统会保存：

- `grounding_report.json`
- `critic_report.json`
- `repair_history.json`

Critic 会检查：

- unsupported claims
- weak grounding
- missing source refs
- abstract-only refs
- too many bullets
- likely overflow
- missing notes
- low confidence
- weak key message
- poor visual usage

Repair loop：

- 尽量只修改受影响的 slides
- 不重新解析整篇论文
- 可裁剪 bullets、补 notes、补保守 source refs、附加更合适的 visual elements
- 由 `MAX_REPAIR_LOOPS` 控制最大轮数

## 选择单页重生成

接口：

- `POST /api/decks/{deck_id}/regenerate-slide`

请求体示例：

```json
{
  "slide_ids": ["slide_05"],
  "instruction": "Make this slide more visual and reduce text.",
  "long_instruction": "optional long instruction",
  "profile_id": "optional profile id"
}
```

行为：

- 只重生成指定 slide
- 保留其余 slides、deck plan、profile、assets
- 重新运行 grounding / critic
- 重建 `final_deck.pptx`

## 产物与存储

默认目录：

- `storage/uploads/`
- `storage/decks/{deck_id}/`
- `storage/config/`
- `logs/`

每个 deck 可能保存：

- `original.pdf`
- `parsed_paper.json`
- `extracted_assets.json`
- `paper_summary.json`
- `deck_plan.json`
- `slide_drafts.json`
- `grounding_report.json`
- `critic_report.json`
- `repair_history.json`
- `user_instruction_raw.md`
- `user_instruction_spec.json`
- `merged_generation_config.json`
- `prompt_merge_report.json`
- `final_deck.pptx`
- `job_status.json`

## Mock 模式

默认 `.env.example` 配置为 Mock 可运行：

```env
DEFAULT_LLM_PROVIDER=mock
DEFAULT_VISION_PROVIDER=mock
ENABLE_VISION=true
ENABLE_CRITIC=true
ENABLE_REPAIR=true
MAX_REPAIR_LOOPS=2
STORAGE_DIR=storage
```

Mock 模式支持：

- profile-based generation
- 长需求解析的规则回退
- mock figure/table understanding
- deterministic grounding / critic / repair
- selected-slide regeneration
- editable PPTX generation

## 常见工作流

1. 启动服务
2. 打开 Web UI
3. 配置模型，或直接切换到 Mock 模式
4. 上传 PDF
5. 选择或编辑 Profile
6. 选择 Deck Mode
7. 粘贴长需求，或加载需求模板
8. 点击“解析需求”查看结构化结果，或直接生成
9. 等待生成进度完成
10. 下载 `final_deck.pptx`
11. 如有需要，对单页执行重生成

## 测试与 Smoke

后端测试：

```bash
cd backend
pytest
```

Round 1 smoke：

```bash
cd backend
python scripts/smoke_test.py
```

Round 2 smoke：

```bash
cd backend
python scripts/smoke_round2.py
```

Windows smoke：

```bash
cd backend
python scripts/smoke_windows.py
```

前端构建：

```bash
cd frontend
npm run build
```

## 故障排查

- Python not found：先安装 Python 3.11+，并勾选加入 PATH
- Node not found：先安装 Node.js 18+
- port occupied：关闭占用 8000 或 5173 的程序后重试
- API key invalid：在模型配置页重新填写 API key / base URL / model
- backend not starting：查看 `logs/backend.log`
- frontend blank page：查看 `logs/frontend.log`，并确认 `http://127.0.0.1:8000/api/health` 可访问
- PDF parse failed：部分加密 PDF 或扫描 PDF 无法稳定抽取文本
- PPTX generation failed：查看 `critic_report.json`、`grounding_report.json` 和后端日志
- no figures extracted：系统会回退为纯文本 grounded slides
- long instruction parse failed：可先切换到 Mock 模式，或缩短过长输入后重试

## 当前限制

- 多栏论文 PDF 仍可能带来 section 提取噪声
- figure/table 提取仍偏启发式，bbox 和裁剪能力有限
- 没有真实视觉模型时，图表理解主要依赖 caption 和附近文字
- 某些 source refs 仍会保守回退到更泛的 section
- 长需求会影响展示风格与结构，但不能覆盖 grounding 规则
- 生成结果仍应由人工最终审阅

## 安全与约束

- 论文是唯一事实来源
- 不支持伪造论文结果、比较或引用
- unsupported claims 会被移除或标记
- vision analysis 在非 Mock 模式下需要配置可用 vision provider
