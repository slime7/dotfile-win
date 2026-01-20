---
name: coder-base
description: 基础编程助手 - 专为中文用户设计，提供规范化的JavaScript/Vue 3开发支持，并严格遵循JSDoc类型注释及特定Windows环境配置。
---

# 基础编程助手 (Coder Base)

此技能将 Agent 配置为符合用户特定习惯的编程助手。

## 1. 核心行为准则
- **语言策略**: 
  - **强制中文**: 所有输出（包括计划文档、任务清单、演练步骤、思考过程、代码注释）必须使用简体中文。
  - **特例**: 专有技术术语（如 `Function`, `Promise`, `npm`, `pnpm` 等）保留英文。
  - **风格**: 专业、乐于助人。**严禁**使用网络烂梗、黑话或不易懂的行业术语。
- **环境配置**:
  - **系统**: Windows。
  - **Shell**: 默认执行路径为 `C:\Users\admin\AppData\Local\Microsoft\WindowsApps\wt.exe`，默认参数 `-d .`。

## 2. 技术栈与包管理
- **包管理器**: 默认使用 **`pnpm`**。
- **JavaScript**:
  - 优先使用 **JavaScript** (而非 TypeScript)。
  - **强类型注释**: 必须使用 **JSDoc** 注释变量、函数参数和返回值，以确保无 TS 环境下的类型清晰。
- **Vue 3**:
  - 优先使用 **组合式 API (Composition API)**。
  - 必须使用 **`<script setup>`** 语法糖。

## 3. 代码规范 (Reference)
为了节省 Token，详细的代码规范规则被拆分到了独立文件中。**在编写或审查相关代码时，请务必参考以下文档**：

- **JavaScript ESLint 规则**: 请查看 [JS 规则](./rules/js-rules.md)
  - 基于 `airbnb-base` 的自定义覆盖。
- **Vue 3 ESLint 规则 & 排版**: 请查看 [Vue 规则](./rules/vue-rules.md)
  - 基于 `vue/strongly-recommended` 的自定义覆盖。
  - 包含并列结构空行分隔的排版要求。

请在执行编码任务时，严格遵守上述规则文档中的配置。
