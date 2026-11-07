---
name: workflow
description: 把《项目开发约定》作为可版本化模板接入代码仓库。init 为新仓库生成 AGENTS.md 与 docs/ 长期文档骨架（product-brief / technical-architecture / data-model / devops / backlog / delivery）；upgrade 把已有仓库升级到当前模板版本、输出差异并补齐缺失骨架。当用户要求初始化项目文档结构、生成 AGENTS.md、升级或对齐项目约定、统一多个仓库的研发规范时使用。
agent_created: true
---

# workflow

把一份只含跨项目通用条款的《项目开发约定》分发到各个代码仓库，并让它们与模板保持一致。

## 命令

| 命令 | 作用 | 是否改写文件 |
| --- | --- | --- |
| `init` | 新仓库接入：生成 `AGENTS.md` 与 `docs/` 骨架 | 只创建缺失项，不覆盖已有 |
| `upgrade` | 已有仓库升级到当前模板版本，补齐缺失骨架 | 默认只读，加 `--write` 才写入 |

平台不会解析命令参数，`init` / `upgrade` 是路由词汇，同时也用作脚本名。用户说「初始化一下项目文档」或「把这个项目升级到最新约定」都能落到对应命令，不必真的敲出这两个词。

## 识别意图

| 用户这么说 | 走 |
| --- | --- |
| 仓库里还没有 `AGENTS.md` / 首次接入 / 初始化项目文档 | `init` |
| 已有 `AGENTS.md` 要跟模板对齐 / 升级约定 / 这个项目落后了 | `upgrade` |
| 想知道有没有漂移，但别改文件 | `upgrade`（默认就是只读） |
| 要改的是约定本身 | 见「修改模板」 |

## 核心约束

- `AGENTS.md` 只承载跨项目通用条款，由模板整份生成。手工修改会在下次 `upgrade` 时被覆盖。
- 项目特有的约定写入 `docs/` 下对应的长期文档：业务规则进 `product-brief.md`，结构与技术决策进 `technical-architecture.md`，数据与迁移进 `data-model.md`，环境与运维进 `devops.md`，其余按主题新建专题文档。不要追加到 `AGENTS.md`。
- 不覆盖已有文档内容。`upgrade` 只处理 `AGENTS.md`，以及补齐缺失的 `docs/` 骨架文件。
- 写盘前必须让开发者看过差异并明确同意。

## init

先预演，让开发者看到将创建哪些文件，确认后再落盘。

```bash
python <skill>/scripts/init_project.py --root <项目路径> --dry-run
python <skill>/scripts/init_project.py --root <项目路径>
```

脚本行为：

- `AGENTS.md` 不存在则按模板创建；已存在则跳过并提示改用 `upgrade`。
- 逐份创建缺失的 `docs/` 骨架文件，已存在的一律不动。
- 创建 `docs/backlog/`、`docs/delivery/` 空目录并放 `.gitkeep`。
- 未检测到 Git 仓库时给出提示，但不阻塞。

初始化后提醒开发者填写 `docs/` 各骨架的实际内容；骨架里的空章节不代表已完成。

## upgrade

先只读报告，把版本差和具体 diff 呈现给开发者，取得同意后再写入。

```bash
python <skill>/scripts/upgrade_project.py --root <项目路径>
python <skill>/scripts/upgrade_project.py --root <项目路径> --write
```

脚本行为：

- 从 `<!-- agents-md-template: x.y.z -->` 读出双方版本；项目侧无标记时报「未标记」，按首次接入处理。
- 比较前统一换行符、去 BOM、忽略行尾空白，避免纯格式差异产生噪音。
- 有差异时输出统一 diff（默认截断 200 行，`--full-diff` 看全部）。
- `--write` 时先把 `AGENTS.md` 备份到 `.workflow/backups/AGENTS.md.<时间戳>.bak`，再整份写入模板，并补齐缺失骨架。
- `--check` 在有差异时退出码为 1，供 CI 或提交前钩子使用，不改变文件。

升级完成后，向开发者交代三件事：版本从哪个到哪个、`AGENTS.md` 的实质变更点、备份文件位置。

## 常见情况处理

- **项目 `AGENTS.md` 含大段本地新增内容**：不要直接 `--write`。先说明这些内容属于项目特有约定，应迁移到 `docs/` 下对应的长期文档，迁移完成后再升级。
- **项目侧版本标记缺失**：正常走 diff + 确认流程，写入后自动带上标记。
- **`docs/` 文件名与骨架不一致**（如遗留 `dev-ops.md`）：提示改为骨架名并合并内容；脚本只创建缺失项，不删除旧文件，交由开发者决定。
- **`docs/` 下有模板之外的文档**：脚本会列出但不处理。专题文档本就允许存在，属于正常情况。
- **只想确认有无漂移**：跑 `upgrade` 不带 `--write`，读完报告即可；CI 里用 `--check`。

## 修改模板

模板是这个 skill 的唯一事实来源，远端 gist 只是历史来源。

1. 编辑 `assets/templates/AGENTS.md` 或 `assets/templates/docs/` 下的骨架。
2. 提升 `AGENTS.md` 顶部 `agents-md-template:` 的版本号，让各项目能识别变更。
3. 各项目重新运行 `upgrade`。

## 文件说明

| 路径 | 用途 |
| --- | --- |
| `assets/templates/AGENTS.md` | 通用约定正文，含版本标记 |
| `assets/templates/docs/*.md` | 四份长期文档骨架 |
| `scripts/init_project.py` | `init`：创建 AGENTS.md 与 docs/ 骨架 |
| `scripts/upgrade_project.py` | `upgrade`：比对与升级，支持 `--write` / `--check` |
| `scripts/_common.py` | 两个脚本共用的路径与文件工具 |

## 后续能力

交付文档（Spec / Plan / Tasks）不设生成脚本：约定已逐节定义内容，由 AI 按 `AGENTS.md` 直接撰写，比套空骨架更贴合实际需求。

- 交付收尾检查：对照约定第 5 节逐项校验验收标准、Tasks 状态、文档同步、backlog 更新。落地时会新增第三个命令。
- 提交信息校验：检查 `[type]topic` 标题与 `Tasks-Doc` / `Tasks` 字段，可作为 commit-msg 钩子。
- 任务与提交对应校验：校验 Tasks 中回填的 hash 存在于历史，且与提交正文的 `Tasks` 字段互为对应。
