# workflow

一个 WorkBuddy skill：把《项目开发约定》分发到各个代码仓库，并保持它们与模板一致。

仓库根目录就是 skill 根目录，克隆下来放进 `~/.workbuddy/skills/workflow/` 即可使用。

## 它解决什么

同一份开发约定在十几个项目里手工维护，很快就会出现各自增删的版本，谁也说不清哪个是最新的。

这个 skill 把约定做成带版本号的模板：新仓库一条命令生成 `AGENTS.md` 和 `docs/` 骨架，已有仓库一条命令比对差异并同步。

## 它管什么

- 在仓库根目录生成 `AGENTS.md`（通用约定：基本原则、注释规范、七步开发流程、提交规则、归档规则）
- 生成 `docs/` 长期文档骨架：`product-brief.md`、`technical-architecture.md`、`data-model.md`、`devops.md`，以及 `backlog/`、`delivery/` 目录
- 比对项目内 `AGENTS.md` 与模板的版本差，输出 diff，确认后整份同步
- 检测漂移，可作为 CI 或提交前检查

## 它不管什么

项目特有的约定不进 `AGENTS.md`，写进 `docs/` 下对应的长期文档。这样 `AGENTS.md` 才能在各项目间保持完全一致、整份覆盖而不产生冲突。

## 安装

skill 需要放在 `~/.workbuddy/skills/<skill-name>/`，目录名与 `SKILL.md` 的 `name` 一致，这里是 `workflow`。

推荐用目录联接或软链，这样 `git pull` 之后立即生效：

```bash
# Windows（无需管理员权限）
cmd /c mklink /J "%USERPROFILE%\.workbuddy\skills\workflow" "E:\Project\workflow"

# macOS / Linux
ln -s "$(pwd)" ~/.workbuddy/skills/workflow
```

也可以直接把整个目录复制过去，代价是每次更新都要重新复制。

需要分发给别人时，用 `git archive` 导出干净副本，避免把 `.git`、`.workbuddy` 等本地数据打进去：

```bash
git archive --format=zip --prefix=workflow/ -o workflow.zip HEAD
```

## 使用

```bash
# 新仓库：先预演，确认后落盘
python scripts/init_project.py --root <项目路径> --dry-run
python scripts/init_project.py --root <项目路径>

# 已有仓库：先看差异，确认后加 --write
python scripts/sync_project.py --root <项目路径>
python scripts/sync_project.py --root <项目路径> --write

# 只判断有无漂移，有则退出码 1
python scripts/sync_project.py --root <项目路径> --check
```

两个脚本默认都是只读的，只有显式加 `--write`（或 `init_project.py --force`）才写文件，覆盖前会备份到目标项目内的 `.workflow/backups/`。

## 模板版本

`assets/templates/AGENTS.md` 顶部的 `<!-- agents-md-template: x.y.z -->` 是对外的版本标识，各项目靠它判断是否需要同步。

修改模板时必须同步提升版本号，否则下游项目无从得知变更。约定如下：

| 变更 | 版本位 |
| --- | --- |
| 修正错字、调整措辞，语义不变 | patch |
| 新增或删除约束条款、调整流程步骤 | minor |
| 文档结构不兼容变更（文件改名、目录调整） | major |

## 目录结构

```
workflow/
├── SKILL.md                  # 触发条件、操作流程、常见情况处理
├── assets/templates/         # 模板正文，同步时整份拷贝到目标仓库
│   ├── AGENTS.md
│   └── docs/
└── scripts/
    ├── init_project.py       # 初始化仓库
    ├── sync_project.py       # 比对与同步
    └── _common.py            # 共用路径与文件工具
```

## 环境要求

Python 3.10+，无需第三方依赖。文件统一以 UTF-8 读写、LF 行尾输出。

## 后续计划

目前只做创建与同步，以下能力已列入 backlog（见 [SKILL.md](SKILL.md) 末尾）：

- 交付文档脚手架：按 topic 生成 `<topic>-spec.md` / `-plan.md` / `-tasks.md`
- 交付收尾检查：对照约定第 5 节逐项校验
- 提交信息校验：检查 `[type]topic` 与 `Tasks-Doc` / `Tasks` 字段，可作为 commit-msg 钩子
- 模板远端刷新：从 URL 拉取更新并自动升版本
