# AUTH-017 操作审计日志查询与留存测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-017 |
| 测试标题 | 操作审计日志查询与留存 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 操作日志记录、敏感字段脱敏、多维查询和 Excel 导出存在，但未找到 180 天留存/分区清理实现，且未验证 CSV 导出。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 14 定义 `AUTH-017` 要求记录登录和操作日志，支持多维查询、导出 CSV，并至少保留 180 天。 |
| 检查日志写入 | PASS | `OperationLog::write()` 写入 `AdminOperationLog`，包含路径、方法、IP、请求参数、操作者和时间。 |
| 检查敏感字段处理 | PASS | `OperationLog::filterData()` 对 key 包含 `password` 和 `token` 的字段进行 `********` 脱敏。 |
| 检查多维查询 | PASS | `AdminOperationLogRepository::list()` 支持时间、操作者、路径、输入、方法、IP、关键词等筛选。 |
| 检查导出 | PARTIAL | 通用 `Export::export()` 可导出 `.xlsx`，但用例要求 CSV，本轮未找到 CSV 导出证据。 |
| 检查 180 天留存 | FAIL | `rg` 未发现针对 `admin_operation_logs` 的 180 天 retention、partition 或 cleanup 实现。 |

## 技术检查记录

```text
OperationLog fields:
- log_route_id
- description
- path
- method
- type
- ip
- input
- created_by
- created_at
- created_by_name

Sensitive masking:
- password -> ********
- token -> ********

Retention search:
No 180-day cleanup/partition rule found for admin_operation_logs.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\Admin\Middleware\OperationLog.php`
- `D:\dev\cscAI\esm\app\Admin\Repositories\AdminOperationLogRepository.php`
- `D:\dev\cscAI\esm\vendor\wangji\amis-admin\src\Traits\Export.php`

## 当前结论

本用例应标记为 `FAIL`。核心查询能力存在，但 180 天留存和 CSV 导出要求未满足或未被证明。
