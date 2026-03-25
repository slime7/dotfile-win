# Stylelint Configuration for CSS

当涉及 CSS/Less/Sass 代码编写或修改时，必须遵循以下规范：

- **Stylelint 校验**:
  - 如果项目配置有 Stylelint（如 `.stylelintrc.*`, `stylelint.config.js` 等），在完成代码修改后，**必须**运行项目配置的 Stylelint 规则进行校验。
  - 任务仅在通过 Stylelint 校验且无错误（Error）后方可视为完成。
  - 如果校验发现错误，应优先修复错误而非忽略。
