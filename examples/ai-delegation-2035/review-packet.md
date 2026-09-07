> 本文件是生成代理交给独立审查者的材料包原文，复制自运行目录，只把一处本机临时目录路径替换为占位符。审查者没有收到其他文件。

# 审查简报（供无生成历史的审查者使用）

## 任务
你是一位独立审查者。下面是一个前瞻探索案例的问题、范围、候选路径、假设与证据。请只依据本简报和你自己对来源的核验进行审查。不要猜测作者是谁、作者偏好哪条路径；本简报不含排序或结论。

## 问题
用户原话："我看到 AI 已经能替人完成一些多步骤线上任务。请探索到 2035 年，普通人的工作、消费和人际关系可能怎样变化。请有依据地展开不同未来，也寻找常见讨论没有充分展开的方向。"

## 范围与截止
- 信息截止日：2026-09-07。晚于此日的信息不应使用。
- "普通人"取为：不拥有 AI 公司、不做前沿研究的一般雇员、自由职业者、家庭成员、消费者。
- 地区：以互联网渗透率高的经济体为主，证据允许时区分中国与美欧。
- 目的：拓展可考虑的未来；不做投资建议或行动计划。

## 已采用的假设（可挑战）
1. 代理能力的关键单位是"任务成功率随任务时长/可靠性要求的分布"，而不是"能否替人"。
2. 委托是否增加取决于三件事：任务落在哪个可靠性桶、授权与责任制度、代理的法律身份；不单取决于模型能力。
3. 关系变化的相当部分来自代理中介的日常沟通与谈判，而不只是 AI 伴侣。
4. 中国与美欧的差异不仅是平台结构，还包括国家目标与官方消费话语。

## 候选路径（中性描述；可重叠；无排序）

**P1 例外处理的生活。** 任务分为"总能成 / 总不成 / 时成时败"三桶；分钟级任务被无形代办，普通人的注意力集中在"时成时败"桶：分拣、盯梢、兜底、核验。办事成本下降导致办事量膨胀（投诉、申请、争议由代理发起，对方也用代理回应），接收方以摩擦、收费、真人到场要求反制。工作上出现"监督代理"类任务；消费上是常备指令；关系受影响较小。

**P2 围墙内的代理。** 平台通过法律与技术手段拒绝第三方代理，代理主要存在于平台自有入口（电商平台、支付平台、超级 App 的代理）。"你的代理"实际上是平台的代理，默认入口捕获消费决策。变体：在中国，政策目标推动智能体普及并把政务办理全程智能化，"不使用"成为需要克服的摩擦；在美国，边界由诉讼与平台条款逐案确定。

**P3 真人溢价。** "有真人参与"成为服务中的付费层与关系中的信号；人际能力在劳动力市场相对升值；入门岗位从"做事"转向"盯代理与到场"，经验积累路径断裂；"亲手做"成为身份表达，部分人以拒绝委托为边界宣言。

**P4 授权社会。** 支付与身份基础设施把"人在场"与"人不在场"的代理行为变成法律-技术类别；普通人日常管理授权粒度、限额与代理责任保险；令人不适的人际事务（谈判、投诉、催款、分手后勤、共同育儿安排）交给代理，出现代理对代理的谈判；沟通中"被察觉的 AI 使用"与"实际使用"的效应分离，形成披露礼仪的拉锯。

**P5 收缩为起草者。** 因注入攻击等安全问题未解或发生大规模代理欺诈事件，监管与平台把代理限制为"起草与建议"，执行仍需人确认；生活结构变化不大，主要影响落在入门工作与 AI 起草的沟通上。

**候选还包含以下关于"常见讨论较少展开"的声明（请核对是否确有较近的既有讨论）：** (a) "时成时败"桶作为日常体验中心；(b) 沟通中的披露悖论；(c) "发送便宜、接收昂贵"导致真人到场要求回归；(d) 代理的法律身份由法院与平台条款决定；(e) 授权书作为新的消费契约；(f) 监督成为入门工作与经验断层；(g) 国家目标推动的代理普及与官方"情感消费"话语；(h) 非使用者与拒绝作为身份；(i) 任务作为社交黏合剂的消失（此条无证据，标为推测）。

## 证据（访问日 2026-09-07）
- E1 XLANG Lab, Introducing OSWorld-Verified（2025-07-28）https://xlang.ai/blog/osworld-verified ：人类基线约 72%，当时最佳 60.76%；失效因素含验证码、机器人封锁、页面变化、时序；领先模型成绩主要来自人类操作轨迹数据。
- E2 Anthropic, Piloting Claude in Chrome（2025-08-26，更新 2025-11-24）https://www.anthropic.com/news/claude-for-chrome ：自主模式注入攻击成功率 23.6%→11.2%（123 用例/29 场景）；先 1,000 试点用户，后向全部 Max 用户开放；高风险动作需确认。厂商自报。
- E3 METR, Measuring AI Ability to Complete Long Tasks（2025-03-19）https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/ ：50% 时间视野约每 7 个月翻倍；<4 分钟任务近 100%，>4 小时 <10%（当时）。
- E4 METR, Time Horizons 页面（更新 2026-05-08）https://metr.org/time-horizons/ ：视野≈低语境新人能完成的任务；GPT-5 在 90 分钟–3 小时任务上约 1/3 总成、1/3 总败、1/3 时成时败；注"超过 16 小时的测量不可靠"。
- E5 Simular, Sai tops OSWorld 2.0（2026-08-28）https://www.simular.ai/articles/sai-tops-osworld-2-0 ：108 个 >1 小时任务；部分得分 73%/70.6%/62.6%，完全成功 28.25%/23.14%/13.10%；每任务 $15.70–$26.62；2025-12 Agent S 在 OSWorld 1.0 达 72.6%（人类 72.36%）。厂商自报。
- E6 Stanford DEL, Canaries in the Coal Mine?（2026-08 修订）https://digitaleconomy.stanford.edu/publications/canaries-in-the-coal-mine/ ：22–25 岁在 AI 暴露职业就业低 19%；替代型 vs 补充型用法差异；调整通过就业而非工资。
- E7 Humlum & Vestergaard, NBER w33777 https://www.nber.org/papers/w33777 ：丹麦；两年后收入与工时精确零效应（排除 >2%）；新任务：内容生成、AI 监督、AI 集成。
- E8 Anthropic Economic Index, Economic primitives（2026-01-22，数据 2025-11）https://www.anthropic.com/research/anthropic-economic-index-january-2026-report ：Claude.ai 增强型对话略过半，API 以自动化为主；成功率随任务时长下降；采用度与人均 GDP 相关。厂商。
- E9 Shao et al., WORKBank, arXiv:2506.06576 https://arxiv.org/abs/2506.06576 ：1,500 从业者、844 任务；意愿×能力四区；核心能力转向人际。
- E10 Google Cloud, AP2（2025-09-16）https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol ：60+ 机构；意向/购物车授权书；"人在场/人不在场"两类。厂商。
- E11 Cloudflare, pay per crawl（2025-07-01）https://blog.cloudflare.com/introducing-pay-per-crawl/ ：HTTP 402 向 AI 爬虫收费。
- E12 CourtListener 案卷 Amazon v. Perplexity, 3:25-cv-09514 https://www.courtlistener.com/docket/71874820/amazoncom-services-llc-v-perplexity-ai-inc/ ：2026-03-09 准予初步禁令；2026-08-04 第九巡回撤销并发回；案件继续。判决理由未读。
- E13 Adobe（2025-03-17）https://blog.adobe.com/en/publish/2025/03/17/adobe-analytics-traffic-to-us-retail-websites-from-generative-ai-sources-jumps-1200-percent ：生成式 AI 来源流量 +1,200%；39% 用过 AI 购物；转化率低 9%（此前低 43%）。厂商。
- E14 authoryze 博客（2026-08-13）https://authoryze.ai/blog/the-reasons-agentic-commerce-hasnt-taken-off-yet ：商户因拒付责任不明而观望。观点。
- E15 CX Dive, Klarna（2025-05-11）https://www.customerexperiencedive.com/news/klarna-reinvests-human-talent-customer-service-AI-chatbot/747586/ ：重新招人，承诺始终可找真人。二手。
- E16 Common Sense Media（2025-07-16）https://www.commonsensemedia.org/research/talk-trust-and-trade-offs-how-and-why-teens-use-ai-companions ：美国青少年近 3/4 用过 AI 伴侣；1/3 曾选 AI 而非真人谈严肃话题。倡导机构。
- E17 Fang et al., arXiv:2503.17473 https://arxiv.org/abs/2503.17473 ：n=981 四周 RCT；分配条件无显著效应；自愿高用量者结果更差。
- E18 Hohenstein et al., Sci Rep 2023 https://www.nature.com/articles/s41598-023-30938-9 ：智能回复占 14.3%；速度 +10.2%；被感知的 AI 使用评价负面、实际使用改善观感。
- E19 Pew（2025-09-17）https://www.pewresearch.org/science/2025/09/17/how-americans-view-ai-and-its-impact-on-people-and-society/ ：50% 更担忧；关系能力 50% 认为变差 vs 5% 变好。
- E20 国务院"人工智能+"意见（2025-08-26）https://www.gov.cn/zhengce/content/202508/content_7037861.htm ：2027 年智能体普及率 >70%，2030 年 >90%；陪伴型应用、情感消费、无人与人工服务结合、全程智能办理政务。
- E21 网信办等《人工智能生成合成内容标识办法》（2025-09-01 施行）https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm ：显式/隐式标识。
- E22 Villa et al., Prismata, arXiv:2607.08147 https://arxiv.org/abs/2607.08147 ：网页代理注入问题仍活跃；最小权限防御。
- E23 Daniel Stenberg, Death by a thousand slops（2025-07-14）https://daniel.haxx.se/blog/2025/07/14/death-by-a-thousand-slops/ ：AI 低质安全报告约 20%，有效率降至约 5%。
- E24 CNNIC 报告列表 https://cnnic.cn/6/86/88/index.html ：仅确认第 57 次报告（2026-02-05）与生成式 AI 应用报告（2025-10-23）存在；用户规模数字未取得。

## 反证与限制（已知）
- 丹麦数据的零效应（E7）与美国年轻人缺口（E6）并存；两者口径不同。
- 初步禁令已被撤销（E12），"平台关门"在法律上未决。
- 内容方倾向"收费开放"而非封死（E11）。
- RCT 未发现分配因果效应（E17）；青少年数据来自倡导机构（E16）。
- 多数能力数字来自厂商自报（E2、E5、E8、E10、E13）。
- 未取得：求职申请量等直接"办事量膨胀"数据；中国实际采用率；OpenAI 代理产品页面（403）；Gartner 代理项目取消率（人机验证）。发现渠道有限（arXiv、HN、已知网址），"最近似既有讨论"核对不完整。

## 请你区分并逐条给出
1. 事实矛盾，或来源不支持其被用来支持的前提（请尽量核验原始来源）。
2. 缺失的过渡、资源、行动者回应、文化条件或延迟。
3. 可信的替代解释，或以不同方式失败的类似案例。
4. 可以保持显式但不能称为已确立的推测条件。
5. 能强化候选的修补，或能开出另一条路的失败。
另外：对"常见讨论较少展开"的 (a)–(i) 各项，指出你所知的最近似既有讨论（给出名称或出处；不确定就说不确定）。
输出格式：每条挑战写明——挑战内容、依据、建议处置（保留/修订/降级/删除/未决）、剩余分歧。用中文，简洁，不要复述简报。

## 环境说明
- 本环境的 WebSearch 与 WebFetch 工具当前报错。核验来源请用 Bash：`curl -sL -A "Mozilla/5.0" <URL> -o <文件>`，再用 python3 或 grep 读取；临时文件放在：<本机临时目录>/review/
- 若遇到验证码或人机验证，不要绕过，标注"不可达"。
- 不要读取本简报之外的任何项目文件（包括同目录下的其他文件及项目中的 docs、evals、examples、history 等）。
- 核验来源以 10 次抓取为限；完成后直接输出审查文本。
