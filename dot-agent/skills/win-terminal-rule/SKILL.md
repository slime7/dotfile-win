---
name: win-terminal-rule
description: 适用于 Windows 和非 Windows 系统的终端使用规则，并包含 Windows PowerShell 的专项注意事项。只要需要使用终端就应加载，尤其是在 Windows 或 PowerShell 环境中。
---

# 终端规则

只要在终端中执行操作，都应遵守以下规则。

## 通用规则

### 关闭彩色输出

- 在终端中读取、截取或转述输出时，尽量关闭所有彩色输出系统，以节省 token。
- 优先使用能够强制纯文本输出的命令参数。
- 如果工具支持颜色相关环境变量，在执行前显式关闭颜色输出。
- 常见示例：
  - `$env:NO_COLOR="1"`
  - `$env:CLICOLOR="0"`
  - `$env:CLICOLOR_FORCE="0"`
  - `--color=never`
  - `--no-color`

### 及时删除临时文件

- 如果为了查看、保存或转述终端输出而临时创建文件，用完后应立即删除。
- 除非用户明确要求保留，否则不要遗留输出快照、中间日志或临时调试文件。

## Windows PowerShell 专项规则

在 Windows，尤其是 PowerShell 环境下，还应额外遵守以下规则。

### 命令串联

- 不要依赖 `&&` 在不同 PowerShell 版本中的一致行为。
- 按顺序执行多条命令时，使用 `;`。
- 示例：
  - 错误：`cd my-dir && npm install && npm run build`
  - 正确：`cd my-dir ; npm install ; npm run build`

### 环境变量

- 为单条命令临时设置环境变量时，使用 PowerShell 语法。
- 示例：
  - 错误：`NODE_ENV=production npm run build`
  - 正确：`$env:NODE_ENV="production"; npm run build`

### 丢弃输出

- Windows 中没有 `/dev/null`。
- 应使用 `$null` 代替。
- 示例：
  - 错误：`command > /dev/null 2>&1`
  - 正确：`command > $null 2>&1`
  - 正确：`command *>$null`

### 常用命令与别名

- 除非明确处于 WSL 或 Git Bash 环境，否则不要假设 `grep`、`sed`、`awk` 这类 Linux 工具存在且行为一致。
- `ls`、`cat`、`rm` 等命令在 PowerShell 中可能只是 `Get-ChildItem`、`Get-Content`、`Remove-Item` 的别名，其参数和 GNU 工具差异很大。
- 递归删除示例：
  - 错误：`rm -rf my-folder`
  - 正确：`Remove-Item -Recurse -Force my-folder`

### 提权方式

- 在原生 Windows 环境中，不要在命令前加 `sudo`。
- 如果需要管理员权限，应直接以管理员身份运行终端。

### 引号与转义

- 在 PowerShell 命令中嵌套引号时要特别谨慎。
- 优先使用 PowerShell 的标准引号规则，能用单引号时尽量用单引号；必须转义时使用反引号 `` ` ``。
- 避免编写引号层级过于复杂的内联脚本。

### 文件编码

- 读写文件时默认使用 `utf-8`，避免因为 PowerShell 默认编码不一致而出现乱码或内容损坏。
- 使用 `Get-Content`、`Set-Content`、`Add-Content`、`Out-File` 等命令时，合适的情况下显式指定 `-Encoding utf8`。
