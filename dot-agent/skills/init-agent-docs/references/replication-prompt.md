# 复刻 Agent 工作流架构完整提示词指南

本参考为 Agent 提供了完整的元提示词（Prompt Template）与操作步骤，用于在任何新旧项目中为该项目生成符合工程规范的 Agent 工作流与架构文档体系。

## 何时使用本提示词

当用户希望将成熟项目的 Agent 工作流与架构体系（包括任务流转状态机、TDD 驱动、分层质量门禁、代码健康度防退化、零增量安全规范、ADR 治理与自动化辅助命令）复刻到当前项目时，直接按本指引执行。

---

## 阶段一：目标项目环境与能力探查（Discovery）

在生成文档前，必须在目标项目中收集真实证据，提取以下关键特征：

- **语言与运行时**：Node.js (pnpm/npm/yarn), Rust (cargo), Python, Go, Java 等。
- **构建与检查工具**：编译命令、代码格式化工具、静态类型检查器（`tsc`, `mypy` 等）、Linter（`eslint`, `ruff`, `clippy` 等）。
- **测试框架与覆盖率工具**：Vitest, Jest, Pytest, Cargo test，覆盖率收集命令。
- **Git 与工作流基础设施**：是否存在 Husky、现有 Git Hooks、CI 配置文件（GitHub Actions, GitLab CI, CircleCI 等）。
- **任务管理与跟踪总线**：是否有配套的 Issue 跟踪系统（如 GitHub Issues, Linear, Jira 等）。若无，默认配置通用 Issue/Task 规范。
- **既有文档与规范**：是否存在现有的架构文档、编码规范，需按“已有项目合并原则”保留有效信息。

---

## 阶段二：生成核心规范与架构文档（Document Generation）

根据探查到的实际环境，将通用 Agent 工作流裁剪并写入目标项目对应文档：

### 生成项目根目录规范：`AGENTS.md`
必须包含以下核心章节，并填充目标项目的具体命令：

- **前置阅读与单一事实源**：
  明确规定 Agent 启动任务前必须阅读的文档清单（`docs/ARCHITECTURE.md`, `docs/ABSTRACTIONS.md`, `docs/adr/README.md`）。
- **任务流转与协同约定（Task Lifecycle）**：
  - 明确状态流转：Backlog → Open → To Rework → In Progress → In Review → Done。
  - 防碰撞声明：写代码前必须将任务状态设为 In Progress 并评论简要方案。
  - 返工优先原则：优先处理 To Rework 状态的任务。
  - 阻塞上报三要素：阻塞原因、证据信息、解除条件。
- **开发与提交流程**：
  - 严格 TDD 规范（Red-Green-Refactor）。
  - 分支与提交规范（如常规分支或直推规范，符合项目实际）。
  - 强制禁止使用 `--no-verify` 绕过质量门禁。
- **分层质量门禁与工程防御（Quality Gates）**：
  - 明确列出项目可执行的 Lint、Typecheck、Build、Test:coverage 具体命令。
  - 静态安全与分析：执行“零新增告警”与“童子军原则”。
  - 代码健康度：如配置了健康度指标，要求只升不降。
- **架构与 ADR 决策约束**：
  - 何时必须记录 ADR（引入新依赖、关键技术选型、存储策略、跨模块核心抽象变化）。
  - ADR 不可变原则（历史 ADR 只允许更新状态，不修改正文）。
  - 架构变更必须在同一 Commit 中同步现态文档。
- **交付验收清单（Release Checklist）**：
  - 任务完成时必须提供的验收证据（实现简述、QA 测试记录、覆盖率结果、门禁检查状态）。
- **规则例外协议（Exception Protocol）**：
  - 遇工具故障或不可行规则时的临时豁免上报与记录流程。

### 生成现态架构与抽象文档
- **`docs/VISION.md`**：项目的核心价值、目标使用者、系统边界与明确非目标。
- **`docs/ARCHITECTURE.md`**：系统架构分层拓扑、模块职责、数据流向、状态持有位置。
- **`docs/ABSTRACTIONS.md`**：核心领域模型、关键实体、命名与序列化约定、系统内部保留前缀（如 `_`）。
- **`docs/GETTING-STARTED.md`**：依赖安装、本地启动、命令速查表、常见排查步骤。

### 生成 ADR 体系
- **`docs/adr/README.md`**：说明 ADR 决策生命周期、不可变规则、现有决策索引表格、标准 ADR 模板以及项目内创建脚本的用法。

---

## 阶段三：写入工程辅助脚本与自动化指令（Tooling & Commands）

确保目标项目在初始化完成后具备完全自足的运行能力，将相关文件写入目标项目：

- **项目内 ADR 创建工具**：
  将 `scripts/create_adr.py` 复制至目标项目的 `scripts/create_adr.py`，并在 `docs/adr/README.md` 中提供命令示例。
- **多 Agent 兼容入口**：
  在项目根目录生成 `CLAUDE.md` 与 `GEMINI.md`：
  ```markdown
  @AGENTS.md

  此文件为兼容入口，请直接遵循 AGENTS.md 中的统一工作规范与架构要求。
  ```
- **（可选）自动化 Slash Commands**：
  若项目使用 Claude Code 或支持 Slash Command 的工具，可在项目内生成 `.claude/commands/` 下的辅助指令：
  - `create-adr.md`：快速创建符合规范的新架构决策记录。
  - `task-done.md`：校验门禁、提交推送、输出验收总结并完成任务。
  - `next-task.md`：按照“返工优先、优先级降序”逻辑拉取并认领下一任务。
- **（可选）Git Hooks 配置**：
  若项目支持或用户要求，辅助配置 `.husky/pre-commit` 与 `.husky/pre-push`，将质量门禁固化在代码提交与推送阶段。

---

## 阶段四：验证与自检（Validation）

生成完成后，运行验证脚本（如 `validate_agent_docs.py`），确保：
- 核心文档（`AGENTS.md`, `VISION.md`, `ARCHITECTURE.md`, `ABSTRACTIONS.md`, `GETTING-STARTED.md`, `docs/adr/README.md`）全部存在且有效连接。
- 无未替换的模板占位符（如包含类似未填充的双大括号或 TODO 标记）。
- 路径和命令完全匹配目标项目的真实工具链，不包含任何外部未适配的专有名词或幻觉。

