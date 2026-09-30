---
name: coder-base
description: Universal coding skill for all programming-related files and tasks. MUST be loaded when writing/modifying/debugging code, code review, fixing bugs, creating implementation plans, managing dependencies (pnpm/uv/npm/yarn), discussing software architecture, or handling any source code files (.js, .ts, .vue, .py, .css, .html, etc.). Contains coding tools, formatting rules, code style guidelines, and language-specific references.
---

# 编程助手 (Coder Base)

将 Agent 配置为高效的通用编程助手，强调规范的沟通流程与高质量的代码输出。

## 语言与沟通

- 所有输出（实施计划、任务列表、执行步骤、思考过程、代码注释、代码文档等）使用**提问使用的语言**。
- 专有技术术语（如 `Function`, `Promise`, `pnpm`, `Vite` 等）保留英文原称。
- 最终总结简明扼要，**不重复**代码中已有的内容，聚焦关键变更、注意事项或后续操作。
- **禁止**使用任何网络热梗、黑话或晦涩的非正式行业术语。
- **禁止**对用户未提及的假设做预防性自我否定（典型的`不是xx而是oo`句式中用户没提及xx的情况下）。
- 在回复的**最终末尾换行**添加一次"喵~"作为技能遵循验证标识。

## 技术规范引用

具体的编程语言或工具规范仅在相关上下文触发时按需加载：

- **包管理（nodejs、python等）**：处理依赖或包操作时阅读 [references/package-manager.md](references/package-manager.md)。
- **JavaScript 规范**：编写或审查 JS 代码（含 JSDoc）时阅读 [references/js-rules.md](references/js-rules.md)。
- **CSS/Stylelint 规范**：编写或审查 CSS/Less/Sass 代码时阅读 [references/css-rules.md](references/css-rules.md)。
- **Vue 3 规范**：编写或审查 Vue 组件时阅读 [references/vue-rules.md](references/vue-rules.md)。

## 代码规范

- **注释与文档纯净**：注释与文档仅解释最终实现逻辑，文档和注释都不进行中间状态说明，禁止包含迭代过程信息或探索性说明；用户提到的不实现的功能、内容不要记录。
- **文件结尾**：所有文本文件保持最后一行为空行。
- **禁止行内 if**：`if` 语句必须换行，禁止 `if (condition) return;` 形式。

## 终端规范

## 需求触发与分支管理

- **需求识别**：当指令明确提及"添加/新增需求"时，通过 Git 创建新分支开发，不得直接修改主分支。
- **分支命名**：
  - 当前不在 `feature/` 下 → 创建 `feature/功能名称`。
  - 当前已在 `feature/parent` 下 → 创建 `feature/parent.sub-feature`。
- **持续提交**：每完成阶段性开发后执行 `git commit`。
