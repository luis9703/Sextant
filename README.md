# Sextant · 未来路径探索

[English](README.en.md) · [Skill](skills/sextant/SKILL.md) · [完整示例](examples/ai-delegation-2035/report.md) · [验证记录](evals/results/2026-09-07.md)

**从今天的一个现象，展开有依据、敢于想象、可以修正的未来路径。**

Sextant 是一个开放的 Agent Skill。你提供一种新能力、一篇论文、一种行为变化或一个困惑，它帮助你探索：哪些默认假设可能改变，人会产生什么新的欲望和行为，世界可能沿哪些路径演化，以及接下来观察什么。

当前版本 **0.1.0-alpha.1**。这是可试用的方法原型，尚未证明优于普通模型提问、领域专家或其他前瞻方法，也没有经过长期预测成绩验证。“先知”表达探索愿景；结果保留事实、假设、情景和未知的区别。

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

发散会用到共识审计、远距离类比及其失效处、欲望与身份、形态移除、稀缺迁移和反馈。研究既寻找反证，也带来新的组合材料。研究模式在宿主支持且授权范围允许时使用新上下文审查；无法隔离时如实说明。输出数量、年份和概率不会为了填模板而强行确定。

**安装。** 需要一个支持读取 Skill 的代理宿主。研究能力由宿主提供；这个仓库不运行常驻服务，也不要求额外 API 密钥。安装与仓库检查脚本使用 Python 3.10+ 标准库；Skill 本身是 Markdown。

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

安装器复制完整的 `sextant` 文件夹；目标已存在时退出，保留现有安装。`--dry-run` 可以预览目标。也可以手动复制 `skills/sextant/` 到宿主配置的 Skill 目录。升级时先检查并保留你的定制版本，再处理旧安装；此安装器不覆盖或合并旧文件。

当前官方文档列出的 Codex 个人目录为 `~/.agents/skills`，Claude Code 为 `~/.claude/skills`。如果使用定制或较早版本，请按该宿主实际配置指定目标。[Codex 官方说明](https://learn.chatgpt.com/docs/build-skills)、[Claude Code 官方说明](https://code.claude.com/docs/en/skills)

安装后在 Codex 用 `$sextant`，在 Claude Code 用 `/sextant`，或明确要求使用该 Skill。若未显示，检查目录与宿主配置，并按官方说明重新加载或重启。仓库的验证记录区分了隔离调用测试与客户端自动发现，不代表所有宿主已经实测。

**选择工作深度。**

| 模式 | 适合什么 | 结果 |
| --- | --- | --- |
| 探索 | 快速拓展一个想法 | 简短未来路径，标出未研究前提 |
| 研究 | 希望有材料依据的完整推演 | 来源、两轮候选变化、路径、审查与观察信号 |
| 更新 | 有旧案例和新证据 | 受影响判断、修订理由、保留的历史 |

你可以指定时间跨度、地域、关注人群、资料范围与研究预算。未提供时，代理采用明确的合理假设；不清楚的关键范围才需要进一步交流。

需要文件的研究默认写到 `sextant-runs/<case-id>/`：`exploration.md` 记录简短候选、证据和修改，`report.md` 面向读者。它们不会自动发布，也不会因为有“观察清单”就创建定时监测。仓库示例是经选择的公开材料。

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

这些检查验证打包、引用路径和安装行为；创造性、事实解释与预测成绩仍需单独评估。当前实际验证范围与未完成项目见[验证记录](evals/results/2026-09-07.md)。
