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
- 上传原文件：`storage/resumes/{resumeId}/{original_filename}`
- 解析快照：`storage/audit/{resumeId}/snapshot_{iso}.json`
- 生成产物：`storage/exports/{genId}/letter.html|letter.pdf|short.txt`
- 标识符：`resumeId`/`genId` 采用 `yyyyMMddHHmmss_{8位随机}` 或 DB 自增 id；同时存储 sha256 文件指纹

i18n 策略
- 输出语言优先级：用户手动选择（若设置）> JD 自动识别语言 > DEFAULT_OUTPUT_LANG

可观测性与计时字段（v1.0 必须记录，暂不设 SLO）
- timings：ingestion_ms、ocr_ms、parse_ms、match_ms、generate_ms、render_ms、total_ms
- model：model_provider、model_name、temperature、top_p、penalties、seed
- tokens：tokens_prompt、tokens_completion（若可得）
- inputs：input_hash（简历/JD 摘要哈希，sha256 前 12 位）
- 其他：timestamp、request_id
- JSON 示例：
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

依赖管理（Poetry 运行时）
- fastapi, uvicorn[standard], pydantic, sqlalchemy, python-dotenv
- langchain, langchain-core, langchain-google-genai
- pdfplumber, python-multipart, pillow, pytesseract, python-magic, langdetect, tenacity
- playwright（用于 HTML→PDF）
- 可选/后续：alembic, structlog

---

## 目录与组件（后端）
- backend/app/main.py — FastAPI 实例与路由注册、CORS、/healthz
- backend/app/core/config.py — 环境加载（env→Settings），含默认值与校验
- backend/app/core/errors.py — `AppError(code,http,msg)` 与全局异常处理器
- backend/app/core/logging.py — 日志初始化（可延后）
- backend/app/db/engine.py — SQLAlchemy Engine/Session/Base 初始化
- backend/app/db/session.py — `get_session()` 依赖注入
- backend/app/db/models.py — ORM：Resume, ResumeSnapshot, Generation
- backend/app/schemas/{resume,job,generate,export,audit}.py — Pydantic 模型
- backend/app/routers/{resumes,jobs,generate,exports,audit}.py — REST 路由
- backend/app/services/{ingestion,ocr,detect,parsing,matching,generation,render,audit}.py — 领域服务
- backend/app/providers/{base.py,gemini.py} — LLM Provider 接口与实现
- backend/app/prompts/{short.txt,letter.txt,normalize.txt} — Prompt 模板

---

## 数据模型（ORM 简化定义）
- Resume：
  - id:int PK, file_path:str, file_name:str, sha256:str, mime:str, lang:str, tags:JSON(list[str]), created_at:datetime
- ResumeSnapshot：
  - id:int PK, resume_id:int FK, data:JSON, lang:str, created_at:datetime
- Generation：
  - id:int PK, resume_id:int FK, job_hash:str, type:str('short'|'letter'), provider:str, model:str,
  - temperature:float, top_p:float, seed:int, params:JSON, prompt:str, timings:JSON, tokens:JSON,
  - output_path:str, output_summary:str, created_at:datetime

## Schemas（Pydantic 主要签名）
- ResumeCreateResponse { resumeId:int, snapshot:bool }
- ResumeOut { id:int, fileName:str, tags:list[str], lang:str, createdAt:str }
- JobNormalizeRequest { text?:str } | multipart(file)
- JobNormalized { role:str, responsibilities:list[str], requirements:list[str], keywords:list[str], language:Literal['zh','en'] }
- GenerateShortRequest { resumeId:int, job:{text?:str, normalized?:JobNormalized}, question:Literal['why_company','why_you','biggest_achievement'], language:Literal['auto','zh','en']='auto' }
- GenerateShortResponse { genId:int, text:str }
- GenerateLetterRequest { resumeId:int, job:{...}, style:Literal['Formal','Warm','Tech']='Formal', paragraphs_max:int=5 (1..7), target_words:int=400 (200..700), include_keywords:list[str]=[], avoid_keywords:list[str]=[], language:'auto'|'zh'|'en'='auto', format:Literal['html','md']='html' }
- GenerateLetterResponse { genId:int, format:'html'|'md', content:str, meta:{style,language,counts,notes?:str} }
- ExportPDFRequest { genId?:int, html?:str, options:{ page:'A4', margin_cm:float=2.0, line_height:float=1.35, header:{enabled:bool,name?:str,contact?:str}, fonts:{en:list[str], zh:list[str]} } }
- AuditResponse { 与 Generation 字段对齐，含 outputs 路径与摘要 }

---

## Provider 接口与 LCEL 链（概念与签名）
- providers/base.py
  - `class LLMProvider(Protocol):`
  - `def generate(self, prompt:str, temperature:float=0.6, top_p:float=1.0, seed:int=0, **kw)->str`
- providers/gemini.py
  - `class GeminiProvider(LLMProvider):`
  - `def __init__(self, api_key:str, model:str='gemini-2.5-flash')`
- LCEL 链（parsing/normalize/short/letter）：从 `prompts/*.txt` 注入参数；`langdetect` 决策语言；对短答强制长度与纯文本；对封面信输出语义 HTML

---

## 服务层函数签名
- services/ingestion.py
  - `def save_upload(file:UploadFile, dst_dir:Path)->tuple[Path,str]`  # 返回落盘路径与 sha256
  - `def allowed_ext(filename:str)->bool`
- services/ocr.py
  - `def ocr_image(path:Path, lang:str='chi_sim+eng')->str`
  - `def ocr_pdf(path:Path, lang:str='chi_sim+eng')->str`
- services/detect.py
  - `def detect_lang(text:str)->Literal['zh','en']`
- services/parsing.py
  - `def build_parse_chain(provider:LLMProvider)->Runnable`
  - `def parse_resume(text:str, meta:dict, provider:LLMProvider)->dict`  # 输出 ResumeSnapshot JSON
- services/matching.py
  - `def extract_keywords(text:str)->list[str]`
  - `def score_match(resume_snapshot:dict, jd:dict)->dict`  # 关键点对齐（可简化）
- services/generation.py
  - `def short_answer(resume_snap:dict, jd:any, question:str, lang:str, params:dict, provider:LLMProvider)->tuple[str,dict]`
  - `def letter(resume_snap:dict, jd:any, params:dict, provider:LLMProvider)->tuple[str,dict]`
- services/render.py
  - `def html_template(style:str, payload:dict)->str`  # 可选：非 LLM 渲染路径
  - `def html_to_pdf(html:str, options:dict)->bytes`
- services/audit.py
  - `def record_generation(db, gen:Generation)->None`
  - `def get_audit(db, gen_id:int)->dict`  # 返回 AuditResponse

---

## REST 端点契约（FastAPI）
- POST /api/resumes — 上传简历
  - form：file, tags?[], ocr?（bool）
  - 201 `{resumeId, snapshot:true}`；错误：415/413/400
- GET /api/resumes — 列表/筛选
  - query：q?（文件名/标签），limit?，offset?
  - 200 `list[ResumeOut]`
- POST /api/jobs/normalize — JD 规范化
  - 入：`{text}` 或文件
  - 出：`JobNormalized`
- POST /api/generate/short — 短答
  - 入：`GenerateShortRequest`
  - 出：`GenerateShortResponse`
  - 约束：最终≤200 字符，去除 Markdown/HTML
- POST /api/generate/letter — 封面信
  - 入：`GenerateLetterRequest`
  - 出：`GenerateLetterResponse`
  - 约束：结构包含抬头/称呼/主体(≤paragraphs_max)/签名；include/avoid 冲突→优先避免并记录 meta.notes
- POST /api/exports/letter/pdf — 导出 PDF
  - 入：`ExportPDFRequest`（优先 genId）
  - 出：application/pdf；保存 `storage/exports/{genId}/letter.pdf`
- GET /api/audit/{genId} — 审计详情
  - 出：`AuditResponse`
- GET /healthz — 健康检查

---

## 关键流程/状态机
- 上传→解析
  1) 校验扩展名/大小 → 落盘 → sha256
  2) 文本提取：txt/md 直读；docx→python-docx；pdf→pdfplumber 或 OCR；image→OCR
  3) detect_lang → build_parse_chain → parse_resume → snapshot JSON
  4) DB：插入 Resume 与 Snapshot；保存 snapshot 文件
  5) 写入 timings：ingestion/ocr/parse/total
- 生成（短答/封面信）
  1) 读取 Snapshot + JD（原文或规范化）
  2) 构造 prompt（风格/长度/关键词/语言优先级）
  3) provider.generate（重试与超时）→ 输出文本/HTML
  4) 保存 Generation（prompt/params/timings/tokens/摘要）；写入 exports（text/html）
- 导出 PDF
  1) 有 genId：取 HTML；否则使用请求 html
  2) Playwright 渲染 → 保存 → 返回
- 审计
  1) DB + JSON 快照聚合
  2) 返回结构化详情（含复现关键参数）

---

## 错误处理与日志
- HTTP 状态：400（参数）/404（不存在）/413（超限）/415（类型）/502（LLM/PDF 错）
- 统一异常：`AppError(code,http,msg)`；全局异常处理器输出 `{code, message, detail?}`
- 请求日志：request_id、path、status、total_ms；服务内部阶段性 timings 聚合到 Generation.timings

---

## 前端最小对接（v1.0）
- 结构：`frontend/src/{main.tsx, App.tsx, routes/{Library.tsx,Compose.tsx,Questions.tsx}, components/{A4Preview.tsx,UploadDropzone.tsx,StyleSelector.tsx,LanguageSwitch.tsx}, api/client.ts}`
- 配置：`.env` `VITE_API_BASE_URL=http://localhost:8000`
- 流程：
  - Library：上传（POST /api/resumes）、列表（GET /api/resumes）
  - Compose：参数面板（style/paragraphs/words/keywords/lang）→ 生成 letter（/api/generate/letter）→ 预览 HTML → 导出 PDF
  - Questions：选择问题 → /api/generate/short → 显示文本

---

## 测试方法（v1.0）
- 单元：schemas 校验、allowed_ext/sha256、detect_lang、简单 matching
- 合同：使用 httpx/pytest 对 REST 端点进行契约测试（200/4xx/5xx）
- 假数据：`docs/` 提供示例简历与 JD；编排 E2E：上传→规范化→短答/封面信→导出→查询审计

---

## v1.0 任务清单（可执行级）

### TASK001 仓库初始化与骨架（完成）
- 验收：根文件与目录存在；不含可运行代码；README/DEV_PLAN 就绪

### TASK002 后端骨架
- 文件：见“目录与组件（后端）”列出的最小文件集合
- 依赖：Poetry 添加 fastapi/uvicorn/pydantic/sqlalchemy/python-dotenv
- 端点：GET /healthz 200→{"ok":true}
- 验收：启动成功；/healthz 响应 Schema 正确
- AI 助手提示词：
```
Implement FastAPI skeleton with Poetry.
Create files per plan; enable CORS(*); add GET /healthz; add config loader.
```

### TASK003 文档摄取与解析（含 OCR）
- 端点：POST /api/resumes；快照 Schema 见“ResumeSnapshot 结构”
- 依赖：langchain, langchain-google-genai, pdfplumber, python-multipart, pillow, pytesseract, python-magic, langdetect
- 验收：原文件与 snapshot.json 存在；DB 两表写入；language 有值；timings 记录
- 失败示例：415/413/400
- AI 助手提示词：
```
Implement ingestion+OCR+LCEL parse; save under storage/*; write DB and JSON snapshot; record timings.
```

### TASK004 JD 规范化与生成
- 端点：/api/jobs/normalize, /api/generate/short, /api/generate/letter
- 依赖：langchain, langchain-google-genai
- 约束：短答≤200 字符纯文本；封面信语义 HTML；语言优先级按 i18n 规则
- 验收：响应结构正确；计时与 tokens（若可得）记录；include/avoid 冲突处理落入 meta.notes
- AI 助手提示词：
```
Build LCEL chains for normalize/short/letter; enforce length & structure; persist Generation rows & files.
```

### TASK005 HTML→PDF 导出
- 端点：/api/exports/letter/pdf；优先 genId
- 依赖：playwright（Chromium）
- 验收：A4；2.0cm；≈1.35；字体回退；页眉可开关
- AI 助手提示词：
```
Render HTML to PDF via Chromium; inject CSS variables; save under storage/exports/{genId}/.
```

### TASK006 审计与复现
- 端点：GET /api/audit/{genId}
- 验收：生成后可立即查询；DB 与 JSON 一致
- AI 助手提示词：
```
Persist full prompt, params, timings, tokens; provide audit API and JSON export.
```

---

## v2.0 / v3.0 提示
- 保持占位，待 v1.0 完成后再细化。
