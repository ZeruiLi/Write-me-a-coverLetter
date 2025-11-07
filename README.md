# Write me a Cover Letter

面向个人求职者的一站式 Cover Letter 生成应用。支持上传多格式简历与输入职位描述，后端基于 LangChain（LCEL）完成识别、分析、抽取、匹配与生成，输出两类结果：
- 短答（200 字以内纯文本），用于快速问答如“Why you want to join our company?”
- 完整封面信（结构完整、精美排版），支持导出 PDF

本仓库为 monorepo，仅包含蓝图与结构占位（初始提交不含可运行代码）。

## 架构蓝图（Blueprint）

- 前端（frontend/）
  - 技术：React + Vite；样式：Tailwind CSS；组件库：Headless UI
  - 设计：极简技术风；主色 `#0EA5E9`；深灰文字；暗色模式可选
  - UI 规范：A4 风格预览面板；固定侧栏（历史简历/证据）；主工作区（编辑/预览）
- 后端（backend/）
  - 技术：Python + FastAPI；AI 编排：LangChain（LCEL）
  - 模型：首选 Gemini-2.5-flash；预留 Qwen 等适配位
  - 存储：本地文件系统 + SQLite 元数据（简历文件、解析快照、标签、审计）
  - 导出：HTML 模板渲染 → 无头浏览器（Chromium）转 PDF
- 边界
  - 前后端分离；仅本地程序接入云端大模型 API；信息安全非重点

## 关键能力

1) 简历上传与解析
- 支持 PDF、DOCX、TXT、MD；图片简历（JPG/PNG）支持 OCR（默认开启，可关闭）
- 中/英双语解析；自动随 JD 语言切换，用户可覆盖
- 解析产物：基础资料、教育/经历/技能要点、时间线、量化指标

2) 职位描述规范化
- 输入文本/文件；抽取角色、职责、要求、关键词、语言

3) 匹配与生成
- 短答问题集（可配置）：
  - Why you want to join our company?（≤200 字）
  - Why you?（≤200 字）
  - Biggest achievement related to this role?（≤200 字）
- 封面信：风格档（Formal/Warm/Tech）；参数（段落上限、目标字数、关键词必含/避免、语言）

4) 历史复用与审计
- 简历库：按文件名、时间、标签（如 “MLE/SWE/实习”）检索
- 审计：记录模型/版本、温度/惩罚、完整提示词、种子、时间戳、输入摘要（哈希）

5) 导出
- Markdown/HTML 预览；PDF 导出（A4，边距 2.0cm，行距 1.35；字体优先级：英文字体 Inter/Times，中文 思源黑体/宋体；页眉含姓名与联系方式可关闭）

## 数据与实体
- Resume：id、文件路径、文件哈希、文件类型、语言、标签、创建/更新时间
- ResumeSnapshot：解析快照 JSON、提取时间、版本
- JobRecord：原文、语言、解析摘要、时间（可选持久）
- Generation：类型（short/letter）、参数（风格、温度、语言、种子）、模型信息、输入哈希、输出摘要、产物路径

## API 轮廓（REST）
- POST /api/resumes（上传） | GET /api/resumes（列表） | GET /api/resumes/{id}
- POST /api/jobs/normalize（JD 规范化）
- POST /api/generate/short（短答生成）
- POST /api/generate/letter（封面信生成）
- POST /api/exports/letter/pdf（HTML→PDF）
- GET /api/audit/{genId}（审计详情）

## 目录结构（monorepo）
```
frontend/    # React + Vite + Tailwind + Headless UI（后续添加）
backend/     # FastAPI + LangChain（后续添加）
storage/     # 本地文件存储（resumes/ exports/ audit/）
templates/   # HTML/CSS 模板（Formal/Warm/Tech）
docs/        # 设计/路线图/规范文档
scripts/     # 辅助脚本
```

## 运行与环境（蓝图）
- Node 18+/20（.nvmrc = v20）、Python 3.11（.python-version = 3.11）
- 环境变量示例：见 `.env.example`
- 包管理：前端 pnpm；后端 Poetry（锁定依赖与虚拟环境一致性）

## 分支与规范
- 主分支：main
- 分支命名：feat/*、fix/*、chore/*、docs/*、refactor/*、release/*（文档化，不设保护）
- 规范化文件：.editorconfig、.gitignore、LICENSE（MIT）

## 路线图
- v1.0 最小可用：上传简历 + 输入 JD → 生成短答 / 封面信（PDF）
- v2.0 体验增强：标签/检索、模板系统化、审计可视化、稳定性提升
- v3.0 扩展：多用户命名空间、模型适配矩阵、A/B 实验、插件化模板

---
本 README 为蓝图与范围约束，指导后续迭代开发与验收，不包含实现细节。
