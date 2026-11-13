---
name: workflow
description: 项目开发约定的总入口与路由索引。当用户提到 AGENTS.md、生成或评审 Spec / Plan / Tasks、交付流程、按 Tasks 实现、代码或文档 review，但没说清要做哪一步时，帮他选对子技能。用户已有明确动作或点名子技能时，直接用对应子技能，不要在本技能里重复执行。
agent_created: true
---

# workflow

一套可版本化的《项目开发约定》分发与执行工具。约定正文只有一份，在 `assets/templates/AGENTS.md`；八个子技能各管一件事，共享 `scripts/` 与 `assets/templates/`。

## 选哪个

| 用户想做什么 | 用 |
| --- | --- |
| 新仓库生成 `AGENTS.md` 和 `docs/` 骨架 | `workflow-init` |
| 已有仓库升级、对齐 `AGENTS.md` | `workflow-upgrade` |
| 澄清需求，生成或订正 Spec | `workflow-spec` |
| 讨论技术方案，生成或订正 Plan | `workflow-plan` |
| 把方案拆成任务，生成或订正 Tasks 文档 | `workflow-tasks` |
| 按 Tasks 文档逐任务实现、验证、提交直到完成 | `workflow-implement` |
| review 交付的实现结果（方案、代码、提交、文档同步），只看不改 | `workflow-review-implementations` |
| review Spec / Plan / Tasks 文档是否合理、同步，只看不改 | `workflow-review-docs` |

用户已经点明动作或技能名时直接调用对应子技能；本技能只在意图模糊时分流，不重复执行它们的流程。

## 调用方式

技能没有参数占位符。把目标仓库路径、topic、文档路径或要点名的文件直接写在话里，由模型从本次请求里读取：

- 生成文档：`/workflow-spec`、`/workflow-plan`、`/workflow-tasks`，后面跟 topic 或要点名的文件
- 执行实现：`/workflow-implement docs/delivery/user-login-tasks.md`（WorkBuddy 也可用 `@skill:workflow-implement`）
- Codex：`$workflow-plan 依据 docs/delivery/user-login-spec.md 出方案`、`$workflow-implement docs/delivery/user-login-tasks.md`

## 地基约束

- `AGENTS.md` 只承载跨项目通用条款，由模板整份生成；项目特有约定写进 `docs/` 下对应的长期文档。
- `AGENTS.md` 顶部 `<!-- agents-md-template: x.y.z -->` 是漂移检测依据，改模板必须同步提升版本号。
- 写盘前让开发者看过差异并明确同意；`upgrade` 默认只读。
- 三个文档技能只产出本阶段的交付文档：可以回头订正更早阶段的文档，但不进入下一步、不执行实现、不创建 commit。每份交付文档确认后各自做一次 docs 提交固化，由开发者自行完成；plan / tasks / implement 开工前先提示并等这个节点。
- 两个 review 技能只读不修复；要修复请开发者点名后另起任务。
