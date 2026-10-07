# 对账与路径深化验证材料

保留各轮实际输入、早期产物、审查、修订与报告。生成者和审查者均以 `fork_turns=none`、`model=gpt-6-luna` 启动，生成者只收到冻结 Skill 和原题，审查者只收到中性包和链接来源；没有提供旧输出、诊断或预期答案。

alpha.3 的两个完整运行：

- [软件原题](alpha3/software-by-nonprogrammers/request.md)、[报告](alpha3/software-by-nonprogrammers/run/report.md)、[处置记录](alpha3/software-by-nonprogrammers/run/08-reconcile.md)、[验证](alpha3/software-by-nonprogrammers/run/verification.json)。
- [独居原题](alpha3/living-alone-networks/request.md)、[报告](alpha3/living-alone-networks/run/report.md)、[处置记录](alpha3/living-alone-networks/run/08-reconcile.md)、[验证](alpha3/living-alone-networks/run/verification.json)。

[alpha.3输入摘要](alpha3-skill-manifest.json)及其[完整冻结Skill](alpha3-skill/SKILL.md)一并保存，旧回执可用其中的匹配工具读取。文件字节与原运行一致。不能使用当前契约的拒读结果改判旧运行的历史结构状态。

alpha.3 的报告绑定通过，但独居处置的一项引用被定位到错误小节。这个失败保留在原始输出中，促成 alpha.4 的行号与原文位置校验。它不因为后续修复就被追记为成功。

alpha.4 又做了一次无旧输出、无诊断提示的新上下文 Luna 独居原题运行：[原题](alpha4/living-alone-networks/request.md)、[报告](alpha4/living-alone-networks/run/report.md)、[实际审查](alpha4/living-alone-networks/run/07-review.md)、[处置](alpha4/living-alone-networks/run/08-reconcile.md)、[验证](alpha4/living-alone-networks/run/verification.json)。[冻结输入](alpha4-skill/SKILL.md)与[摘要](alpha4-skill-manifest.json)一并保留。

该运行的7个引用定位和报告绑定检查通过，但报告仍把2010年普查资料误写成2020年。阅读原始报告时请同时看[协调者事实更正](alpha4/coordinator-audit.md)；它不是语义全通过的正例。

前六阶段与中性包计划约15分钟、审查约6分钟、协调约8分钟；生成者在包完成后停下，由协调者直接启动新上下文审查，收到实际回复后再继续。实际Token未知，不能从文件大小或时间目标推算。完整分析见[验证记录](../../results/2026-10-02-reconciliation-and-depth.md)。
