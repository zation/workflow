---
name: workflow-tasks
description: 根据已确认的 Spec 与 Plan，把方案拆成可验证的任务，生成或订正 <topic>-tasks.md。Use when 用户说拆一下任务、生成 tasks 文档、把方案拆成 T001 起的任务清单。产出带三位递增编号、状态、目标与完成条件、依赖与执行顺序的任务清单。允许回头订正 Spec / Plan，但不执行任何任务、不改代码、不提交。需要按 Tasks 文档实现时改用 workflow-implement；看文档本身写得对不对用 workflow-review-docs，看代码实现和提交结果用 workflow-review-tasks。
agent_created: true
---

# workflow-tasks

判断基准是目标仓库 `AGENTS.md` 的「交付文档」与「标准开发流程」第 3 节；没有该文件时按本节要点执行，并提示可以先用 `workflow-init` 接入。

## 输入

从本次请求取 `<topic>` 或 Plan 路径，没给就问一句。必须读同 `topic` 的 Spec 和 Plan，以及开发者点名的相关代码与文档。

开工前确认两个门槛：Spec 与 Plan 都已经过开发者确认；`AGENTS.md` 要求的方案固化 docs 提交已经发生。任一不满足就停下说明，不代为提交，也不先斩后奏。

## 只做这一步

- 在 `docs/delivery/` 下生成或订正 `<topic>-tasks.md`，与 Spec、Plan 共用同一 `topic` 前缀。
- 任务编号从 `T001` 起三位递增，同一文件内不重复、不重新编号；任务标题可以不用 kebab-case。
- 每个任务在实施前写清：状态、目标与完成条件、必要依赖、修改范围（仅在有助于明确边界时填写）；并在文档中说明执行顺序和依赖关系。状态取值见 `AGENTS.md` 第 3 节（`pending` / `working` / `blocked` / `done` / `cancelled`），本阶段一律 `pending`。
- 引用 Spec 的业务规则与 Plan 的技术设计，不复述正文、不复制测试策略、不逐函数复述实现。
- 实施后字段（实施结果、验证、提交 hash、必要的问题与决策）一律不写入，既不预填也不写空占位，由 `workflow-implement` 实施后补充；这里不置 `working`、不标 `done`。
- 交付收尾的全量检查列为最后一个任务，但不执行它；按 `AGENTS.md`，收尾任务不设「提交」字段。
- **允许回头订正，不往前走**：发现 Spec 或 Plan 有矛盾、验收标准不可验证、设计有缺口时，可以订正同 `topic` 的 Spec 或 Plan 并说明改了什么、为什么。订正不等于开始实现，也不自动视为已确认。
- 订正发生在方案固化 docs 提交之后时，已固化版本与当前文档不再一致：提醒开发者重新确认，并自行重做或追加这次 docs 提交；本技能不代做，也不把订正当成提交已完成。
- 不改长期文档、不动已归档的交付文档。

## 硬边界

- 不改代码，不跑测试 / 类型检查 / lint / 构建（这些属于任务实施验证），不把任何任务推进到 `working` 或 `done`。
- 不创建 commit，不执行 `git add` / `commit`。
- 不转调 `workflow-implement` 或 review 技能；写完停在本阶段。
- 不因为「顺手就能做完」而开始实现，即使请求里同时提到了实现。

## 完成后

用一小段说明：写了哪个文件、拆了几个任务、是否订正了上游文档、还有哪些待确认问题。提醒开发者：Tasks 只是执行安排，按它实现请用 `workflow-implement`；本技能停在这里，不启动下一步。
