# 三次 Luna 测试的原始材料

三个案例均为构造的现实感请求，生成者与审查者分别以 `fork_turns=none`、`model=gpt-6-luna` 启动。生成者只收到请求与冻结 Skill；审查者只收到中性包及其来源。没有提供历史案例、设计稿、评测结论或预期答案。整个测试过程使用同一份[方法输入摘要](skill-manifest.json)，没有中途修改 Skill。[冻结输入Skill](input-skill/SKILL.md)一并归档，供对应版本回执的复查使用。

| 案例 | 输入 | 最终报告 | 审查原文 | 处置记录 |
| --- | --- | --- | --- | --- |
| 软件与组织 | [请求](software-by-nonprogrammers/request.md) | [报告](software-by-nonprogrammers/run/report.md) | [审查](software-by-nonprogrammers/run/07-review.md) | [协调](software-by-nonprogrammers/run/08-reconcile.md) |
| 独居与互助 | [请求](living-alone-networks/request.md) | [报告](living-alone-networks/run/report.md) | [审查](living-alone-networks/run/07-review.md) | [协调](living-alone-networks/run/08-reconcile.md) |
| 制造与维修 | [请求](distributed-making/request.md) | [报告](distributed-making/run/report.md) | [审查](distributed-making/run/07-review.md) | [协调](distributed-making/run/08-reconcile.md) |

生成者先完成六阶段并准备中性包，然后停止。协调者直接启动新的审查代理，记录实际包与实际回复，再把真实回复交回生成者完成协调和交付。前六阶段及审查材料保持冻结，最终结构状态由回执工具生成。前段计划约 15 分钟、审查约 6 分钟、协调约 8 分钟；这些上限不是有效思考时长、必须消耗的预算或完整深度的证明。真实 Token 用量均未知。

三个生成者使用了不同的临时目录层次。制造案例的中性包与审查原文起初在运行目录外，协调者为登记回执将它们按原字节复制到运行目录内；没有改写内容或直接编辑 state。归档把三个运行目录统一放到各案例的 `run/` 下，文件字节和 state_fingerprint 与原运行一致；没有回写原始案例。机器上的临时绝对路径不公开。

完成后另启动一个新上下文 Luna 代理，只读三个案例的生成与修订材料，形成[横向审查](cross-review.md)。这是产物复核，不是第四次前向未来推演。评测协调者的结论与不同意见见[综合诊断](../../results/2026-10-02-luna-three-cases.md)。
