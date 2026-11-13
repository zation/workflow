---
name: workflow
description: 项目开发约定的总入口与路由索引。当用户提到 AGENTS.md、Spec/Plan/Tasks、交付流程、代码或文档 review，但没说清要做哪一步时，帮他选对子技能。用户已有明确动作或点名子技能时，直接用对应子技能，不要在本技能里重复执行。
agent_created: true
---

# workflow

一套可版本化的《项目开发约定》分发与执行工具。约定正文只有一份，在 `assets/templates/AGENTS.md`；五个子技能各管一件事，共享 `scripts/` 与 `assets/templates/`。

## 选哪个

| 用户想做什么 | 用 |
| --- | --- |
| 新仓库生成 `AGENTS.md` 和 `docs/` 骨架 | `workflow-init` |
| 已有仓库升级、对齐 `AGENTS.md` | `workflow-upgrade` |
| review 任务执行结果（方案、代码、文档同步），只看不改 | `workflow-review-tasks` |
| review Spec / Plan / Tasks 文档是否合理、同步，只看不改 | `workflow-review-docs` |
| 按 Tasks 文档逐任务实现、验证、提交直到完成 | `workflow-tasks` |

用户已经点明动作或技能名时直接调用对应子技能；本技能只在意图模糊时分流，不重复执行它们的流程。

## 调用方式

技能没有参数占位符。把目标仓库路径、Tasks 文档路径或要 review 的文档直接写在话里，由模型从本次请求里读取：

- WorkBuddy：`/workflow-tasks` 或 `@skill:workflow-tasks`，后面跟 `docs/delivery/user-login-tasks.md`
- Codex：`$workflow-tasks docs/delivery/user-login-tasks.md`

## 地基约束

- `AGENTS.md` 只承载跨项目通用条款，由模板整份生成；项目特有约定写进 `docs/` 下对应的长期文档。
- `AGENTS.md` 顶部 `<!-- agents-md-template: x.y.z -->` 是漂移检测依据，改模板必须同步提升版本号。
- 写盘前让开发者看过差异并明确同意；`upgrade` 默认只读。
- 两个 review 技能只读不修复；要修复请开发者点名后另起任务。
