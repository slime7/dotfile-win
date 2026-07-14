---
name: init-agent-docs
description: 为新项目、脚手架生成但尚未实质开发的项目，或已有项目初始化、补建和审计 agent 驱动的编程文档体系。仅当用户明确要求建立、初始化、补全或整理项目级 agent 文档时使用，不要为普通编码或一般文档任务自动触发。
---

# 初始化项目 Agent 文档

为项目建立可由人和 coding agent 共同维护的文档体系。先从仓库取证，再生成或合并文档；不要把推断、脚手架示例或未来设想写成当前事实。

## 读取参考资料

执行每次任务前：

1. 阅读 [references/project-state.md](references/project-state.md)，判断项目所处状态。
2. 阅读 [references/document-system.md](references/document-system.md)，确定每份文档的职责和默认结构。
3. 如果项目已有实质实现或已有同类文档，再阅读 [references/existing-project.md](references/existing-project.md)。

## 工作流

### 1. 确认目标与保护现场

- 确认项目根目录，不要默认当前目录就是目标项目。
- 读取目标项目内适用的 `AGENTS.md`、已有自定义 agent 入口及其他仓库指令。
- 检查 Git 状态，保留用户未提交的更改。不要覆盖、回退或删除无法确认来源的内容。
- 确认用户要求的是完整初始化、补建缺失文档，还是审计现有体系。
- 确认用户指定的文档路径，并检查旧项目是否已有等价文档。没有特殊要求时才使用默认路径。

### 2. 从仓库收集事实

优先使用快速文件搜索和定向读取，检查以下信息：

- 项目名称、README、依赖清单和锁文件。
- 源码入口、模块目录、领域类型、数据存储和外部集成。
- 构建、运行、测试、检查、发布与部署配置。
- CI、迁移、示例环境变量和基础设施文件。
- Git 历史及现有设计、架构、贡献和决策文档。
- 默认示例页面、占位名称、示例测试和其他脚手架痕迹。

不要仅因项目已有源码、测试、Git 提交或大量文件，就把它判定为已有项目。脚手架可能同时具备这些特征。

### 3. 判断项目状态

按照 `project-state.md` 将项目归为：

- **空白新项目**：尚无实质业务实现。
- **脚手架新项目**：主要是生成器提供的通用结构和示例，尚未形成项目特有能力。
- **已有项目**：存在可验证的项目特有实现、抽象、运行方式或维护历史。

空白新项目和脚手架新项目都走新项目流程。少量定制但主体仍为脚手架时也走新项目流程，同时保留已验证的定制内容。证据相互冲突且会改变文档内容时，询问用户。

### 4. 建立事实清单

在写文件前，将信息区分为三类：

- **当前实现**：可由代码、配置、测试或可靠现有文档验证。
- **计划设计**：由用户明确确认，但尚未实现。
- **未知信息**：仓库和用户输入都不能确认。

从仓库提取可发现的信息。只向用户询问无法从环境确认且会实质影响文档的内容，例如项目愿景、目标用户、非目标和不可妥协的约束。不得编造未知信息；非关键未知项可明确写为“待确认”，但不得留下模板占位符。

### 5. 创建或合并文档

默认建立以下文件；用户指定位置或项目已有权威位置时，使用相应路径替换默认值：

- `AGENTS.md`
- `docs/VISION.md`
- `docs/ARCHITECTURE.md`
- `docs/ABSTRACTIONS.md`
- `docs/GETTING-STARTED.md`
- `docs/adr/README.md`

遵循以下规则：

- 新项目按 `document-system.md` 创建完整但与成熟度相称的内容。
- 脚手架示例不得描述为项目功能；尚未实现的内容明确标为“计划”。
- 已有项目按 `existing-project.md` 审计后合并，保留有效人工规则和项目知识。
- 所有文档路径都以项目根目录为基准。记录本次实际路径映射，并让链接、兼容入口和校验参数使用同一映射。
- 一项事实只设一个权威位置，其他文档使用相对链接引用。
- 沿用项目现有文档语言；没有既有约定时使用用户沟通语言，保留必要的英文技术名词。
- 仅在检测到相应工具、已有兼容文件或用户明确要求时创建 `CLAUDE.md` 或 `GEMINI.md`。兼容入口只指向本次采用的实际 agent 入口，不要复制共享规则。
- 默认只建立 ADR 体系，不追写历史决策。只有决策内容及其原因都有明确证据时才创建历史 ADR。
- 使用 UTF-8 编码，并保持文本文件末尾有空行。

### 6. 使用固定脚本创建 ADR

不要临时编写 ADR 编号、命名或模板脚本。先确定背景、决策、候选方案和影响，再根据终端调用技能自带 Python 脚本。

脚本需要 Python 3.10 或更高版本。

PowerShell：

```text
python .\scripts\create_adr.py <project-root> "<title>" --adr-dir <adr-directory> --slug <slug> --context "<context>" --decision "<decision>" --option "<option-a>" --option "<option-b>" --consequence "<consequence>"
```

Bash：

```text
python3 scripts/create_adr.py <project-root> "<title>" --adr-dir <adr-directory> --slug <slug> --context "<context>" --decision "<decision>" --option "<option-a>" --option "<option-b>" --consequence "<consequence>"
```

ADR 使用默认 `docs/adr` 时可以省略 `--adr-dir`。自定义目录必须是相对于项目根目录的路径，并且目录内已有 `README.md`。英文标题可以省略 `--slug` 并由脚本生成。中文或无法生成 ASCII 文件名的标题必须显式提供 `--slug`。新 ADR 默认状态为 `proposed`；只有决策已经生效时才传入 `--status active`。使用 `--supersedes NNNN` 前确保被替代 ADR 存在。

### 7. 使用固定脚本验证结果

不要重新实现校验逻辑。根据当前终端从技能目录直接运行 Python 脚本。

PowerShell：

```text
python .\scripts\validate_agent_docs.py <project-root> --adr-dir <adr-directory>
```

Bash：

```text
python3 scripts/validate_agent_docs.py <project-root> --adr-dir <adr-directory>
```

默认路径全部可省略对应参数。使用自定义文档路径时，按照 `document-system.md` 中的参数表传入完整路径映射。PowerShell 与 Bash 直接使用同一个 `validate_agent_docs.py`，因此两种环境遵循相同规则。校验失败时修正文档并重新运行。脚本只做结构检查，仍需人工复核：

- 所有“当前实现”是否都有仓库证据。
- 所有“计划设计”是否明确标注且得到用户确认。
- 命令、路径和文件名是否与目标项目一致。
- 旧项目的有效内容是否完整保留。
- 文档之间是否存在矛盾或大段重复。

## 完成报告

向用户简要说明：

- 项目被判定为何种状态及主要依据。
- 创建和更新了哪些文档。
- 保留或合并了哪些既有规则。
- 校验结果和仍待确认的事项。

不要把任务标记为完成，除非核心文档齐全、校验通过，或已明确说明无法完成的阻塞原因。
