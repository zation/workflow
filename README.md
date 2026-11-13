# workflow

把《项目开发约定》做成带版本号的模板，并拆成 8 个独立 skill，在 WorkBuddy、Codex 等 coding agent 里都能直接点名调用。

约定正文只有一份（`assets/templates/AGENTS.md`），8 个技能共享同一套 `scripts/` 和 `assets/templates/`。

## 八个技能

| 技能 | 作用 | 是否写文件 |
| --- | --- | --- |
| `workflow-init` | 新仓库生成 `AGENTS.md` 与 `docs/` 骨架，先预演再写入 | 只创建缺失项 |
| `workflow-upgrade` | 已有仓库升级 / 对齐 `AGENTS.md`，默认只读出差异 | 确认后才写，覆盖不备份 |
| `workflow-spec` | 生成或订正 Spec：澄清需求、范围与验收标准 | 只写 `<topic>-spec.md` |
| `workflow-plan` | 生成或订正 Plan：技术方案与决策依据 | 只写 `<topic>-plan.md`，可订正 Spec |
| `workflow-tasks` | 生成或订正 Tasks 文档：把方案拆成 T001 起的任务清单 | 只写 `<topic>-tasks.md`，可订正 Spec / Plan |
| `workflow-implement` | 按指定 Tasks 文档逐任务实现、自审、验证、修复、提交，直到完成；业务问题才停下询问 | 写代码与文档、提交 |
| `workflow-review-docs` | review 指定交付的 Spec / Plan / Tasks 是否合理、同步 | **只读，不修复** |
| `workflow-review-implementations` | 按指定 Tasks 文档 review 实现结果：方案、代码、提交、文档同步 | **只读，不修复** |

三个文档技能按阶段顺序各自只产出一份交付文档：可以回头订正更早阶段的文档，但不进入下一步、不执行实现、不创建 commit。每份交付文档经开发者确认后，各自做一次 docs 提交固化；提交由开发者自行完成，`workflow-plan`、`workflow-tasks`、`workflow-implement` 开工前都会先提示「上游文档已确认，请提交」并等这个节点。

两个 review 技能是硬只读：即使问题很小、即使请求里写了「review 并修一下」，也只输出分级问题清单。

## 安装

源码一份，各平台挂目录链接即可。**对已挂载的技能，链接是实时的**：改 `SKILL.md`、`git pull` 之后内容立刻生效，不需要重装。所以重复执行安装脚本看到「已挂载」是正常的，不是没更新。

```bash
# 先看计划
python scripts/install_skills.py --dry-run --target all

# 确认后执行
python scripts/install_skills.py --target all
```

`--target` 可选 `workbuddy`（`~/.workbuddy/skills/`）、`codebuddy`（`~/.codebuddy/skills/`）、`codex`（`~/.agents/skills/`）、`all`。Windows 用目录联接（无需管理员权限），其他系统用软链。

默认只补建缺失的链接，不覆盖、不删除任何已有内容。目标目录里存在下面几种情况时会跳过并提示，加 `--force` 才处理：

| 情况 | 现象 | `--force` 的行为 |
| --- | --- | --- |
| 已存在同名真实目录 | 早期用复制方式装的旧副本，改源码不会跟着变 | 整份删掉该技能目录，改挂链接（不备份） |
| 链接指向别处 | 仓库挪过位置，旧链接还指着老路径 | 摘掉旧链接，重新挂到当前源码 |
| 链接已失效 | 源目录被删 / 改名，链接悬空 | 摘掉失效链接，重新挂 |
| 源码里已删除的技能 | 目标目录留着一个孤儿链接 | 清理该链接（只删链接，不删源码） |

`--force` 的含义是「目标目录以源码为准」：真实目录副本直接删除，不做 `.bak` 备份，所以先跑 `--dry-run` 看清要删什么。它只作用于与技能同名的目标项，不碰其他目录，也不删源码。有跳过的项时退出码为 1，可用来在 CI 里发现「有人手动复制装过」。

新挂的链接要新开会话或重启客户端才会出现在技能列表里——客户端把技能清单缓存在 `~/.workbuddy/.skill-list-cache.json`，只有新会话会重新扫描。

**技能增删或改名必须重跑安装脚本。** 链接的实时性只覆盖「已挂载技能的内容变更」；新建技能目录、删除技能、给技能改名时，目标目录里的链接不会自动跟着变。改名尤其容易踩坑：源码里把 `workflow-tasks` 改成 `workflow-implement` 后又新建了同名的 `workflow-tasks` 目录，旧链接会**静默指向新语义的技能**，安装脚本判定它「已挂载，内容实时生效」，`--force` 和孤儿链接清理都不会提示。遇到改名，先跑 `--dry-run` 看清要补哪些链接，再执行安装，并确认旧名字现在对应的是不是你要的技能；改完新开会话刷新技能列表。

也可以手动挂载单个技能：

```bash
# Windows
cmd /c mklink /J "%USERPROFILE%\.workbuddy\skills\workflow-implement" "E:\Project\workflow\skills\workflow-implement"

# macOS / Linux
ln -s "$PWD/skills/workflow-implement" ~/.agents/skills/workflow-implement
```

根目录的 `SKILL.md` 是 `workflow` 总入口（意图模糊时分流到子技能），安装脚本不处理它，也**不建议手动挂**：仓库根下面有 `skills/`，客户端扫描会递归进去，同一批 `SKILL.md` 被登记两次，技能列表里 8 个子技能各出现两份；带 `skills/` 子目录的目录还会被当成「技能集合」，根 `workflow` 自己反倒不出现在列表里。它留在原地只作为路由索引的参考文本——真要一个 `/workflow` 式的总入口，把 `SKILL.md` 单独放进一个只装它的目录再挂。

不挂它不影响 8 个子技能，直接点名 `workflow-implement` 之类的调用照常。

团队共享时，把 `skills/` 下的目录提交到目标仓库的 `.agents/skills/`（Codex、Cursor、Gemini CLI 等）或 `.codebuddy/skills/`（WorkBuddy / CodeBuddy），随仓库分发。

导出干净副本给别人时用 `git archive`，避免带入 `.git`、`.workbuddy`：

```bash
git archive --format=zip --prefix=workflow/ -o workflow.zip HEAD
```

## 调用

技能没有参数占位符，把目标路径、topic 或要点名的文件直接写在话里，由模型从本次请求里读取：

```text
WorkBuddy   /workflow-spec 给 user-login 写 spec，参考 docs/product-brief.md
            /workflow-implement docs/delivery/user-login-tasks.md
            @skill:workflow-review-docs docs/delivery/user-login-spec.md

Codex       $workflow-plan 依据 docs/delivery/user-login-spec.md 出方案
            $workflow-implement 执行 docs/delivery/user-login-tasks.md，剩下的任务跑完
            $workflow-review-implementations 看一下 docs/delivery/user-login-tasks.md 的实现结果
```

两个 `init` / `upgrade` 技能通过技能目录下的 `run.py` 转调共享脚本，需要目标仓库路径；没给就用当前工作目录并先确认。

## 直接跑脚本（不经技能）

在源码仓库目录下执行：

```bash
# init：新仓库接入，先预演，确认后落盘
python scripts/init_project.py --root <项目路径> --dry-run
python scripts/init_project.py --root <项目路径>

# upgrade：已有仓库，先看差异，确认后加 --write
python scripts/upgrade_project.py --root <项目路径>
python scripts/upgrade_project.py --root <项目路径> --write

# CI：只判断有无漂移，有则退出码 1
python scripts/upgrade_project.py --root <项目路径> --check
```

`upgrade` 默认只读，只有 `--write` 才写文件；`AGENTS.md` 会被整份覆盖，不做备份，回滚靠目标仓库的 Git 历史。

## 模板版本

`assets/templates/AGENTS.md` 顶部的 `<!-- agents-md-template: x.y.z -->` 是对外的版本标识，各项目靠它判断是否需要同步。修改模板必须同步提升版本号：

| 变更 | 版本位 |
| --- | --- |
| 修正错字、调整措辞，语义不变 | patch |
| 新增或删除约束条款、调整流程步骤 | minor |
| 文档结构不兼容变更（文件改名、目录调整） | major |

三个文档技能的阶段纪律写在各自的 `SKILL.md` 里，不进模板：`AGENTS.md` 只承载跨项目通用条款。

## 目录结构

```
workflow/
├── SKILL.md                      # workflow 总入口：路由索引，不挂进技能目录
├── skills/                       # 8 个独立技能，各自一个 SKILL.md
│   ├── workflow-init/            # SKILL.md + run.py（转调 init_project.py）
│   ├── workflow-upgrade/         # SKILL.md + run.py（转调 upgrade_project.py）
│   ├── workflow-spec/            # 生成或订正 Spec
│   ├── workflow-plan/            # 生成或订正 Plan
│   ├── workflow-tasks/           # 生成或订正 Tasks 文档（拆分任务，不执行）
│   ├── workflow-implement/       # 按 Tasks 文档逐任务实现、验证、提交
│   ├── workflow-review-docs/
│   └── workflow-review-implementations/
├── assets/templates/             # 约定正文与 docs 骨架，唯一事实来源
│   ├── AGENTS.md
│   └── docs/
└── scripts/
    ├── install_skills.py         # 把 skills/ 下的技能挂到各平台技能目录
    ├── init_project.py           # 初始化仓库
    ├── upgrade_project.py        # 比对与升级
    └── _common.py                # 共用路径与文件工具
```

`workflow-init` / `workflow-upgrade` 各带一个 `run.py`，用 `__file__.resolve()` 定位源码仓库再转调共享脚本。技能目录常以软链或目录联接挂载，相对路径里的 `..` 会在链接处被错误解析，直接写 `<skill>/../../scripts/` 会找不到文件。

## 为什么拆成多个 skill

一个 `SKILL.md` 就是一个可显式触发的名字，没有子命令，也不做 `$ARGUMENTS` 替换。要 8 个入口就只能有 8 个 `SKILL.md`。

`SKILL.md` 是 Agent Skills 开放标准，各家都认；斜杠命令（`commands/`、冒号分层、参数展开）是各平台私有的。所以这里押注内容标准：规则和脚本只留一份，入口做成薄壳，跨平台只差挂载目录和提及语法。

## 环境要求

Python 3.10+，无需第三方依赖。文件统一以 UTF-8 读写、LF 行尾输出。

## 后续计划

- 提交信息校验：检查 `[type]topic` 标题与 `Tasks-Doc` / `Tasks` 字段，可作为 commit-msg 钩子。
- 任务与提交对应校验：Tasks 回填的 hash 与提交正文互为对应。
