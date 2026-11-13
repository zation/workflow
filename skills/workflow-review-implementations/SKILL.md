---
name: workflow-review-implementations
description: 按指定的 Tasks 文档 review 交付的实现结果，检查方案一致性、代码实现、提交和文档同步，只输出分级问题清单，不改任何文件。Use when 用户说 review 一下这次交付的实现、检查交付完成情况、收尾前检查、对照 spec/plan 看实现有没有跑偏；看的是代码实现、提交和执行结果，文档本身写得对不对请用 workflow-review-docs。产出按阻塞/重要/建议分级的发现，每条带位置、依据和具体建议。不用于评审 Spec/Plan/Tasks 文档本身是否合理（用 workflow-review-docs），不用于生成 Tasks 文档（用 workflow-tasks），不用于执行任务（用 workflow-implement），也不要顺手修复。
agent_created: true
---

# workflow-review-implementations

判断基准是目标仓库的 `AGENTS.md`，尤其是「标准开发流程」第 4、5、6 节；没有该文件时按本节要点评审，并提示可以先用 `workflow-init` 接入。

## 输入

从本次请求里取 `<topic>-tasks.md` 路径，没给就问一句。同时读同 `topic` 的 Spec 和 Plan、Tasks 里列出的提交记录与当前 diff，别只看文档自述。

## 看什么

- **方案**：实现是否满足 Spec 的验收标准、是否遵循 Plan 的技术决策；有偏差时 Tasks 里有没有记录原因与确认依据；需求范围或技术方案被改动却没走确认，属于阻塞。
- **代码**：正确性、主要路径与关键边界的测试、已修复问题的回归覆盖；类型检查是否作为独立项执行；是否夹带了与本次交付无关的改动。
- **文档同步**：Tasks 状态与实施记录是否准确完整、每个已实施任务的「提交」字段是否已回填 hash；长期文档（`product-brief.md` 等）是否按实际实现更新；文档与代码有无已知矛盾；`docs/backlog/` 相关条目是否已处理。
- **提交**：标题是否符合 `[<type>]<topic>`；任务提交是否带 `Tasks-Doc` / `Tasks` 且编号真实存在；一个 commit 是否对应一个原子变更、有没有跨越多个 Tasks 文档。

## 硬边界

**只读，不修复。** 不修改任何工作区文件、不提交、不执行 `git add` / `commit` / `checkout` 等改动仓库状态的命令。即使问题看起来很 trivial、即使请求里写了「review 并修一下」，修复也要等开发者点名后再开始。

## 输出

先给一句结论（通过 / 有 N 项需处理），再按「阻塞 / 重要 / 建议」分组。每条写清 `文件:位置`、问题、依据（引用 AGENTS.md 条款或文档原文）、具体建议。

只报实际存在的问题，不加「写得不错」这类评论，也不为了凑数制造问题；查完没发现问题就直说通过。措辞和排版类问题一律归到「建议」。
