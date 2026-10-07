# Sextant · 未来路径探索

[English](README.en.md) · [Skill](skills/sextant/SKILL.md) · [完整示例](examples/ai-delegation-2035/report.md) · [本轮校准](evals/results/2026-10-02-imagination-priority.md)

**从今天的一个现象，展开有依据、敢于想象、可以修正的未来路径。**

Sextant 是一个开放的 Agent Skill。你提供一种新能力、一篇论文、一种行为变化或一个困惑，它帮助你探索：哪些默认假设可能改变，人会产生什么新的欲望和行为，世界可能沿哪些路径演化，以及接下来观察什么。

当前版本 **0.2.0-alpha.9**。这是可试用的方法原型，尚未证明优于普通模型提问、领域专家或其他前瞻方法，也没有经过长期预测成绩验证。“先知”表达探索愿景；结果保留事实、假设、情景和未知的区别。

主要价值是发现常规框架容易漏掉的未来：把能力从当前用途里拆出来，寻找意外用途、互补条件和新需求，再推演生活与产业怎样变化。历史资料提供材料和约束，未来假说可以没有先例；当下事实仍需写准，不能把有引用等同于有想象力。

当前实现区分来源支持的事实纠正与审查者建议的机制修补；当前产品可作为起点，其重要属性可以在条件探索里改变。宿主支持独立上下文时，可用[选定输入任务包](skills/sextant/references/independent-exploration.md)分别发展不同机制，再整合。脚本只复制选定材料、保存快照和返回调用参数，不调用模型、判断想象质量或增加完成闸门。[本轮实现与对照记录](evals/results/2026-10-06-exploration-and-review.md)区分已实现行为和实际效果。

**可以这样使用。**

> 我看到 AI 已经能替人完成一些多步骤线上任务。请探索到 2035 年，普通人的工作、消费和人际关系可能怎样变化。请有依据地展开不同未来，也寻找常见讨论没有充分展开的方向。

> 如果一种原来稀缺的能力变得很便宜，下一种稀缺会是什么？请从人的欲望、身份和制度变化出发推演。

> 这是上次的推演和新出现的证据。请更新受影响的路径，保留旧判断，解释为什么改变。

**它怎样工作。**

```mermaid
flowchart LR
    A[最小事实核对] --> B[第一次发散]
    B --> C[定向研究]
    C --> D[第二次发散]
    D --> E[路径连接与审查]
    E --> F[未来图景与观察信号]
    F -->|新证据| C
```

发散会用到共识审计、远距离类比及其失效处、欲望与身份、形态移除、稀缺迁移和反馈。研究既寻找反证，也带来新的组合材料。默认完整深度推演，不能因为用户说“想象一下”就变成速答。审查同时检查事实和被过早压制的想象，接受的修正需要落实到正文。输出数量、年份和概率不会为了填模板而强行确定。

**安装。** 需要一个支持读取 Skill 的代理宿主。研究能力由宿主提供；这个仓库不运行常驻服务，也不要求额外 API 密钥。安装、仓库检查与阶段记录脚本使用 Python 3.10+ 标准库；方法指令保持 Markdown。

```sh
git clone https://github.com/luis9703/Sextant.git
cd Sextant
```

在 Codex 中安装到个人 Skill 目录：

```sh
python3 scripts/install_skill.py --to "$HOME/.agents/skills"
```

在 Claude Code 中安装到个人 Skill 目录：

```sh
python3 scripts/install_skill.py --to "$HOME/.claude/skills"
```

WorkBuddy 使用安装时适配，保留此前的宿主显示字段：

```sh
python3 scripts/install_skill.py --to "$HOME/.workbuddy/skills" --host workbuddy
```

通用源码仅保留标准 frontmatter；`agents/workbuddy.json` 是本项目安装器使用的扩展配置，安装器把其字段写入 WorkBuddy 的复制版，方法正文保持一致。它不是 WorkBuddy 原生清单格式。已有安装仍不会被覆盖；直接链接通用源码不会应用这层显示字段，请按[宿主说明](skills/sextant/references/hosts/workbuddy.md)选择安装方式。实际宿主加载和各模型行为仍需分别验证。

安装器复制包含许可证的完整 `sextant` 文件夹；目标已存在时退出，保留现有安装，源目录内部的目标与包内符号链接也会被拒绝。`--dry-run` 可以预览目标。通用版本也可以手动复制 `skills/sextant/` 到宿主配置目录。升级时先检查并保留定制版本，再处理旧安装；此安装器不覆盖或合并旧文件。文件系统错误会明确报告，部分写入的安装目录保留供检查，不会被下一次安装自动覆盖。

当前官方文档列出的 Codex 个人目录为 `~/.agents/skills`，Claude Code 为 `~/.claude/skills`。如果使用定制或较早版本，请按该宿主实际配置指定目标。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 官方说明](https://code.claude.com/docs/en/skills)

安装后在 Codex 用 `$sextant`，在 Claude Code 用 `/sextant`，或明确要求使用该 Skill。若未显示，检查目录与宿主配置，并按官方说明重新加载或重启。仓库的验证记录区分了隔离调用测试与客户端自动发现，不代表所有宿主已经实测。

**选择工作深度。**

| 模式 | 适合什么 | 结果 |
| --- | --- | --- |
| 深度 deep（默认） | 完整探索未来的生活、行为与制度变化 | 两次发散、定向研究、路径深化、事实与创造性审查、修订与阶段回执 |
| 扩展 extensive | 用户希望投入更多资源 | 增加独立候选探索、陌生领域资料、分支交互与分开的审查 |
| 简短 brief | 用户明确要求快速、简短 | 有界草图，仍区分事实和假设，不声称完成深度流程 |

更新旧案例是一种操作，不是自动降级的档位。资源不足或工具失败时，保留已完成工作并记录缺口，不能把未完成的 deep 运行悄悄改称 brief。

你可以指定时间跨度、地域、关注人群、资料范围与研究预算。未提供时，代理采用明确的合理假设；不清楚的关键范围才需要进一步交流。

完整推演默认写到新的 `sextant-runs/<case-id>/`。从自动生成的`00-current.md`读取当前路径综合、报告与历史版本。九阶段材料和`run-state.json`保留原记录，审查前综合可以追加新版本；对账绑定当前综合与报告，并要求每项已登记异议有处置及对应摘录，支持中文标签。检查不证明来源真实、修订充分或想象有价值。旧版记录保持原样，使用匹配版本读取。详情见[执行约定](skills/sextant/references/execution.md)和[本轮实测修订](evals/results/2026-10-05-execution-contract.md)。

**阶段内部可以继续展开。** [演化与比较工作台](skills/sextant/references/development.md)把值得深挖的问题放进可恢复的工作队列：一类先假设关键条件成立，追踪普通事件、他人响应和重复使用如何改变世界；另一类固定一个情境，比较不同人为什么选择、放弃或迁移，以及什么条件会反转选择。商业问题再区分需求、使用、付费与收入归属，非商业问题不强套市场分析。宿主执行实际研究与创造，脚本保存输入、依赖和结果，通过`next`返回可继续的工作。待办未完成时不能登记完整路径或对账；两类都有结果也不代表想象已经足够深入。实际改进见[验证记录](evals/results/2026-10-02-development-workbench.md)。

资源配置见 [depth-profiles.json](skills/sextant/assets/depth-profiles.json)。工程默认目标为 deep 合计 5 万–10 万 Token、extensive 合计 10 万–20 万；尚未通过预算对照证明这些区间最优。可修改配置、把目标设为 null，或给单次运行指定区间。目标不是实耗、硬上限或必须花完的额度。真实输入、输出、缓存和推理用量需要宿主统计，无法取得时记为未知。

阶段工具的调用示例（从仓库根目录运行；初始化目标必须尚不存在）：

```sh
python3 -B skills/sextant/scripts/run_control.py init --run sextant-runs/my-case --topic "我的未来问题" --budget-min 50000 --budget-max 100000
python3 -B skills/sextant/scripts/run_control.py next --run sextant-runs/my-case
```

以上命令从仓库根目录执行；安装副本使用该Skill内脚本的实际路径。`next`在实际阶段或工作步骤返回目标、完成标准、当前输入、可打开的参考路径和调用参数；`plan_work`只提示缺少的工作种类与工作台指南，不提前要求综合。预算含义随返回值提供。审查可以保存为忠实的异议摘要，并说明范围；摘要压缩不自动成为未完成，外围未使用线索也不必全部复核。执行状态与未决内容分别记录。早期路径`partial`在工作补齐并由审查后当前综合承接后不再阻塞，原回执仍保留；已登记异议的摘录须显式带编号。见[本轮小范围修订](evals/results/2026-10-05-imagination-workflow-fixes.md)。

更高预算优先支持不同机制的候选、跨领域材料、分支深化和反对意见的处理，而非更长的最终报告。Skill 与回执工具不能替代宿主的强制编排，也不保证所有模型自动执行一致。结果不会自动发布，观察清单也不会自动建立定时监测。

**阅读与参与。**

- [完整示例](examples/ai-delegation-2035/report.md)及其[过程记录](examples/ai-delegation-2035/exploration.md)：阅读实际输出与限制。
- [产品设计](docs/01-product-and-architecture.md)与[研究依据](docs/02-research-and-evaluation.md)：了解设计取舍；保留早期快照用于对照。
- [评估方式](evals/README.md)与[行为用例](evals/cases.md)：检查有支撑的认知增量，避免用好文笔代替新想法。
- [贡献指南](CONTRIBUTING.md)：欢迎失败案例、反例、来源更正与宿主兼容性报告。
- [版本记录](CHANGELOG.md)与[MIT 许可证](LICENSE)。

本地运行检查：

```sh
python3 -B scripts/check_project.py
python3 -B -m unittest discover -s tests -v
```

这些检查验证打包、引用路径和安装行为；创造性、事实解释与预测成绩仍需单独评估。参见[发布审查](evals/results/2026-09-09-release-review.md)及[仍为部分完成的行为验证](evals/results/2026-09-08-depth.md)，首次版本的验证保留在[历史记录](evals/results/2026-09-07.md)。
