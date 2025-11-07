# Development Plan (v1.0 → v2.0 → v3.0)

本版变更（2025-11）
- 阶段转换：从“仅占位”进入“可执行级规范（不写代码）”。
- 范围聚焦：仅细化 v1.0 所有 TASK；v2.0/v3.0 暂不拉齐到相同粒度。
- 明确 AI 助手提示词需包含：环境与依赖前置（Poetry、pnpm、Playwright、Tesseract）、文件路径约定与可复制执行上下文。
- 性能与可观测性：v1.0 不锁定 SLO；但必须定义并记录计时与度量字段的数据结构。
- i18n 规则：当 JD 语言与用户手动选择冲突时，以“用户手动选择”为最高优先级。

---

## v1.0 全局规范与前置

工具链与环境
- Node v20（.nvmrc），pnpm；Python 3.11（.python-version），Poetry
- Playwright（Chromium 无头浏览器）；Tesseract OCR（含中文/英文语言包）
- 操作系统：macOS/Windows/Linux 任一；需具备本地文件读写权限

环境变量（.env.example 已提供）
- MODEL_PROVIDER=gemini（默认）
- GEMINI_API_KEY（必填，当 provider=gemini）
- OPENAI_API_KEY（可选，预留）
- DATABASE_URL=sqlite:///./storage/app.db
- OCR_ENABLED=true（默认）
- PDF_RENDERER=chromium（默认）
- DEFAULT_OUTPUT_LANG=auto
- APP_PORT=3000 / API_PORT=8000

路径与命名约定
- 上传原文件：storage/resumes/{resumeId}/{original_filename}
- 解析快照：storage/audit/{resumeId}/snapshot_{iso}.json
- 生成产物：storage/exports/{genId}/letter.html|letter.pdf|short.txt
- 标识符：resumeId/genId 均为 `yyyyMMddHHmmss_{8位随机}` 或 DB 自增 id；同时存储 sha256 文件指纹

i18n 策略
- 输出语言=用户手动选择（若设置）> JD 自动识别语言 > DEFAULT_OUTPUT_LANG

可观测性与计时字段（v1.0 必须记录，暂不设 SLO）
- ingestion_ms、ocr_ms、parse_ms、match_ms、generate_ms、render_ms、total_ms
- model_provider、model_name、temperature、top_p、penalties、seed
- tokens_prompt、tokens_completion（若可得）
- input_hash（简历/JD 摘要哈希，sha256 前 12 位）、timestamp、request_id
- 结构化示例（JSON）：
```
{
  "request_id": "2025-11-07T12:00:00Z_abc12345",
  "timestamps": {"start": "...", "end": "..."},
  "timings_ms": {"ingestion": 120, "ocr": 380, "parse": 220, "match": 90, "generate": 950, "render": 310, "total": 2070},
  "model": {"provider": "gemini", "name": "gemini-2.5-flash", "temperature": 0.6, "top_p": 1.0, "seed": 0},
  "tokens": {"prompt": 1200, "completion": 650},
  "inputs": {"resume_hash": "a1b2c3d4e5f6", "jd_hash": "f6e5d4c3b2a1"}
}
```

---

## v1.0（最小可用）— 可执行级规范

### TASK001 仓库初始化与骨架（已完成）
- 版本号：v1.0
- 状态：完成
- 交付物：monorepo 目录、规范化文件、README 蓝图、DEV_PLAN 草案
- 验收断言：根目录存在 README.md/DEV_PLAN.md/LICENSE/.editorconfig/.gitignore/.nvmrc/.python-version/.env.example；六大目录存在且含占位
- 注意事项：无代码；无机密

### TASK002 后端骨架（FastAPI 占位规范）
- 版本号：v1.0
- 状态：计划中
- 文件与结构（不实现）：
  - backend/app/main.py（FastAPI 实例创建、CORS；/healthz GET→{"ok":true}）
  - backend/app/routers/{resumes,jobs,generate,exports,audit}.py（空路由占位）
  - backend/app/db/{engine.py,models.py,schema.py}（占位：SQLite/SQLAlchemy + Pydantic）
- 输入/输出示例：
  - GET /healthz → 200 {"ok": true}
- 验收断言（实现时）：
  - 启动成功；/healthz 返回 200/JSON schema 匹配
- AI 助手可执行提示词（保留供实现用，不在本次执行）：
```
You are an AI coding assistant. Implement FastAPI skeleton.
Prereqs: Poetry; run: poetry init -n; poetry add fastapi uvicorn[standard] pydantic sqlalchemy python-dotenv
Files:
- backend/app/main.py (create FastAPI app, enable CORS * for dev, add GET /healthz -> {"ok": true})
- backend/app/routers/__init__.py and empty routers for resumes, jobs, generate, exports, audit
- backend/app/db/engine.py (SQLite engine via DATABASE_URL), models.py, schema.py (placeholders)
Command: poetry run uvicorn app.main:app --reload --port ${API_PORT:-8000}
```

### TASK003 文档摄取与解析（含 OCR）
- 版本号：v1.0
- 状态：计划中
- 接口：POST /api/resumes（multipart/form-data）
  - 扩展名：pdf, docx, txt, md, jpg, jpeg, png
  - 限制：max_size_mb=20；max_files=1；mime 必须匹配扩展
  - 参数：tags[]=string（可选）、ocr=bool（默认读取 OCR_ENABLED）
- 处理流程/状态机：
  1) 校验与落盘 → 计算 sha256 → 新建 Resume 记录
  2) 若为图片或 PDF 且 OCR 开启 → OCR 文本
  3) 调用 LCEL 解析链 → 产出 ResumeSnapshot JSON
  4) 写入 snapshot 文件与 DB，记录语言与提取置信度
- ResumeSnapshot 结构（JSON 草案）：
```
{
  "name": "string",
  "contact": {"email": "string", "phone": "string", "location": "string"},
  "links": {"github": "string", "linkedin": "string"},
  "summary": "string",
  "skills": ["string"],
  "experiences": [{"company":"string","role":"string","start":"YYYY-MM","end":"YYYY-MM|Present","bullets":["string"]}],
  "education": [{"school":"string","degree":"string","graduation":"YYYY"}],
  "language": "zh|en",
  "source": {"file_path":"string","sha256":"string"}
}
```
- 成功响应（201）：{resumeId, snapshot:true}
- 失败示例：415/413/400（类型不支持/超大小/OCR 关闭但文件为图像）
- 验收断言：原文件与 snapshot.json 均存在；DB 中 Resume 与 Snapshot 均有记录；language 有值
- 计时记录：ingestion_ms, ocr_ms, parse_ms, total_ms
- AI 助手提示词（供实现）：
```
Implement ingestion+parse with LCEL.
Prereqs: poetry add langchain langchain-google-genai pdfplumber python-magic pytesseract
Steps: save file -> sha256 -> OCR if needed -> LCEL chain to extract fields -> write snapshot JSON -> DB rows
Paths: storage/resumes/{resumeId}/..., storage/audit/{resumeId}/snapshot_*.json
```

### TASK004 JD 规范化与生成接口（短答/封面信）
- 版本号：v1.0
- 状态：计划中
- JD 规范化：POST /api/jobs/normalize
  - 输入：{text:string} 或 文件（同上类型）
  - 输出（JSON）：{"role":"string","responsibilities":["string"],"requirements":["string"],"keywords":["string"],"language":"zh|en"}
- 短答生成：POST /api/generate/short
  - 输入：{resumeId, job:{text|normalized}, question: enum[why_company, why_you, biggest_achievement], language: auto|zh|en}
  - 规则：最终输出≤200 字符（单段纯文本，移除 Markdown/HTML）；语言按 i18n 策略
  - 成功：200 {genId, text}
  - 失败：404 无 snapshot；400 非法 question；502 模型错误
- 封面信生成：POST /api/generate/letter
  - 输入：{resumeId, job:{text|normalized}, style: enum[Formal,Warm,Tech] (default=Formal), paragraphs_max:int(1..7, default=5), target_words:int(200..700, default=400), include_keywords:[string], avoid_keywords:[string], language:auto|zh|en}
  - 输出：{genId, format: md|html (default=html), content:string, meta:{style,language,counts}}
  - 验收：content 结构包含：抬头、称呼、主体段落(<=paragraphs_max)、结尾签名；include/avoid 冲突→优先避免，并在 meta.notes 记录
- 计时记录：match_ms, generate_ms, total_ms；tokens_prompt/completion
- AI 助手提示词（供实现）：
```
Implement normalize+generate with LCEL (Gemini flash).
Prereqs: poetry add langchain langchain-google-genai tiktoken
Prompts: enforce max 200 chars for short (no Markdown); letter outputs semantic HTML (<header><main><section>...).
Parameters: style, paragraphs_max, target_words, include/avoid, language priority: user > JD > default.
```

### TASK005 HTML→PDF 导出
- 版本号：v1.0
- 状态：计划中
- 接口：POST /api/exports/letter/pdf
  - 输入：{genId?, html?, options:{page:"A4", margin_cm:2.0, line_height:1.35, header:{enabled:true,name,contact}, fonts:{en:["Inter","Times"], zh:["Noto Sans CJK","SimSun"]}}
  - 行为：优先 genId；否则用 html 直接渲染；保存至 storage/exports/{genId}/letter.pdf
  - 输出：application/pdf 字节流
- 验收断言：A4；边距=2.0cm（±1%）；行距≈1.35（±0.05）；字体可回退；页眉可开关
- 失败：400（无 html 且无 genId）；502（渲染器错误）
- 计时记录：render_ms, total_ms
- AI 助手提示词（供实现）：
```
Prereqs: playwright install chromium; poetry add playwright
Render HTML with Chromium headless; inject CSS variables for page size/margins/line-height/fonts.
```

### TASK006 审计与复现
- 版本号：v1.0
- 状态：计划中
- 记录内容（DB + JSON 文件）：
  - genId, resumeId, job_hash, type: short|letter
  - model_provider/name, temperature/top_p/penalties, seed
  - params: style/paragraphs_max/target_words/include/avoid/language
  - prompt_full（完整提示词）、tokens_prompt/completion（可选）
  - timings：见全局计时字段；timestamp
  - outputs：text/html 路径与摘要（前 120 字）
- 接口：GET /api/audit/{genId} → 返回上述结构
- 复现原则：同一 provider/model + 相同 seed/params → 期望输出相似（非完全一致）
- 验收断言：生成后可立即查询到审计；导出 JSON 与 DB 一致
- AI 助手提示词（供实现）：
```
Design ORM & Pydantic schemas; persist audit rows and write JSON snapshot per generation under storage/audit/{genId}. Capture timings and full prompt.
```

---

## v2.0 / v3.0 提示
- 维持原有目录与任务占位，不在本版细化到可执行级。

## 版本与分支策略（文档化）
- 主分支：main；命名：feat/*、fix/*、chore/*、docs/*、refactor/*、release/*
- 前端包管理：pnpm；后端依赖：Poetry

## 环境与运行（文档化）
- Node：.nvmrc = v20；Python：.python-version = 3.11
- 环境变量：见 `.env.example`
