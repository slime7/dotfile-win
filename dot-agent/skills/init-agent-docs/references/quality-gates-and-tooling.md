# 质量门禁与工程防护参考

高质量的 Agent 驱动开发离不开严格、自动化的工程质量门禁。本文档提供可复现的门禁设计模式、配置范例以及规则说明，使目标项目能够建立坚固的自动化防护网。

## 1. Git Hooks 门禁架构（基于 Husky / 纯 Shell）

使用双层钩子架构：Pre-commit 快速拦截语法与格式问题，Pre-push 拦截逻辑、健康度、安全与构建破坏。

### Pre-commit 示例实现（`.husky/pre-commit`）
```sh
#!/bin/sh
set -e

echo "🔍 执行 Pre-commit 检查..."

# 检测暂存区是否有实质代码变更
STAGED_FILES=$(git diff --cached --name-only)
CODE_CHANGED=false

for FILE in $STAGED_FILES; do
  case "$FILE" in
    docs/*|*.md|.github/*|.husky/*)
      ;;
    *)
      CODE_CHANGED=true
      ;;
  esac
done

if [ "$CODE_CHANGED" = false ]; then
  echo "  → 仅文档或工作流配置变更，跳过重度代码校验"
  exit 0
fi

# 仅对暂存代码执行极速 Lint / 格式检查
STAGED_CODE=$(echo "$STAGED_FILES" | grep -E '\.(ts|tsx|js|jsx|py|rs|go)$' || true)
if [ -n "$STAGED_CODE" ]; then
  echo "  → 执行代码风格与语法检查..."
  # 例如: pnpm lint --quiet 或 npm run lint 等
fi

echo "✅ Pre-commit 通过"
```

### Pre-push 示例实现（`.husky/pre-push`）
```sh
#!/bin/sh
set -e

echo "🚀 执行 Pre-push 全量校验 (不可使用 --no-verify 绕过)..."

# 强制主分支直推规范检测（若项目采用直推模式）
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "HEAD" ]; then
  echo "❌ 仅允许在 main 分支或直推 main 的临时状态下执行推送"
  exit 1
fi

# 静态分析与安全审计（零新增告警检查）
echo "🛡️ 执行静态分析门禁..."
# 例如: npm run lint:security 或扫描差异文件

# 核心构建与类型检查
echo "📦 执行类型检查与构建..."
# 例如: npm run build / tsc --noEmit

# 单元与集成测试（强制覆盖率达标）
echo "📊 执行测试套件并计算覆盖率..."
# 例如: npm run test:coverage

# 代码健康度棘轮检查（可选，基于指标文件）
if [ -f ".codescene-thresholds" ] || [ -f ".code-health-thresholds" ]; then
  echo "🏥 校验代码健康度基线..."
  # 比较并更新棘轮
fi

echo "✅ 所有 Pre-push 校验通过，允许推送"
```

---

## 2. 静态安全与质量扫描规范（静态代码分析）

### 零增量规则（Zero New Findings Rule）
- **新文件绝对零告警**：凡是任务中新建的文件（源码、脚本、配置、测试），必须达到对应静态扫描工具的 0 Critical、0 High、0 Medium、0 Minor、0 Info。
- **存量文件童子军规则（Boy Scout Rule）**：修改已有文件时，修改后的静态分析告警总数必须严格小于或等于修改前的基线告警数。绝对不允许引入任何新增告警。

### 扫描清单构建模式
在提交与扫描前，精准枚举本次变更涉及的文件：
```bash
# 获取已暂存及已提交相对于基线的变更
git diff --name-only --diff-filter=ACMR "$(git merge-base HEAD origin/main)" --
# 获取未跟踪的新增文件
git ls-files --others --exclude-standard
```

---

## 3. 代码健康度棘轮机制（Code Health Ratchet）

代码健康度防退化机制能有效防止代码在长期多 Agent 维护下逐渐腐化。

### 棘轮运行原则
- **基线记录**：在仓库根目录维护健康度基线文件（如 `.codescene-thresholds` 或 `.code-health.json`），记录核心模块健康度与全局平均健康度数值。
- **提交前自检**：Agent 在修改任何文件前，先获取该文件的当前健康度；修改并重构后，再次获取评分，确保评分上升（若原本为满分 10.0 则保持 10.0）。
- **推送时上调（Ratchet Up）**：当推送时的健康度高于记录的基线时，门禁脚本自动将基线数值提高到最新水平，并要求 Agent 提交更新后的基线文件。基线只升不降，推动代码质量持续改善。

---

## 4. 测试与验证策略

### TDD 步骤要求
1. **Red**：先编写可重现缺陷或覆盖新需求的失败测试。
2. **Green**：编写最小实现代码使测试通过。
3. **Refactor**：重构并保持测试通过，同时优化代码结构与可读性。
4. **Commit**：完成一个周期后提交代码。

### 覆盖率防线
- 设定明确的覆盖率门槛（如语句覆盖率 ≥ 70% 或更高）。
- 覆盖率检查必须作为 CI 与 Pre-push 的硬性门禁，防止遗漏核心边界测试。

