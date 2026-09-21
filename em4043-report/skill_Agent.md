<!-- Agent ? Skill/Plugin ?? ??? Markdown?? ??? ?? -->

NTT社内用

# Agent、Skill 与 Plugin 使用目录

快速了解各类智能体和能力组件的用途、清单信息，以及它们如何组合完成任务。

**阅读提示：**本目录整理现有清单与已核对的实现关系，根据业务发展随时变更。版本:v0.1

## 1. 文档目的

本文定义 Agent 管理菜单的分类、列表字段、对象关系与运行概念，供产品、运维和开发人员统一理解当前清单。菜单分为业务/官方 Agent、系统 Agent、辅助 Agent、Skill 和 Plugin 五个区块。此文档整理现有目录数据及实现关系，不代表所有对象都已启用、可访问或正在运行。

本文中的“官方 Agent”是便于菜单组织的业务分类，指原始 `Agent` 清单里的常规主智能体。它不是已核实的数据库类型、供应商认证、权限等级或独立运行时。数据模型里的 `master`、`sub`、`audit` 才是 Agent 类型，两者不能互换。

## 2. 菜单结构

```text
Agent 管理
├── 业务 Agent（菜单显示：官方 Agent）
├── 系统 Agent
├── 辅助 Agent
├── Skill 管理
└── Plugin 管理
```

Agent 区块按用途浏览；Skill 与 Plugin 区块管理可被 Agent 组合使用的能力。一个 Agent 可以直接关联辅助 Agent、Skill、Plugin、Connector 和模型。Plugin 也可以关联 Skill 和 Connector。某个功能是否真的进入一次运行，要看该 Agent 的有效配置和具体调用路径。

## 3. Agent 对象规格

### 3.1 通用字段

ESM `aigc_work_agents` 模型中已确认 Agent 具有名称、显示名称、描述、类型、角色提示词、用户提示词、版本、扩展元数据、启用状态及排序等字段。管理界面的原始清单还显示操作列。下表描述菜单规格；“需确认”表示源清单没有足够信息，不能据此实现权限或编辑规则。

| 字段 | 用途 | 规格说明 |
| --- | --- | --- |
| 智能体名称 `name` | 稳定的英文标识 | 用于程序查找和关联；创建后应保持唯一。 |
| 显示名称 `display_name` | 面向管理员的名称 | 列表和详情的主要标题。 |
| 描述 `description` | 说明适用任务 | 原始清单以省略号截断的内容必须从详情读取，不应猜补。 |
| 类型 `type` | 执行结构类型 | 已确认的实现值包括 `master`、`sub`、`audit`；与菜单分类分别展示。 |
| 排序 `order` | 同一分区内排序 | 源清单为“—”，代表没有提供排序值。 |
| 操作 | 查看 Agent 详情 | 原始清单明确显示“详情”。编辑、删除、复制等操作及权限规则需由产品另行定义。 |

Agent 详情可包含 `role` 系统提示词、`user_prompt` 用户提示词、版本、metadata、模型、子 Agent、Plugin、Skill 和 Connector 关联。敏感提示词或 Connector 凭据不应出现在普通列表摘要中。

### 3.2 业务 Agent（菜单显示：官方 Agent）

此分区对应原始 Agent 清单里的主要业务智能体。清单条目按原有名称、显示名和状态登记。显示名中的“主智能体”不替代数据库 `type` 字段。

| 智能体名称 | 显示名称 | 目录说明 |
| --- | --- | --- |
| `ESEC-main-agent2` | ESEC主智能体2 | 原清单未提供 |
| `ESEC-main-agent` | ESEC主智能体 | 负责调度子 Agent 完成诊断 |
| `aiops_master` | AIOps主智能体 | IDC 运维协作与诊断；源说明已截断 |
| `incident_master` | 故障申报主智能体 | IDC 运维协作；源说明已截断 |
| `information_collection_master` | 信息收集/意图识别主智能体 | 初步收集工单信息并识别用户意图 |
| `fault_diagnosis_master` | 故障诊断主智能体 | 信息收集完成后，基于已收集故障信息诊断；源说明已截断 |
| `troubleshooting_advisor` | 排查建议主智能体 | 根据故障诊断结论给出排查与处置建议 |
| `cutover_master` | 资产割接 | 解析割接范围、风险和影响；源说明已截断 |
| `consult_master` | 咨询主智能体 | 负责问题理解、定性和知识检索；源说明已截断 |
| `change_master` | 变更申请主智能体 | 变更请求处理；源说明原文截断 |
| `incident_master1` | Master智能体（废弃） | 故障申报专属主调度 Agent；源说明已截断 |

源目录将 `incident_master1` 标为“废弃”，但状态列为空。菜单应显示废弃标记，并将数据库启用状态单独呈现，不能把“废弃”直接转换成已禁用。

### 3.3 系统 Agent

此分区登记由系统流程使用的内建或后台 Agent。双下划线名称是源清单中的标识约定；具体调用点仍应以业务代码核实。源清单中的“主智能体/子智能体”类型照录，未提供的类型和状态不补猜。

| 智能体名称 | 显示名称 | 目录说明 | 类型 |
| --- | --- | --- | --- |
| `__stage_summary_agent__` | 方案阶段总结助手 | 阶段完成时，根据阶段主会话历史生成结构化总结 | 子智能体 |
| `__user_input_refine_agent__` | 用户输入润色助手 | 改善语法、补足信息并提升表达清晰度 | 子智能体 |
| `__data_distillation_agent__` | 数据蒸馏智能体 | 从已完成工单诊断记录中提取运维经验并生成或更新知识；源说明已截断 | 子智能体 |
| `__knowledge_select_agent__` | 知识库筛选 | 筛选适用知识库 | 主智能体 |
| `__knowledge_rag_agent__` | `knowledge_rag_agent` | 用于 RAG 查询 | 主智能体 |
| `__issue_distill_agent__` | 历史任务知识蒸馏智能体 | 蒸馏已完成历史任务相关知识 | 主智能体 |
| `__context_compress_agent__` | 上下文压缩智能体 | 压缩会话消息并生成摘要 | 主智能体 |
| `__memory_extraction_agent__` | 记忆提取智能体 | 在任务执行期间提取记忆信息 | 主智能体 |
| `__issue_audit_agent__` | 审计智能体 | 用于任务审计 | 未提供 |

### 3.4 辅助 Agent

此分区登记可供主流程组合调用的子智能体及特定用途 Agent。下列目录类别是管理视图；运行时仍由 Agent 关联、执行器和工作流配置决定。

| 智能体名称 | 显示名称 | 目录说明 | 类型 |
| --- | --- | --- | --- |
| `ESEC-sub-agent-d` | ESEC子智能体d | 原清单未提供 | 子智能体 |
| `ESEC-sub-agent-c` | ESEC子智能体c | 原清单未提供 | 子智能体 |
| `ESEC-sub-agent-b` | 子智能体b | 结果总结 | 子智能体 |
| `ESEC-sub-agent-a` | 子智能体a | 数据收集 | 子智能体 |
| `common_role` | 通用对话智能体 | 绑定到业务主 Agent 的通用对话子 Agent；源说明已截断 | 子智能体 |
| `jira_issue_query` | Jira工单查询 | 调用 Jira MCP 查询工单并提取故障处理信息；源说明已截断 | 子智能体 |
| `strange_AI` | 测试打卡子智能体 | 被调用时输出打卡消息 | 子智能体 |
| `report` | reporter | 总结问题方案与处理步骤 | 子智能体 |
| `ultra_plan` | 多智能体并行规划 | 使用多个智能体规划 | 子智能体 |
| `plan` | 计划智能体 | 分析任务并生成计划 | 子智能体 |

## 4. Skill 菜单规格

Skill 是可按需加载的指令、流程或领域知识包。Skill 和 Agent 是不同对象：Skill 不等于 Agent，也不因显示在目录中就代表已绑定或自动执行。ESM 的 Agent 加载路径会汇总直接关联以及通过 Plugin/项目带入的 Skill，再生成技能摘要供执行链路使用。

建议列表字段：名称、描述、来源、版本、更新状态、启用状态、安装时间、操作。原始目录把多种来源的数据放在一个列表中，来源空白或状态为破折号时保留“未提供”，不要据此认定该 Skill 的真实来源或激活状态。

| Skill 名称 | 描述摘要 |
| --- | --- |
| `handover-report` | 依据 Jira 评论生成工单交接总结；源说明已截断 |
| `firecrawl-web-scraping` | 搜索关键词、筛选网页并提取结果 |
| `new-skill` | 测试必填项的技能 |
| `admin-su-report` | 统计当天全部工单 |
| `report-admin` | 汇总告警数量、状态和后续处理 |
| `jira-ticket-history-query` | 查询 Jira 工单及相关工单的处理时间线；源说明已截断 |
| `info-query-router` | 将信息查询意图路由到对应渠道；源说明已截断 |
| `md-to-office-converter-mcp` | 将 Markdown 转换为 Excel 或 Word |
| `md-to-office-converter` | Markdown 到 Excel 与 Word 的转换 |
| `incident-troubleshoot-advice` | 在根因分析完成并经用户确认后，查询知识并提出处理建议 |
| `incident-root-cause-analysis` | 故障信息收集完成并经用户确认后，检索相似知识并分析根因 |
| `incident-intent-collection` | 识别故障意图并收集信息 |
| `batch-issues-comments` | 汇总工单、父工单及相关子工单的评论脉络 |
| `kb-solution-advisor` | 匹配知识库经验并推荐解决方案 |
| `ticket-closure-report` | 重新查询 Jira 后生成工单结案报告；源说明已截断 |
| `skill-invocation-test` | 仅在精确触发码 `PROBE-7f3a9c` 出现时运行自检 |
| `csc-admin-alert-briefing` | 面向 CSC 管理员的告警简报；源说明已截断 |
| `agent-browser` | 浏览器自动化 CLI Skill |

原始清单顶部还列出快捷入口 `firecrawl`、`multi-project-issue-statistics`、`single-project-issue-statistics`、`/handover-report`、`/jira-ticket-history-query`、`/incident-intent-collection`。这些是入口/命令记录，不额外推断为独立 Skill 数据对象。

### 快捷方式（工具）

| 名称 | 命令 / 描述 |
| --- | --- |
| 意图识别与信息收集 | `/incident-intent-collection` 开始... |
| 根因分析 | `/incident-root-cause-analysis` ... |
| 排查 / 提供处理建议 | `/incident-troubleshoot-advice` ... |
| 交接班报告 | `/handover-report` 请为我生成交接班报告[请输... |
| 结案报告 | `/ticket-closure-report` 请为我输出当前... |
| md转换office | `/md-to-office-converter` 使用md转o... |
| 查询工单信息 | `/jira-ticket-history-query` 查询工... |
| reportforadmin | `/report-admin` 作为管理员admin 是面向系统... |
| 工具添加测试 | 用于测试添加的工具 |
| firecrawl-web-scraping | web搜索并得出结果 |

### 任务方案关联

#### 通用

#### 故障申报

| 任务方案 | 方案名称 | 阶段名称 | 阶段显示名称 | 关联工具 | 工具描述 | 已关联 |
| --- | --- | --- | --- | --- | --- | --- |
| 故障申报 | incident | info_gathering | 意图识别与信息收集 | 意图识别与信息收集 | `/incident-intent-collection` 开始... | 是 |
| 故障申报 | incident | info_gathering | 意图识别与信息收集 | 交接班报告 | `/handover-report` 请为我生成交接班报告... | 否 |
| 故障申报 | incident | info_gathering | 意图识别与信息收集 | 查询工单信息 | `/jira-ticket-history-query` 查询工... | 否 |
| 故障申报 | incident | info_gathering | 意图识别与信息收集 | firecrawl-web-scraping | web搜索并得出结果 | 否 |
| 故障申报 | incident | deep_diagnosis | 根因分析 | — | — | — |
| 故障申报 | incident | troubleshooting_recommendations | 排查建议 | — | — | — |

![任务方案与阶段配置关系图](incident-task-scheme.svg)

#### 信息咨询

| 任务方案 | 方案名称 | 阶段名称 | 阶段显示名称 | 关联工具 | 工具描述 |
| --- | --- | --- | --- | --- | --- |
| 信息咨询 | knowledge_test | test | 初步诊断 | — | — |
| 信息咨询 | knowledge_test | reporter | 整理归档-admin | — | — |
| 信息咨询 | info_con | info_collection | 咨询协助 | — | — |
| 信息咨询 | info_con | reporter | 总结报告（admin | — | — |

![信息咨询任务方案关系图](information-consultation.svg)

#### 变更申请

| 任务方案 | 方案名称 | 方案显示名称 | 阶段名称 | 阶段显示名称 | 阶段任务目标 |
| --- | --- | --- | --- | --- | --- |
| 变更申请 | bgsqcllc | 变更申请处理流程 | info_gathering | 信息收集与初步分析 | 收集工单信息，解析变更对象、变更内容、期望时间，查询资产配置... |
| 变更申请 | bgsqcllc | 变更申请处理流程 | risk_assessment | 风险评估 | 评估变更风险等级、影响范围与可回滚性，结合设备负载情况给出建... |
| 变更申请 | bgsqcllc | 变更申请处理流程 | plan_generation | 变更方案生成 | 生成包含前置检查、变更步骤、回滚方案、变更后验证清单的变更方... |
| 变更申请 | bgsqcllc | 变更申请处理流程 | report | 变更建议报告生成 | — |

![变更申请任务方案关系图](change-application.svg)

#### 资产割接

| 任务方案 | 方案名称 | 方案显示名称 | 阶段名称 | 阶段显示名称 | 阶段任务目标 |
| --- | --- | --- | --- | --- | --- |
| 资产割接 | cutover_master | 资产割接流程 | info_gathering | 割接信息收集与范围解析 | — |
| 资产割接 | cutover_master | 资产割接流程 | risk_and_impact | 割接风险与影响评估 | — |
| 资产割接 | cutover_master | 资产割接流程 | plan_generation | 割接方案生成 | — |
| 资产割接 | cutover_master | 资产割接流程 | report | 割接方案报告生成 | — |

![资产割接任务方案关系图](asset-cutover.svg)

## 5. Plugin 菜单规格

Plugin 是可关联到 Agent 的能力组合项。ESM 数据关系允许 Plugin 关联 Skill 和 Connector，也允许 Agent 直接关联 Plugin。Worker Agent Engine 的加载器按执行路径合并 Agent 直接绑定与 Plugin 及项目 Plugin 引入的 Connector、Skill。Plugin 本身不应描述成独立执行的 Agent；实际功能由关联资源及其调用方完成。

| Plugin 名称 | 显示名称 | 描述 |
| --- | --- | --- |
| `batch-issues-comments` | 工单评论汇总 | 未提供 |
| `plugin_test` | 插件调用检测 | 检测插件是否正常调用 |
| `report_plugin` | `report_plugin` | 面向管理者生成报告 |
| `jira_plugin` | jira插件 | jira插件 |

## 6. Connector 清单

| 连接器名称 | 显示名称 | 描述 | 类型 |
| --- | --- | --- | --- |
| mcp-atlassian | Jira MCP | mcp-atlassian 远程 MCP Server：Jira 检索/创建/流转 | MCP服务 |
| Zabbix MCP | Zabbix MCP | 连接 Zabbix MCP 服务器，读取数据 | MCP服务 |
| query_device_logs | 查询设备日志 | 查询设备的日志情况 | MCP服务 |

## 7. 关联与调用流程

```text
用户请求 / 项目任务
        ↓
业务 Agent（通常由 Master 类型承担入口；以具体调用配置为准）
        ├── 直接关联辅助 Agent
        ├── 加载直接绑定的 Skill
        ├── 关联 Plugin ──→ Plugin 提供的 Skill / Connector
        └── 关联模型、内置工具和 MCP Connector
        ↓
按需执行并返回结果

系统 Agent：由对应系统功能或后台流程显式调用；不得仅凭名称推断触发时机。
```

上述关系有实现依据：Agent 模型提供 Agent—子 Agent、Skill、Plugin、Connector 和模型关联；Plugin 模型提供 Plugin—Skill 与 Connector 关联。Engine Loader 的特定路径会载入 Agent 配置、子 Agent、直接及间接 Connector/Skill 并组装 Agent Snapshot。不同系统入口是否经过该 Loader，应以实际调用点为准。

## 8. 状态与数据质量规则

1. 严格区分菜单分组、数据库类型与启停状态。“业务/官方”“系统”“辅助”是本规格的目录分区；`master/sub/audit` 是 Agent 类型。
2. 使用英文标识作为稳定键，以显示名称作为用户界面标签。查询、绑定和跳转以标识或数据库 ID 为准，不依赖显示名称。
3. 保留源清单明确给出的“废弃”标签；未提供的数据库状态显示“未提供”，不得由名称或目录分组推断启停状态。
4. 描述中的省略号意味着原始摘要不完整；列表可显示原摘要，详情页再取完整记录，不在本规格中补写。
5. 本清单有记录时间，但没有可靠的统一导出时间、已启用字段真值、更新状态和 Skill 安装归属；界面应对缺失值使用“未提供”。
6. 执行权限、Agent/Plugin 编辑权限、禁用影响、删除保护和审计要求不能从此清单推出，须以授权与实现定义为准。

## 9. 已核对的实现依据

- ESM `AigcWorkAgent`：`esm/app/AppAgent/Models/AigcWorkAgent.php`，字段、`master/sub/audit` 类型注释，以及子 Agent、Skill、Plugin、Connector、模型和版本关系。
- ESM `AigcWorkPlugin`：`esm/app/AppAgent/Models/AigcWorkPlugin.php`，Plugin 与 Skill、Connector 及 Agent 关联。
- ESM 关联模型：`esm/app/AppAgent/Models/AigcWorkAgentSkillRelation.php`、`AigcWorkAgentPluginRelation.php`。
- Worker Engine Agent 加载：`worker-agent-engine/app/agent/loader/_impl.py`，Agent Snapshot、Connector、子 Agent 与 Skill 摘要装配。
- 用户提供的原始 Agent、系统 Agent、辅助 Agent、Skill、Plugin 清单：本文件改写前版本。目录快照内容可能随管理端配置变化。

Copyright NTT Communications China 2026
