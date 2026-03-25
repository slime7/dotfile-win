# ESLint Configuration for JavaScript

当涉及 JavaScript 代码编写或修改时，必须遵循以下规范：

- **JSDoc 类型标注**: 必须使用 JSDoc 对所有公共变量、函数参数及返回值进行明确的类型标注。
- **ESLint 校验**:
  - 如果项目含有 ESLint 配置（如 `.eslintrc.*`, `eslint.config.js` 等），在完成代码修改后，**必须**运行项目配置的 ESLint 规则进行校验。
  - 任务仅在通过 ESLint 校验且无错误（Error）后方可视为完成。
  - 如果校验发现错误，应优先修复错误而非忽略。

