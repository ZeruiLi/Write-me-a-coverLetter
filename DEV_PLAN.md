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
- Node v18+（推荐 v20；.nvmrc 提供建议版本），包管理优先 pnpm（若无 pnpm，可使用 npm）
- Python 3.11（.python-version），Poetry
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

## 前端规范（v1.0）

技术栈与约束
- React 18 + Vite + TypeScript；包管理：pnpm
- UI：Tailwind CSS + Headless UI；主色 `#0EA5E9`；暗色模式可选
- 状态管理：Zustand（轻量全局状态：所选 resume、JD 文本、生成参数、界面语言）
- 国际化：i18next + react-i18next（zh/en），默认随系统，支持手动切换
- 网络：axios；基地址 `VITE_API_BASE_URL`（默认 `http://localhost:8000`）

目录结构（可执行级）
```
frontend/
  index.html
  vite.config.ts
  tsconfig.json
  tailwind.config.ts
  postcss.config.js
  .env.example              # VITE_API_BASE_URL
  src/
    main.tsx
    App.tsx
    styles/tailwind.css
    api/client.ts           # axios 实例与拦截器（错误映射）
    api/types.ts            # 与后端 Schemas 对齐的 TS 类型
    store/index.ts          # zustand：resumeId、jd、params、lang 等
    i18n/index.ts           # i18n 初始化 & 资源加载
    i18n/locales/en/common.json
    i18n/locales/zh/common.json
    routes/Library.tsx      # 简历库：上传/列表/筛选
    routes/Compose.tsx      # 组合：参数侧栏 + A4 预览
    routes/Questions.tsx    # 短答问答
    components/UploadDropzone.tsx
    components/ResumeCard.tsx
    components/TagFilter.tsx
    components/StyleSelector.tsx
    components/LanguageSwitch.tsx
    components/A4Preview.tsx
```

类型与契约（api/types.ts，摘录）
```
export type ResumeOut = { id:number; fileName:string; tags:string[]; lang?:'zh'|'en'; createdAt:string };
export type JobNormalized = { role?:string; responsibilities:string[]; requirements:string[]; keywords:string[]; language?:'zh'|'en' };
export type GenerateShortRequest = { resumeId:number; job: JobNormalized|Record<string,unknown>; question:'why_company'|'why_you'|'biggest_achievement'; language:'auto'|'zh'|'en' };
export type GenerateShortResponse = { genId:number; text:string };
export type GenerateLetterRequest = { resumeId:number; job: JobNormalized|Record<string,unknown>; style:'Formal'|'Warm'|'Tech'; paragraphs_max:number; target_words:number; include_keywords:string[]; avoid_keywords:string[]; language:'auto'|'zh'|'en'; format:'html'|'md' };
export type GenerateLetterResponse = { genId:number; format:'html'|'md'; content:string; meta:{ style:string; language:string; counts:Record<string,number>; notes?:string } };
export type ExportPDFRequest = { genId?:number; html?:string; options?:Record<string,unknown> };
```

API 客户端（api/client.ts，函数清单）
- listResumes(): GET /api/resumes → Promise<ResumeOut[]>
- uploadResume(file:File, tags?:string[]): POST /api/resumes → {resumeId:number}
- normalizeJob(text:string): POST /api/jobs/normalize → JobNormalized
- generateShort(payload:GenerateShortRequest): POST /api/generate/short → GenerateShortResponse
- generateLetter(payload:GenerateLetterRequest): POST /api/generate/letter → GenerateLetterResponse
- exportPDF({genId?, html?}): POST /api/exports/letter/pdf → Blob（优先 genId；若后端未持久化 HTML 则使用 html 兜底）
- getAudit(genId:number): GET /api/audit/{genId}
注意：HTTP 错误码与提示映射
- 400 参数错误 → toast("参数有误")
- 404 不存在 → toast("资源不存在或已删除")
- 413 文件过大 → toast("文件超过大小限制")
- 415 类型不支持 → toast("不支持的文件类型")
- 502 模型/渲染错误 → toast("服务繁忙或模型异常，请重试")

UI 规范与流程
- Library：
  - 顶部上传（拖拽/点击），显示上传进度
  - 列表（文件名/时间/标签/语言），支持搜索和标签过滤
  - 选择一份简历后，跳转 Compose 并在全局 store 保存 resumeId
- Compose：
  - 左侧参数：style、paragraphs_max(1..7)、target_words(200..700)、include/avoid、language(auto/zh/en)
  - 右侧 A4 预览：
    - 生成 letter 后渲染 HTML；
    - 打印样式：A4、边距 2cm、行距 1.35；字体回退与暗色兼容
  - 导出 PDF：优先 genId；若失败则以当前预览 HTML 调用导出
- Questions：
  - 下拉选择问题枚举；
  - 点击生成短答（展示字符统计，若>200 给出提示但不强制截断）

样式与可访问性
- Tailwind 配置主色 `#0EA5E9`，支持暗色 `media` 或 `class` 模式
- A4Preview 提供打印专用类名（@media print）与屏幕预览边框/阴影
- 组件交互（按钮/输入/切换）均提供 aria 属性与键盘可达性

构建与运行
- .env.example：`VITE_API_BASE_URL=http://localhost:8000`
- 使用 pnpm（优先）
  - `pnpm install`
  - `pnpm dev`（本地开发，端口 5173）
  - `pnpm build && pnpm preview`
- 若本机无 pnpm，可用 npm 作为临时替代
  - `npm install`（会生成 package-lock.json）
  - `npm run dev` / `npm run build` / `npm run preview`
  - 或使用 corepack：`corepack enable` 后 `pnpm`

验收标准（v1.0 前端）
- 能完成“上传 → 列表 → 选择 → 生成 letter → 预览 → 导出 PDF”的最短闭环
- Questions 页面可生成 3 个预置问题之一的短答并展示
- 错误码映射提示准确；加载/禁用/重试状态明确
- i18n 切换后 UI 文案实时更新；默认随系统语言


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

### TASK007 前端脚手架与基础视图
- 版本号：v1.0
- 状态：计划中
- 子任务（可执行级）：
  1) 脚手架：`pnpm create vite@latest frontend -- --template react-ts`；安装与配置 Tailwind/Headless UI（暗色+主色）
  2) 目录与文件：按“前端规范（v1.0）”创建 `src/*`、`tailwind.config.ts`、`postcss.config.js`、`.env.example`
  3) API 客户端与类型：`api/client.ts`、`api/types.ts`（对齐后端 Schemas）；封装错误映射
  4) 路由与页面：`routes/Library.tsx`、`Compose.tsx`、`Questions.tsx`；顶部导航与 LanguageSwitch
  5) 组件：UploadDropzone、ResumeCard、TagFilter、StyleSelector、A4Preview
  6) Store：Zustand 保存 resumeId、jd、params、language；开启 localStorage 持久化
  7) 集成流程：完成“上传→列表→生成 letter→预览→导出 PDF”闭环；Questions 生成短答
  8) i18n：初始化 en/zh 文案；默认随系统语言；提供切换控件
  9) 文档：在 `frontend/README.md` 补充运行说明与命令（dev/build/preview）
- 依赖（前端）：react, react-dom, typescript, vite, axios, zustand, tailwindcss, postcss, autoprefixer, @headlessui/react, i18next, react-i18next
- 验收清单：
  - `pnpm dev` 可启动；各页面加载无报错
  - 能与后端完成闭环（至少使用 html 方式导出 PDF）
  - 错误码映射准确；i18n 切换生效
- AI 助手可执行提示词：
```
Scaffold a React+Vite+TS app under frontend/ with Tailwind+Headless UI and Zustand.
Add api/client.ts with axios (baseURL from VITE_API_BASE_URL) and error mapping for 400/404/413/415/502.
Implement routes: Library (upload/list), Compose (params panel + A4 preview), Questions (short answers).
Implement components: UploadDropzone, ResumeCard, TagFilter, StyleSelector, LanguageSwitch, A4Preview.
Wire to backend endpoints described in DEV_PLAN; export PDF using html if genId-only export fails.
```

---

## v2.0 / v3.0 提示
- 保持占位，待 v1.0 完成后再细化。

---

## LLM-First Extraction Workflow（A/B/C/D）— v1.1 规范补充

目标与边界（依据最新决策）
- 模型必须原生支持“文件上传与识别”；如不支持，直接报错（不做降级/折衷）。
- 证据指针使用“全局字符区间”（start,end）基于规范化锚文本定位；前端高亮非 v1.0 强制。
- 抽取范围限定：硬技能、项目/经验中的可度量成果（AOM：Action/Outcome/Metric）、教育背景。
- 亮点选择全自动（≤3 条），本轮不提供人工 override。
- 抽取失败（JSON 不合规/缺关键字段）即 422 报错，让用户修正后重试。
- 审计与版本化：存“文档版本”与“抽取 prompt/提示版本”，并行共存可检索。

数据契约（C 点存储对象）
- ResumeObjectV1（JSON）
  - basics: { name, email, phone, location }
  - hard_skills: string[]
  - experiences: Array<{ title, company, period: { start, end }, bullets: Array<{ id:string, action, outcome, metric, evidence: { start:int, end:int, anchor_sha256:string } }> }>
  - education: Array<{ school, degree, graduation }>
  - language: 'zh'|'en'
  - meta: { source: { doc_version_id, file_sha256, mime }, extract_version: string, prompt_version: string, model: string }
- JDObjectV1（JSON）
  - role: string
  - company: string
  - must_have_skills: string[]
  - nice_to_have_skills: string[]
  - responsibilities: string[]
  - challenges: string[]
  - language: 'zh'|'en'
  - jd_unique_terms: string[]
  - meta: 同上
- AnchorTextV1（规范化锚文本，仅用于指针定位）
  - anchor_sha256: string
  - text: string  // 规范化后的纯文本
  - doc_version_id: number
- CoverPlanV1（规划）
  - opening: { company, role, hook: string }
  - why_me: Array<{ evidence_id: string, line: string }>  // ≤3，引用 ResumeObjectV1.bullets[*].id
  - why_you: { focus_points: string[] }
  - cta: string
  - language: 'zh'|'en'
- Audit 元数据（全链路）
  - 每步：input_hash、prompt_version、model/params、timings、tokens、outputs_sha、status

后端模块与文件
- providers/filecapable.py
  - FileCapableLLM 接口：upload(file)->file_token；generate(prompt, files:[token], params)->text/json
  - GeminiFileCapable 实现；若当前模型不支持文件 → raise 501 provider_no_file_support
- chains/extract_resume.py（LCEL + PydanticOutputParser）
  - 入：file_token，language_hint，prompt_version
  - 出：ResumeObjectV1（严格 JSON）
  - 失败：422 schema_invalid
- chains/extract_jd.py（LCEL + PydanticOutputParser）
  - 入/出 类似，产出 JDObjectV1
- services/anchor.py
  - 生成 AnchorTextV1（规范化文本）；对 evidence.quote 做对齐 → evidence.{start,end,anchor_sha256}
- chains/plan_letter.py → CoverPlanV1（≤3 why_me, 仅证据引用）
- chains/generate_letter.py → HTML（语义结构；不得新增事实数字）
- guardrails/validate.py → 校验：每段≤3行、禁词、≥1 个 jd_unique_terms、证据 ID 存在、数字来自证据

数据库与版本化（新增/扩展表）
- documents(id, kind)
- document_versions(id, document_id, file_sha256, mime, uploaded_at)
- anchor_texts(id, doc_version_id, anchor_sha256, text)
- extraction_runs(id, doc_version_id, kind, prompt_version, model, params_json, status, created_at)
- resume_objects(id, doc_version_id, extract_version, prompt_version, model, json, created_at)
- jd_objects(id, doc_version_id, extract_version, prompt_version, model, json, created_at)
- generation_runs(id, resume_obj_id, jd_obj_id, plan_json_sha, html_sha, model, params_json, timings_json, created_at)

API（A/B/C/D）
- A：POST /api/extract/resume
  - form: file；header: x-prompt-version（可选）
  - 返：{ resumeObjId, docVersionId, extract_version, prompt_version }
  - 错：501/415/422
- B：POST /api/extract/jd（同上）
- C：GET /api/resume_objects/{id}；GET /api/jd_objects/{id}
- D：POST /api/generate/letter2
  - body: { resumeObjId, jdObjId, style, language:'auto'|'zh'|'en', params:{ paragraphs_max, target_words } }
  - 流程：plan → generate → validate → persist → 返回 { genId, html }
  - 错：422 guardrail_failed/schema_invalid

Prompt 提纲（v1）
- ResumeExtract：严格 JSON（ResumeObjectV1），bullets 必含 AOM 与 evidence.quote
- JDExtract：严格 JSON（JDObjectV1），需产出 jd_unique_terms
- Plan：四段式规划，仅引用 evidence_id，≤3 条 why_me
- Generate：按规划输出语义 HTML（header/main/section/footer），每段≤3行，语言按策略

错误策略
- 501 provider_no_file_support（模型不支持文件上传）
- 422 schema_invalid（抽取 JSON 校验失败）
- 422 guardrail_failed（受控校验不通过）
- 400 bad_request；415 unsupported_media_type

审计与可复现
- 记录每步 prompt_version、完整提示词、模型与参数、timings、tokens、inputs/outputs 摘要；同文档多版本并存；latest 指针

测试方法
- 合同测试：PDF/DOCX/TXT/OCR 图片上传；501/422/415 错误路径
- 结构化测试：对象 JSON Schema 校验；evidence 指针切片与 quote 一致
- 端到端：extract(resume)+extract(jd) → letter2 → PDF 导出

实施清单（新增任务）

### TASK008 文件能力 Provider（必需）
- 版本：v1.1｜状态：计划中
- 子任务：
  1) 新增 FileCapableLLM 接口与 GeminiFileCapable 实现
  2) 检测不支持文件模型 → 501 provider_no_file_support
  3) 审计：记录模型/版本与文件 token 数
- 验收：不支持模型时准确报错；支持模型能返回 token 并生成
- AI 助手提示词：
```
Implement FileCapableLLM (upload/generate) using Gemini SDK; raise 501 if model lacks file support; add unit tests for both paths.
```

### TASK009 简历抽取 API（A 点）
- 版本：v1.1｜状态：计划中
- 子任务：
  1) POST /api/extract/resume：接收 file，调用 extract_resume 链
  2) PydanticOutputParser 强校验；422 on invalid
  3) 生成 AnchorTextV1；对齐 evidence 指针（start,end,anchor_sha256）
  4) 持久化 resume_object 与 extraction_runs
- 验收：返回 resumeObjId；不合规时 422；不支持文件时 501
- AI 助手提示词：
```
Build extract_resume chain producing ResumeObjectV1; validate JSON; align evidence pointers over normalized anchor text; persist with version info.
```

### TASK010 JD 抽取 API（B 点）
- 版本：v1.1｜状态：计划中
- 子任务：与 TASK009 对称，实现 JDObjectV1 与持久化
- 验收：返回 jdObjId；422/501 错误路径正确
- AI 助手提示词：
```
Build extract_jd chain producing JDObjectV1 with jd_unique_terms; strict validation and persistence.
```

### TASK011 锚文本与证据指针
- 版本：v1.1｜状态：计划中
- 子任务：
  1) services/anchor：生成标准化文本并保存 AnchorTextV1
  2) 对 evidence.quote 定位为全局字符区间；无法定位即报错
- 验收：evidence.{start,end} 切片与 quote 完全一致
- AI 助手提示词：
```
Implement anchor normalization and quote alignment; produce {start,end,anchor_sha256}; add tests to assert exact slice match.
```

### TASK012 规划与受控生成（D 点 letter2）
- 版本：v1.1｜状态：计划中
- 子任务：
  1) plan_letter：输出 CoverPlanV1（≤3 why_me，仅证据引用）
  2) generate_letter：按规划生成语义 HTML；禁止新增事实数字
  3) guardrails：段落≤3行、禁词、≥1 个 jd_unique_terms、证据/数字校验
  4) API：POST /api/generate/letter2；持久化 HTML 与审计
- 验收：合格 HTML 返回；违反规则时 422 guardrail_failed
- AI 助手提示词：
```
Implement plan->generate->validate pipeline; enforce constraints; return 422 on guardrail failure; persist outputs with audit.
```

### TASK013 DB 扩展与版本化审计
- 版本：v1.1｜状态：计划中
- 子任务：新增/迁移上述表；latest 指针与查询
- 验收：同一 doc_version 支持多抽取版本共存；可按 prompt_version 检索
- AI 助手提示词：
```
Add DB tables & migrations; expose queries by doc_version and prompt_version; ensure referential integrity.
```

### TASK014 合同与端到端测试
- 版本：v1.1｜状态：计划中
- 子任务：
  1) 合同测试：PDF/DOCX/TXT/OCR 错误路径（501/422/415）
  2) 结构化测试：Schema 校验与 evidence slice 一致性
  3) E2E：extract(resume)+extract(jd) → letter2 → PDF
- 验收：测试全部通过；关键错误路径可复现
- AI 助手提示词：
```
Write contract & E2E tests covering success and failure paths; assert evidence pointer correctness.
```

### TASK015 前端对接（可选）
- 版本：v1.1｜状态：计划中
- 子任务：Compose 调整为调用 extract→letter2；保留旧流兼容；显示基础错误提示
- 验收：最短闭环成功；错误码（501/422/415）指引清晰
- AI 助手提示词：
```
Wire frontend to new endpoints; update .env as needed; keep legacy flow as fallback toggle (dev only).
```
