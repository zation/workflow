---
name: workflow-init
description: 为尚未接入约定的仓库生成 AGENTS.md 与 docs/ 长期文档骨架，先预演再写入，只创建缺失文件。Use when 用户说初始化项目文档、生成 AGENTS.md、给新仓库接入开发约定、补齐 docs 骨架。产出创建与跳过清单。已有 AGENTS.md 需要更新时改用 workflow-upgrade；不用于 review 或执行任务。
agent_created: true
---

# workflow-init

把《项目开发约定》接入一个新仓库。约定正文只有一份，在共享模板 `assets/templates/AGENTS.md`；本技能不复制、不改写它。

## 做之前

从本次请求里确定目标仓库路径，没给就用当前工作目录，并向开发者确认一次。

先预演，把将要创建的文件列给开发者看，明确同意后再写入。

## 执行

直接调用本技能目录下的 `run.py`，它会定位源码仓库并转调共享脚本：

```bash
python <SKILL_DIR>/run.py --root <目标仓库> --dry-run
python <SKILL_DIR>/run.py --root <目标仓库>
```

先取得本 SKILL.md 所在目录的绝对路径再替换 `<SKILL_DIR>`，不要假设当前工作目录就是技能目录。

不要自己拼 `<SKILL_DIR>/../../scripts/init_project.py`：技能目录常以软链或目录联接挂载，相对路径里的 `..` 会在链接处被错误解析，脚本会找不到。

## 边界

- 已存在的文件一律不覆盖。`AGENTS.md` 已存在时默认停止，提示改用 `workflow-upgrade`；只有开发者明确要求覆盖时才加 `--force`（脚本会先备份）。
- 不填写 `docs/` 骨架的正文。创建后提醒开发者按实际项目填写，空章节不等于已完成。
- 不猜测业务规则，不替开发者决定项目特有约定。
- 不修改 `run.py` 与共享脚本；要改行为请改源码仓库里的 `scripts/init_project.py`。

## 完成后

说明创建了哪些文件、跳过了哪些，并提醒：项目特有约定写进 `docs/` 下对应的长期文档，不要追加到 `AGENTS.md`。
