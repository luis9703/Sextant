# 审查后的定点事实补充 — 2026-10-02
回应R5，仅补关键外部接入范围，不把reviewer记忆当证据，不覆盖04-research.md。
S15 WPS开放平台WebOfficeSDK网页概述：https://open.wps.cn/documents/app-integration-dev/docs-center/online-preview-edit/web/summary 。实际open全26行。说明iframe嵌入在线文档、初始化/事件/Application对象调用；SDK与在线服务不同。可支持外部网页文档操作路线，不等于无前台的通用服务端计算API。
S16 同平台API概述：https://open.wps.cn/documents/app-integration-dev/docs-center/online-preview-edit/client/summary 。实际open，0–29行及示例。前提是开发者后台建应用、实现并调通回调、业务前端SDK初始化文档；分doc/xlsx/ppt/pdf等对象。原则上VBA风格兼容不等于所有宏/业务语义等价。没有实测此团队模型。
S17 同平台定价：https://open.wps.cn/documents/app-integration-dev/docs-center/price/detail 。实际open全83行。WebOffice预览编辑按应用/日峰值并发阶梯计费，自然月结算并有月最低收费；还描述转换另计费。最终不报单价，因未核实际套餐/该团队合同和历史版本。计费对象不是每个人的WPS个人会员，不可与Graph随意做每席位价格比较。数据边界/授权需求仍需具体合同与回调实现核对。
上述动态文档未显发布时间；供2026-10-02现页的当前范围描述，不推断更早日期功能何时实现。
S18 WPS365官方博客：https://plus.wps.cn/blog/p125097.html ，open显示2026-07-29。描述外部ISV/企业开放平台方向；页末明确部分内容由AI辅助/匹配关键词生成。只用作厂商定位线索，不采用“能力更完整、私有化安全、同类独有”的营销比较；技术与可购范围以SDK/价格文档为依据，不能单靠该博客取消未决条件。
事实处置：R5所指“年报内部内核服务化不等于任意外部API”接受；补证表明外部WebOffice文档SDK路线存在，但不能把它宣布为GraphcreateSession的等价后端。若限定中国小团队只需有用户在场的计划文档共同修改，可考察浏览器SDK集成；若要求无人值守服务端试算/特定模型/不出边界，仍未核到所需端点、授权、费用和数据协议。Microsoft与WPS不能只换品牌名保持一切实现不变。

访问限制：SDK更新日志链接返回空正文，回调说明链接404；未将其记为已读。尚未核对具体回调字段/认证与数据留存边界。该缺口在比较中保持未决，不宣称不存在。
