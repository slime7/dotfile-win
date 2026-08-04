---
name: fusion-mcp
description: 连接并调用 Autodesk Fusion 本地 MCP 服务器（fusion-mcp），重点是获取 session_id 并完成 MCP 握手。当用户明确提到 fusion-mcp，或要求连接/调用本机 Fusion MCP（读取项目与文档、执行 Fusion 脚本、读取电子设计数据、视口截图、撤销/重做）时使用。
---

# Fusion MCP

## 端点以 Codex 配置为准

不要假设端口固定。每次使用前先读取 Codex 中的 MCP 服务器配置：

- 配置文件：`~/.codex/config.toml`
- 段落：`[mcp_servers.fusion-mcp]`
- 端点：该段落下的 `url` 字段（例如 `http://127.0.0.1:27182/mcp`，端口可自由修改）

若 Codex 会话内已直接暴露 fusion-mcp 的工具（如 `fusion_mcp_read`、`mcp__fusion-mcp__*`），直接调用即可，无需手动握手。以下流程用于工具未暴露、需要直接调试或验证连接时。

## 获取 session_id

fusion-mcp 是 Streamable HTTP 传输的 MCP 服务器，session_id 在握手响应头中返回。

1. 向端点发送 `initialize`，**不带** `MCP-Session-Id` 头：

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"fusion-mcp-client","version":"1.0.0"}}}
```

请求头：

```
Content-Type: application/json
Accept: application/json, text/event-stream
```

2. 从响应头读取 `MCP-Session-Id`，其值即 session_id（响应体不含会话 ID）。
3. 携带 session_id 发送 `notifications/initialized`：

```json
{"jsonrpc":"2.0","method":"notifications/initialized"}
```

4. 携带 session_id 调用工具：

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
```

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"fusion_mcp_read","arguments":{"queryType":"projects"}}}
```

`tools/list` 可发现 4 个工具：`fusion_mcp_read`、`fusion_mcp_execute`、`fusion_mcp_update`、`fusion_mcp_electronics_read`。电子设计实体字段与过滤规则可通过 Codex 中 fusion-mcp 的资源查看（`resource://mcp.electronics_schema_<类名>`）。

5. 结束后可发送 `DELETE` 关闭会话（仍需携带 session_id）。

## 错误排查

- `Missing MCP-Session-Id header`：请求体未被正确解析为 JSON-RPC（多为引号转义问题），或请求本身缺少必要头。把 JSON 写入文件再发送可避免转义损坏。
- `Session not found`：session_id 无效或已过期，重新执行 initialize。
- 连接失败：确认 Fusion 正在运行、MCP 服务已启用，并核对配置中的 url。

## PowerShell 注意

- 请求体先写入临时文件，再用 `curl.exe --data-binary "@文件"` 发送。
- 用 `curl.exe -s -D <头文件> -o <体文件>` 分离响应头与响应体，从响应头解析 `MCP-Session-Id`。
- 临时文件用后立即删除；读写文本文件显式使用 UTF-8。
