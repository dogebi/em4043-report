# TICKET-009 补偿扫描激活 pending 工单测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | TICKET-009 |
| 测试标题 | 补偿扫描激活 pending 工单 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 管理端手动启动 pending/draft 工单会重新匹配任务方案，但未找到定时补偿扫描 pending 工单的命令或调度配置。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 16 定义 `TICKET-009` 要求管理员新增配置后，补偿扫描定时发现 pending 工单并激活。 |
| 检查重新匹配能力 | PASS | `WorkIssueRepository::startIssue()` 启动前重新调用 `resolvePlanForIssueType()`，再调用 `tryMatchAutomation()`。 |
| 检查状态 pending→active | PARTIAL | 手动启动命中方案时可创建 active 会话，但这是用户触发，不是补偿扫描。 |
| 检查定时补偿扫描 | FAIL | `rg` 未发现 pending 工单补偿扫描命令，`app\Console\Kernel.php` 也未调度相关命令。 |
| 执行补偿扫描 | NOT RUN | 无可执行补偿扫描入口。 |

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Repositories\WorkIssueRepository.php`
- `D:\dev\cscAI\esm\app\Console\Kernel.php`

## 当前结论

本用例应标记为 `FAIL`。缺少自动补偿扫描机制，不能满足定时激活 pending 工单的验收标准。
