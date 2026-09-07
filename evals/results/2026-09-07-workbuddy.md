# 验证记录：WorkBuddy 兼容性，2026-09-07

本记录只登记实际完成的测试，并按[评估方式](../README.md)中的证据等级标注每项结论。没有做的事写"未做"，中断的事写"中断"。执行环境：macOS 上的 WorkBuddy 5.5.3 会话。

本记录与[同日的前向案例记录](2026-09-07.md)分开：那一份是完整示例，这一份只是宿主兼容性，两者不能互相代替。

## 1. 改了什么

目标是让 Sextant 在 WorkBuddy 下能被触发、能被管理、能正确交付，**不改动任何方法论逻辑**。

| 文件 | 动作 |
| --- | --- |
| `skills/sextant/SKILL.md` | frontmatter 新增 `agent_created`、`display_name`、`display_name_en`、`description_zh`、`description_en`、`visibility`；`description` 保留原英文首句，原第二、三句（英文的能力说明与反向排除）由中文能力句、触发词与反向排除句覆盖（单行，285 字符）；正文新增 1 行宿主条件引用 |
| `skills/sextant/references/hosts/workbuddy.md` | 新增。只写宿主执行方式，不改动任何方法论要求 |

`references/` 三份核心资料、`assets/` 模板、九阶段正文语义、`scripts/`、`tests/`、`README.md`、`README.en.md`、`CHANGELOG.md`、版本号：**全部未动**。

## 2. 打包验证（等级：打包验证）

| 项目 | 结果 |
| --- | --- |
| `python3 -B scripts/check_project.py` | 通过：0 错误，0 警告；检查了 Skill frontmatter、版本一致、45 个文档链接、5 个 Skill 内部链接（原 4 个，新增宿主附录链接）、1 个示例、34 个文本文件（原 30 个：+宿主附录、+本记录、+仓库 `.workbuddy/` 下 2 个记忆文件） |
| `python3 -B -m unittest discover -s tests` | 通过：17 个测试全部通过（与改动前一致，无回归） |
| 版本号一致性 | `metadata.version` 保持 `0.1.0-alpha.1`，README / README.en / CHANGELOG 未动，`check_versions` 零影响 |
| `git diff --stat`（已跟踪文件） | `skills/sextant/SKILL.md` 9 增 1 删；`.gitignore` 新增 1 行（`.workbuddy/`，见第 2 节末） |
| 正文方法学校验 | 与 git HEAD 逐行比对：九阶段正文零改动，仅 frontmatter 7 行与 1 行宿主引用为新增 |
| 备份完整性 | `~/.workbuddy/skills/sextant.bak-20260907` 与 git HEAD 的 `skills/sextant` **逐字节一致**，可无损回退 |

**两处必须守住的坑**：`scripts/check_project.py` 的 `parse_frontmatter` 是手写解析器，不支持 YAML 折叠块 `>`。`description` 必须写成单行，多行写法会直接让 `test_repository_passes_check` 失败。同一脚本的路径扫描会检查仓库内所有文本文件的**内容**（不限 skill 目录），且**连在文档里引用这些模式的字面量都会触发**——仓库 `.workbuddy/` 记忆文件第一版就因此产生 4 个错误，拆开字符串后恢复 0 错误。因此仓库任何文档里只能用 `~/.workbuddy/skills` 这类写法，不能出现具体用户路径。

**审计追加（同日稍后）**：发现 WorkBuddy 在仓库内自动生成的 `.workbuddy/memory/` 未被 `.gitignore` 覆盖，存在被提交进公开仓库的风险（机器相关记录不应进公开提交）。已在 `.gitignore` 的「Credentials and local agent settings」段加入 `.workbuddy/`。这是仓库卫生项，不涉及任何方法论或脚本逻辑。

## 3. 安装（等级：打包验证）

| 步骤 | 结果 |
| --- | --- |
| 改动前 `diff -rq` 现有安装与仓库 | 一致（除本次改动外无差异） |
| 备份 | 原复制版 `mv` 为 `~/.workbuddy/skills/sextant.bak-20260907`（可逆，未删除） |
| 安装方式 | 符号链接：`~/.workbuddy/skills/sextant` → 仓库 `skills/sextant` |
| 通过链接读取 | `SKILL.md` 9239 字节可读；`references/hosts/workbuddy.md` 5561 字节可读；`-L` 列出全部 7 个文件，无缺失 |

未使用 `install_skill.py`（它只支持 Codex / Claude Code 的目标目录，且不覆盖已有安装）。未改动该脚本。

**已知风险，未实测**：WorkBuddy 能否正确加载符号链接技能尚未证实。本机 7 个 `dify-*` 技能是符号链接，只能证明可以这样放，不能证明能加载。需要新开会话看技能列表确认；不生效则回退复制模式（备份仍在）。iCloud 若把文件回收为未下载状态，链接会失效。

## 4. 触发测试（未做）

计划的 6 条测试问句（T1–T3 期望命中，T4–T5 期望不命中，T6 为边界）**未执行**：触发测试必须在未加载本技能的新会话中进行，当前会话已加载。留待后续新开会话逐条跑，结果补记于此。

同样未做的还有：不指定技能时的**客户端自动发现**测试，与显式说"用 sextant"时的**隔离调用**测试。这两件事在证据等级里分开，不能互相代替。

## 5. 宿主兼容性

| 宿主 | 测试类型 | 结果 |
| --- | --- | --- |
| WorkBuddy 5.5.3，macOS | 文件落盘与读取 | 通过：符号链接可读，7 个文件齐全，内容为新版本 |
| WorkBuddy 5.5.3 | 客户端自动发现（中文提问触发） | 未做 |
| WorkBuddy 5.5.3 | 隔离调用（显式指定 sextant） | 未做 |
| WorkBuddy 5.5.3 | 阶段 6 用 `Agent` 做无生成历史审查 | 未做 |
| WorkBuddy 5.5.3 | `skill_manage` 能否改/删（`agent_created` 是否生效） | 未做 |
| Claude Code / Codex 回归 | 改动后是否影响原宿主 | 未做 |

## 6. 本记录允许的结论

- 改动通过打包检查，17 个既有测试无回归。
- 符号链接安装后文件可读、完整。
- 不能据此声称 WorkBuddy 会正确加载、触发或运行该技能——三项均未实测。
- `display_name`、`description_zh`、`description_en`、`visibility`、`agent_created` 是否被 WorkBuddy 实际识别：未证实，仅与本机已装技能的既有写法对齐。
