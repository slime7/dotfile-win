# Agent 工作流与系统架构参考

本文档详述源自成熟生产级实践的高效 Agent 驱动开发（Agent-Driven Development）工作流、架构分层体系以及配套的工程保障机制。当为项目初始化或升级 Agent 文档体系时，应参照本架构为目标项目复现完整的流程和规范。

## 核心设计理念

- **文件系统作为单一事实来源（Filesystem as Single Source of Truth）**：
  项目所有配置、文档、规则与数据都以明文文件（Markdown / YAML / JSON）存储在仓库中。Agent 决策和行动完全依赖仓库内的静态文件与版本历史，不依赖外部黑盒记忆。
- **约定优于配置（Convention over Configuration）**：
  规范化文件命名、字段名称、目录结构与错误协议。规范越标准化，上下文消耗越低，多 Agent 协同的摩擦越小。
- **闭环自驱动循环（Autonomous Dispatch & Execution Loop）**：
  Agent 具备明确的“认领任务 → 实施与 TDD 验证 → 质量门禁校验 → 提交并直接推送 → 汇报并自派发下一任务”的完整自治生命周期。
- **渐进式质量门禁（Layered Quality Gates）**：
  轻量级校验（Lint / Format）前置至提交（Pre-commit），重量级分析（全量构建、测试覆盖率、代码健康度、安全与静态分析、核心冒烟）置于推送（Pre-push），云端流水线负责交叉验证与发布。

---

## 1. 任务流转与生命周期（Task Lifecycle）

在支持 Agent 自治协同的架构中，任务队列是协调人和多个 Agent 的唯一总线：

### 状态机定义
```text
[Backlog / 需求池]
       │
       ▼
    [Open] ───────────────┐
       │ (优先选择)       │ (普通选择)
       ▼                 ▼
[To Rework / 待返工] ──► [In Progress / 推进中]
                         │
                         ▼ (测试通过 & 质量门禁全绿 & git push 成功)
                   [In Review / 待人工验收]
                         │
                         ▼ (人工 QA / 合并确认)
                   [Done / 已完成]
```

### 状态流转规则
- **防碰撞声明（Claim Gate）**：Agent 在开始写代码前，必须先将任务移至 In Progress，并在任务中评论简要方案（例如：`🚀 正在开始处理此任务：[简要方案]`）。绝不处理已被他人或其他 Agent 认领的任务。
- **返工优先原则（To Rework First）**：当队列中存在 `To Rework`（审核或 QA 未通过）的任务时，必须优先于 Open 任务领取。领取后必须直接阅读最新失败原因评论，针对性修复。
- **优先级严格排序**：在同状态任务中，严格按优先级（P1 > P2 > P3 > P4）顺序抓取。
- **阻塞上报协议（Blocker Protocol）**：当任务因外部依赖、权限或不可抗力中断时，Agent 必须将状态标记为 `agent-blocked` 或退回 Open，并且强制附加包含三要素的说明评论：
  - 确切的阻塞原因；
  - 诊断证据（日志、输出或报错路径）；
  - 解除阻塞所需的决策或行动。

---

## 2. 门禁分级与工程防御体系（Quality Gates）

质量门禁是保证 Agent 高速提交而不污染主分支的核心防线。

### 第一层：本地 Pre-commit（轻量级快速检查，< 5 秒）
- **触发机制**：Git pre-commit 钩子。
- **职责范围**：仅针对暂存区（Staged Files）中的代码文件运行语法检查与代码格式校验（Lint / Formatting）。
- **排除策略**：纯文档（`.md`、`docs/*`）、工作流配置变更跳过重度编译。

### 第二层：本地 Pre-push（全面防护门禁，严格把关）
- **触发机制**：Git pre-push 钩子。
- **强制原则**：禁止使用 `--no-verify` 绕过。推送到主分支（`origin/main`）成功才算任务在技术层面交付。
- **核心检查项**：
  - **静态代码分析与安全扫描（零增量规则）**：
    - 新增文件必须达到零漏洞、零警报（0 Critical / High / Medium / Minor / Info）。
    - 修改已有文件遵循“童子军规则（Boy Scout Rule）”，修改后的告警数必须严格小于或等于修改前基线。
  - **代码健康度度量（Code Health Ratchet 棘轮机制）**：
    - 维护项目代码健康度基线（如平均健康度、热点模块健康度）。
    - 每次推送时校验当前评分不得低于基线。若重构使评分提升，自动更新健康度基线并要求提交记录新基线，使质量指标“只升不降”。
  - **单元与集成测试覆盖率**：
    - 设定前后端/各子模块的最低行覆盖率门槛。
    - 遵循 TDD 原则，缺陷修复必须包含重现该缺陷的回归测试（Red-Green 循环）。
  - **全量构建与类型检查（Build & Typecheck）**：
    - 严格类型检查（如 `tsc --noEmit`、编译器告警禁止）。
  - **核心链路冒烟测试（Smoke Tests）**：
    - 限制在关键端到端流程（如核心业务创建、检索、保存），执行时间控制在极短窗口（如 < 3-5 分钟）。

### 第三层：CI/CD 外部循环（Outer-loop Verification）
- 多平台矩阵构建、端到端全量回归测试、发布产物生成与部署。

---

## 3. 架构分层与不可变规范（ADR & Documentation System）

系统架构信息与决策沉淀在结构化文档体系中，分为现态文档与历史决策文档：

### 现态文档体系
- **`AGENTS.md`**：
  Agent 行动指南，包含任务领用、TDD 流程、门禁命令、代码健康度要求、提交格式、完成定义与应急例外协议。
- **`docs/VISION.md`**：
  产品愿景、目标用户、核心价值与明确的非目标（Non-goals），防止 Agent 产生不必要的过度设计。
- **`docs/ARCHITECTURE.md`**：
  现态系统拓扑图、技术栈分工、所有权边界、数据流动链路、存储与状态归属规则。
- **`docs/ABSTRACTIONS.md`**：
  核心领域实体、生命周期、值对象规范、跨层协议约定、系统保留字段/前缀约定（如系统内部属性使用 `_` 前缀，与业务属性隔离）。
- **`docs/GETTING-STARTED.md`**：
  本地开发环境准备、最短启动路径、常用开发命令与故障排查索引。

### 历史架构决策记录（ADR 体系）
- 位于 `docs/adr/` 目录，命名为 `NNNN-short-kebab-name.md`。
- **不可变性原则（Immutable History）**：已激活（active）的 ADR 严禁直接改动正文。新决策变更或推翻旧决策时，必须创建新 ADR，旧 ADR 仅更新元数据（`status: superseded`, `superseded_by: "NNNN"`）。
- **同步更新现态文档**：当产生新 ADR 时，必须在同一个提交中更新 `docs/ARCHITECTURE.md` 或 `docs/ABSTRACTIONS.md`，确保现态文档随时反映当前最新架构状态。

---

## 4. 自动化指令与多 Agent 兼容（Commands & Tooling）

为了让 Agent 可以像熟练团队成员一样运行，仓库中需要提供统一的操作入口：

- **统一 ADR 创建工具**：
  项目内置标准脚本（如 `scripts/create_adr.py`）或 Slash Command（`.claude/commands/create-adr.md` 等），由 Agent 调用，自动化计算编号、更新索引、验证参数。
- **任务闭环自动化（Done & Dispatch）**：
  提供标准化自动化指令（如 `next-task` 与 `done`），串联“读取任务 -> 启动评论 -> 自动校验 -> 提交推送 -> 完成汇报 -> 认领下一任务”流程。
- **多 Agent 兼容垫片（Compatibility Shims）**：
  在仓库根目录维护 `CLAUDE.md`、`GEMINI.md` 等工具专用入口，内部仅引用主规范 `@AGENTS.md`，确保无论团队采用哪种模型或 CLI 工具，均能无缝遵循项目统一的规范约束。

