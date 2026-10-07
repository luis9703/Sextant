# 协调者来源抽查

访问日期：2026-10-02。这是协调者在生成完成前六阶段后进行的独立回读，未向生成者或新上下文审查者提供发现。仅核对列出的主张，不把来源回读当作用户研究或对未来路径的证实。

| 来源 | 实际回读与判断 | 不能据此推出 |
| --- | --- | --- |
| [Microsoft FY26 Q4 metrics](https://www.microsoft.com/en-us/investor/earnings/fy-2026-q4/metrics) | Q426 商业云收入同比增长14%，付费商业席位增长6%；定义包含多种组织服务。生成者的数字和口径限制与表格相符。 | 不能推出桌面编辑时长增长、增长由AI造成，或未来收入必然保留。 |
| [金山办公2026半年报](https://static.cninfo.com.cn/finalpage/2026-08-20/1225482678.PDF) | PDF第6页表格营业收入3,313,262,599.20元、同比24.69%；第13页说明投资收益对利润的影响，第29页列各业务收入。报告声明未经审计。生成者的收入事实与限制成立。 | 合并收入不等于单一编辑器需求，厂商产品描述不等于实际可靠性测试。 |
| [Sway服务说明](https://learn.microsoft.com/en-us/office365/servicedescriptions/microsoft-sway-service-description) | 正文说明浏览器互动作品及Windows客户端自2026-06-01停止支持、网页服务保留。正文可读取，虽然页首有授权提示。 | 网页与原厂商共存的前例不证明商业成功或未来市场份额。 |
| [Anthropic Artifacts公告](https://claude.com/blog/build-artifacts) | 正文日期为2025-06-25，2025-10-21更新注明MCP与持久存储；互动应用、分享和修改在正文中有据。 | 持久存储不自动提供多人共同状态、跨组织协商或复杂任务可靠性；公告也不证明中国地区可达性。 |
| [Ink & Switch local-first论文](https://www.inkandswitch.com/essay/local-first/) | 原文讨论本地控制与协作、CRDT和原型；明确实验尚未满足所有理想，技术合并不消除所有应用层冲突。 | 不能把2019探索写成2026通用部署成熟度或用户需求调查。 |

额外对照：[Office Add-ins官方说明](https://learn.microsoft.com/en-us/office/dev/add-ins/overview/office-add-ins)说明HTML/CSS/JavaScript可以扩展Office，网页技术与Office并非技术上互斥。生成者已通过Sway表达相同边界；此对照没有作为新的预期答案交给它。WPS开发文档入口的一次访问超时，不从超时推断产品不存在。

截至本次抽查，未发现上述五个来源支点中足以推翻路径的事实错误。这不等于报告所有事实均已验证，也不证明路径新颖、会被采用或会发生。

## 审查新增材料的再次抽查

- [微软无人自动化说明](https://learn.microsoft.com/en-us/office/client-developer/integration/considerations-unattended-automation-office-microsoft-365-for-unattended-rpa)确实区分无人RPA授权与桌面应用在非交互环境的运行问题，并推荐Graph和直接操作Open XML等替代。它限制一种当前实现，不排除未来后台服务化；审查者保留了这项区别。
- [A2A v1.0.0规范](https://a2a-protocol.org/v1.0.0/specification/)的Cancel Task说明取消是尝试而非保证。由此区分任务取消与业务承诺撤销是适当的推理，但规范本身不证明企业采用或法律安排。
- [协商预印本摘要页](https://arxiv.org/abs/2608.14613)确实存在对应题目与方法摘要；页面显示2026-07-10提交，与编号中的2608月份表述不一致。审查者已经保留日期疑点，未将其成功率作为未来采用率。协调者只回读了摘要与元数据，没有复现或完整审计实验。该材料不宜成为本案例强结论的依据。

这些抽查未回传给生成者；用于检查生成者是否自行处理实际审查带来的新主张。
