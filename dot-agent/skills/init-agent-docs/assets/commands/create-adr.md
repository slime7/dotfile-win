# Create Architecture Decision Record

在任务开发过程中记录新的架构决策（ADR）。

## 何时创建 ADR
- 引入或移除重大外部依赖
- 变更数据持久化方案或存储策略
- 引入新的运行平台或部署目标
- 引入、变更或废除核心业务领域抽象
- 做出影响未来代码规范的重大跨模块架构决策

不适用于：日常 Bug 修复、局部 UI 样式调整、行为不变的小型重构或普通测试补充。

## 创建步骤

### 1. 运行项目内置 ADR 创建脚本
使用项目自带的脚本快速创建新的 ADR：

PowerShell：
```powershell
python .\scripts\create_adr.py . "决策简短标题" --context "促成决策的背景与约束" --decision "核心决策内容" --option "候选方案A (采纳理由)" --option "候选方案B (未采纳理由)" --consequence "正负面影响与风险" --status active
```

Bash：
```bash
python3 scripts/create_adr.py . "决策简短标题" --context "促成决策的背景与约束" --decision "核心决策内容" --option "候选方案A (采纳理由)" --option "候选方案B (未采纳理由)" --consequence "正负面影响与风险" --status active
```

### 2. 替代旧决策（如适用）
若新 ADR 是为了替代既有决策，传入 `--supersedes NNNN` 参数。脚本会自动更新关联信息，并在 `docs/adr/README.md` 中更新索引。

### 3. 同步提交现态架构文档
在同一 Git 提交中包含新建的 ADR、更新的 `docs/adr/README.md` 以及对应的 `docs/ARCHITECTURE.md` 或 `docs/ABSTRACTIONS.md`。

