# Research — evidence ledger and discoveries
信息截止、读取日期均2026-10-02。以下只保存简短来源摘要/限制，不保存私有推理。所有标注“已读”为实际web open读取的相关原文，未宣称读完整个长报告。网页工具曾有一次多源open长时间未返回，被停止；随后逐项重试得到了相关正文。未返回那次不算已读。

## 最小立足点来源（延续S1–S3）
S1 Microsoft Support, Learn about file formats。https://support.microsoft.com/en-us/office/collab-files/learn-about-file-formats 。发布日期未知；已读128–131。Office默认Open XML，跨格式可能损失功能或内容。不证明别的格式不能做好。
S2 Microsoft Learn, Office for the web service description。https://learn.microsoft.com/en-us/office365/servicedescriptions/office-online-service-description/office-online-service-description 。文档更新日期未留存；已读32–41、Word/Excel/web与desktop功能表。Office有浏览器编辑，现版本具能力差异；该表不综合，厂商自己提醒可能变化。本文只用“web和Office可重叠”，不用细节作永恒限制。
S3 WPS全球AI套件功能页。https://www.wps.com/feature/ai-office-suite/ 。发布日期未知；已打开厂商现页。供初始立足点，后被日期明确的S5替代为主要依据。未实测，无准确率/质量证明。

## 关键市场、供给与不同捕获路径
S4 Microsoft Annual Report 2025。https://www.microsoft.com/investor/reports/ar25/index.html 。财年截止2025-06-30，已读Operating Segments及FY2025 comparison（260–279、498–499、561–569）。Commercial cloud收入同比增长15%、期末付费席位同比增长6%；前者不是利润，后者不是活跃率。范围包括安全、Windows、Teams、Exchange等，不是三个编辑器单独收入。支持在AI发展期仍有付费市场，不能证明编辑劳动增加或AI造成增长。厂商把AI-first应用列为竞争来源。财务口径2025有重组，不拼接旧口径趋势。未把2025称作截止日最新结果，亦不借此量化2031。
S5 金山办公2025年年度报告。https://static.cninfo.com.cn/finalpage/2026-03-26/1225032227.PDF 。披露2026-03-26，已读产品服务P9–11、讨论P15–17。P10明确金山文档基于HTML5，结合浏览器/小程序与内核服务化；P11称AI企业版可调用WPS365及客户API；属于公司产品描述，未验证效果。P17国内WPS个人业务收入334,399.59万元人民币（33.439959亿元）、累计年度付费个人用户4,615万；不是月活设备、不等于同时订阅数，更不是AI专属付费。收入包含服务，不能推断纯编辑器价格/利润。公司已有协作与AI路线，不能默认其不变。P16部分“目前”与2026展望不能自动当成2025已实现；不用其OpenClaw等描述作机制必需前提。
S6 Microsoft 365 Copilot spring announcement。https://www.microsoft.com/en-us/microsoft-365/blog/2025/04/23/microsoft-365-copilot-built-for-the-era-of-human-agent-collaboration/ 。2025-04-23，已读205–215。宣布Search/Create/Notebooks/Agent Store，Researcher/Analyst当时通过Frontier逐步推出。支持既有套件主动改变入口，未证明所有账号普及、公司全部授权或可靠执行。
S7 Anthropic, Turn ideas into interactive AI-powered apps。https://claude.com/blog/build-artifacts 。原2025-06-25，页内注明2025-10-21持久存储/MCP更新；已读181–229。对话生成可共享互动应用，包含beta及接收者账号条件。证明公开产品方向和能力入口，非长期维护成熟或替代率证据。不使用厂商巨量创建总数推导活跃、质量或收益。

## 跨域材料，既打开新路径也限制救场论
S8 SEC, Inline XBRL。https://www.sec.gov/data-research/structured-data/inline-xbrl 。2016介绍页，2018规则、页面最后更新2025-01-17；已读25–32。单一披露对象可兼顾人读及机器读并用浏览器查看。是美国指定披露范围，不等于中国合同/所有法定档案规则，也不表明JSON/AI摘要可取代原文。它反驳“网页一定不正式”，打开资料的语义与呈现分离。这里不提供法律建议。
S9 W3C Service Workers1, Candidate Recommendation 2019-11-19。https://www.w3.org/TR/2019/CR-service-workers-1-20191119/ 。已读摘要、Motivations及cache说明；提供offline bootstrap与可控缓存的机制，同时引入开发复杂性。只证明可设计，不证明任一生成HTML附件已具离线/数据持久/备份。
S10 Kleppmann等, Local-first software: you own your data, in spite of the cloud。https://www.inkandswitch.com/essay/local-first/ 。2019-04，Onward!2019论文，已读概览/ownership/offline/协作讨论。研究原型和设计原则，使数据所有权与协作不必二选一；不是总体愿付费调查，也不保证通用业务语义合并正确。
S11 Automerge官方文档Welcome。https://automerge.org/docs/hello/ 。页日期未知；已读60–79，离线本地状态、同步、版本、CRDT，JS/browser可用。工具具体用法的时点不作强断言，S10提供截止前的机制立足点。结构合并不等于两个采购承诺在业务上兼容，不能让机器并发写直接覆盖责任决定。
S12 Microsoft Graph Excel API overview。https://learn.microsoft.com/en-us/graph/excel-concept-overview 。最后更新2024-11-07；已读31–58。web/mobile能读写存储在OneDrive/SharePoint等的xlsx，使用计算能力。只限支持的文件和配置，不证明可无账户无限部署或完整替代desktop。
S13 Microsoft Graph workbook:createSession。https://learn.microsoft.com/en-us/graph/api/workbook-createsession?view=graph-rest-1.0 。最后更新2025-07-23；已读35–60。持久/非持久session不同；此endpoint仅delegated work/school，个人与application permission不支持，中国21Vianet部署不支持；不可扩写为所有Graph API均不支持。这改变D1：中国云/无人值守须另找引擎或等待接口条件改变，而非API即可通用。
S14 HyperFormula官方兼容说明与release notes。https://hyperformula.handsontable.com/docs/guide/compatibility-with-microsoft-excel.html ，https://hyperformula.handsontable.com/docs/guide/release-notes.html 。已读兼容正文104–117、日期明确release；3.4发布2026-08-10（截止前）。存在独立计算库，兼容范围/配置有限，已知语义差异。公式执行的确定性不等于模型选错公式时正确；函数覆盖不等于xlsx整个文件/宏/插件/协作兼容。不采用营销页“完全兼容”直接推断全替代。

## 调查改变了什么
1. 初始D1的“后台引擎存活”不是自动保卫Microsoft/WPS：S12打开入口，S13限制当前配置，S14打开第三方价值捕获。新的分岔是可替代函数/任务先脱离，而非全部旧文件必须迁走。
2. D3资料包不必全靠模型重新读非结构化文档：S8给出呈现与语义同居的制度性立足点。发信人/收信人谁有权控制故事出现实际冲突，值得后续展开。
3. D5固定承诺不依附docx或PDF。S8/S9/S10允许网页/本地状态生成共同快照；套件“因为合规永远存在”的救场论须撤除。
4. D2/D9新消费可以走“本地自有工具+分享”，不用云门户。S10/S11让退出平台和接力维护变为一条独立条件路线。研究没有发现普及率，仍可条件探索。
5. S4/S5证明历史付费市场和动态供给，不能证明未来护城河。HTML渗透、传统编辑器使用强度、AI付费细分、跨组织真实迁移成本未取得可比统计。

## 最近已有解释与本次增量
常规已有供给叙事：套件内Copilot/灵犀、AI原生应用、低代码/网页工具、local-first。D1/D2都并非新发明。需要发展的增量是后续人际关系：接收方不接受发方定好的故事；微工具持续使用产生共同维护及社区接力；丰裕之后让人有权结束交付。无原创性宣称。
停止更多调查的理由：此时更多功能发布新闻不能回答人怎样选择和需求怎样变化。商业/文化行为仍须未来观察，继续罗列新闻不会使其成为事实；转入二次创造与发展。保留关键信息缺口，不称穷尽研究。
