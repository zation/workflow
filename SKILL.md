---
name: workflow
description: 把《项目开发约定》作为可版本化模板落地到代码仓库，负责创建与同步仓库根目录的 AGENTS.md 及 docs/ 长期文档骨架（product-brief / technical-architecture / data-model / devops / backlog / delivery）。支持新仓库初始化、已有仓库的模板版本比对与整份同步、缺失骨架补齐，以及 CI 场景的漂移检测。当用户要求初始化项目文档结构、生成或更新 AGENTS.md、同步开发约定、统一多个仓库的研发规范时使用。
agent_created: true
---

# 项目开发约定：创建与同步

把一份只含跨项目通用条款的《项目开发约定》分发到各个代码仓库，并保证它们与模板保持一致。

## 核心约束

- `AGENTS.md` 只承载跨项目通用条款，由模板整份生成。手工修改会在下次同步时被覆盖。
- 项目特有的约定写入 `docs/` 下对应的长期文档：业务规则进 `product-brief.md`，结构与技术决策进 `technical-architecture.md`，数据与迁移进 `data-model.md`，环境与运维进 `devops.md`，其余按主题新建专题文档。不要追加到 `AGENTS.md`。
- 不覆盖已有文档内容。同步只处理 `AGENTS.md`，以及补齐缺失的 `docs/` 骨架文件。
- 写盘前必须让开发者看过差异并明确同意。

## 判断场景

| 情况 | 动作 |
| --- | --- |
| 仓库根目录没有 `AGENTS.md` | 初始化：`scripts/init_project.py` |
| 已有 `AGENTS.md`，要与模板对齐 | 同步：`scripts/sync_project.py` |
| 只想确认是否漂移（提交前 / CI） | `scripts/sync_project.py --check` |
| 要改的是约定本身 | 见「修改模板」 |

## 初始化新项目

先预演，让开发者看到将创建哪些文件，确认后再落盘。

```bash
python <skill>/scripts/init_project.py --root <项目路径> --dry-run
python <skill>/scripts/init_project.py --root <项目路径>
```

脚本行为：

- `AGENTS.md` 不存在则按模板创建；已存在则跳过并提示改用同步。
- 逐份创建缺失的 `docs/` 骨架文件，已存在的一律不动。
- 创建 `docs/backlog/`、`docs/delivery/` 空目录并放 `.gitkeep`。
- 未检测到 Git 仓库时给出提示，但不阻塞。

初始化后提醒开发者填写 `docs/` 各骨架的实际内容；骨架里的空章节不代表已完成。

## 同步已有项目

先只读报告，把版本差和具体 diff 呈现给开发者，取得同意后再写入。

```bash
python <skill>/scripts/sync_project.py --root <项目路径>
python <skill>/scripts/sync_project.py --root <项目路径> --write
```

脚本行为：

- 从 `<!-- agents-md-template: x.y.z -->` 读出双方版本；项目侧无标记时报「未标记」，按首次接入处理。
- 比较前统一换行符、去 BOM、忽略行尾空白，避免纯格式差异产生噪音。
- 有差异时输出统一 diff（默认截断 200 行，`--full-diff` 看全部）。
- `--write` 时先把 `AGENTS.md` 备份到 `.workflow/backups/AGENTS.md.<时间戳>.bak`，再整份写入模板，并补齐缺失骨架。
- `--check` 在有差异时退出码为 1，可用于 CI 或提交前钩子。

同步完成后，向开发者交代三件事：版本从哪个到哪个、`AGENTS.md` 的实质变更点、备份文件位置。

## 常见情况处理

- **项目 `AGENTS.md` 含大段本地新增内容**：不要直接 `--write`。先说明这些内容属于项目特有约定，应迁移到 `docs/` 下对应的长期文档，迁移完成后再同步。
- **项目侧版本标记缺失**：正常走 diff + 确认流程，写入后自动带上标记。
- **`docs/` 文件名与骨架不一致**（如遗留 `dev-ops.md`）：提示改为骨架名并合并内容；脚本只创建缺失项，不删除旧文件，交由开发者决定。
- **`docs/` 下有模板之外的文档**：脚本会列出但不处理。专题文档本就允许存在，属于正常情况。
- **只想看某处差异**：用 `--check` 判断有无漂移，或直接读脚本输出的 diff 片段。

## 修改模板

模板是这个 skill 的唯一事实来源，远端 gist 只是历史来源。

1. 编辑 `assets/templates/AGENTS.md` 或 `assets/templates/docs/` 下的骨架。
2. 提升 `AGENTS.md` 顶部 `agents-md-template:` 的版本号，让各项目能识别变更。
3. 各项目重新运行 `scripts/sync_project.py`。

## 文件说明

| 路径 | 用途 |
| --- | --- |
| `assets/templates/AGENTS.md` | 通用约定正文，含版本标记 |
| `assets/templates/docs/*.md` | 四份长期文档骨架 |
| `scripts/init_project.py` | 初始化仓库：创建 AGENTS.md 与 docs/ 骨架 |
| `scripts/sync_project.py` | 比对与同步，支持 `--write` / `--check` |
| `scripts/_common.py` | 两个脚本共用的路径与文件工具 |

## 后续能力（v1 未实现）

交付文档（Spec / Plan / Tasks）不设生成脚本：约定已逐节定义内容，由 AI 按 `AGENTS.md` 直接撰写，比套空骨架更贴合实际需求。

- 交付收尾检查：对照约定第 5 节逐项校验验收标准、Tasks 状态、文档同步、backlog 更新。
- 提交信息校验：检查 `[type]topic` 标题与 `Tasks-Doc` / `Tasks` 字段，可作为 commit-msg 钩子。
- 任务与提交对应校验：校验 Tasks 中回填的 hash 存在于历史，且与提交正文的 `Tasks` 字段互为对应。
- 模板远端刷新：从 URL 拉取并更新内置副本，自动提升版本号。
