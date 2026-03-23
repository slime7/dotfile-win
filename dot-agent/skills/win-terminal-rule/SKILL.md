---
name: win-terminal-rule
description: Windows PowerShell terminal specific rules and precautions. MUST be loaded when the user is on a Windows system or using a Windows-style terminal (PowerShell).
---

# Windows 终端（PowerShell）规范

在 Windows 环境下操作时，特别是使用 PowerShell（Windows 中 `run_command` 的默认终端）时，必须遵守以下与标准 Linux/bash 终端不同的规则：

## 1. 命令连接
- 禁止使用 `&&` 连接命令。并非所有 PowerShell 版本都以相同方式支持它。必须使用 `;` 按顺序执行命令。
  - 错误（Linux 风格）: `cd my-dir && npm install && npm run build`
  - 正确（PowerShell 风格）: `cd my-dir ; npm install ; npm run build`

## 2. 环境变量
- 为单个命令临时设置环境变量的方式不同。
  - 错误（Linux 风格）: `NODE_ENV=production npm run build`
  - 正确（PowerShell 风格）: `$env:NODE_ENV="production"; npm run build`

## 3. 丢弃输出
- Windows 中没有 `/dev/null`。请使用 `$null` 代替。
  - 错误（Linux 风格）: `command > /dev/null 2>&1`
  - 正确（PowerShell 风格）: `command > $null 2>&1` 或 `command *>$null`

## 4. 常用命令和别名
- 常用的 Linux 工具如 `grep`、`sed`、`awk` 在原生环境下并非以完全相同的方式提供，除非明确使用了 WSL 或 Git Bash。
- 像 `ls`、`cat`、`rm` 这样的命令是 PowerShell cmdlet（`Get-ChildItem`、`Get-Content`、`Remove-Item`）的别名，但它们的参数标志（flags）有很大不同。
- 对于递归删除：
  - 错误（Linux 风格）: `rm -rf my-folder`
  - 正确（PowerShell 风格）: `Remove-Item -Recurse -Force my-folder`

## 5. Sudo
- Windows 没有原生的 `sudo` 命令。不要在命令前加 `sudo`。如果需要提升权限，必须以管理员身份运行终端本身。

## 6. 双引号与转义
- 在命令内部转义双引号可能会很棘手。在 PowerShell 中，通常需要使用反引号 `` ` `` 进行转义，或者对字面字符串使用单引号。通过 `run_command` 运行组合命令时，坚持使用标准的 PowerShell 字符串结构，避免编写过于复杂的带引号 shell 脚本。

## 7. 文件编码
- 读取或写入文件时默认使用 `utf-8` 编码，避免因 PowerShell 默认编码不一致导致乱码或内容损坏。
- 涉及 `Get-Content`、`Set-Content`、`Add-Content`、`Out-File` 等文件操作命令时，优先明确指定 `-Encoding utf8`。
