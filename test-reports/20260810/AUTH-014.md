# AUTH-014 Redis不可用时直连Jira降级测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-014 |
| 测试标题 | Redis不可用时直连Jira降级 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码实现了Redis读取失败后跳过缓存并实时查询Jira的降级路径，但本轮未停止Redis服务做端到端验证，也未测量响应时间变化。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 13 定义 `AUTH-014` 要求Redis连接失败时降级为直连Jira API查询，正常返回权限数据，响应时间增加但功能正常。 |
| 检查Redis失败捕获 | PASS | `getAccessibleProjects()` 读取Redis主缓存异常时直接调用 `resolveWithoutCache()`。 |
| 检查直连Jira路径 | PASS | `resolveWithoutCache()` 优先调用 `fetchAccessibleProjects()`，其中使用 `JiraProjectAccessService::getAccessibleProjects()`。 |
| 检查最终降级兜底 | PASS | Jira或本地查询失败时可退到本地成员镜像；全部不可用时抛 `ProjectAccessException`。 |
| 实际Redis停止复测 | NOT RUN | 本轮未停止Redis服务。 |
| 响应时间增加但功能正常 | NOT RUN | 未执行Redis故障条件下的延迟测量。 |

## 技术检查记录

```text
Redis hgetall exception -> resolveWithoutCache().
resolveWithoutCache() -> fetchAccessibleProjects() -> JiraProjectAccessService.
Fallback after Jira failure -> member mirror -> ProjectAccessException if all unavailable.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectAccessService.php`

## 当前结论

本用例应标记为 `PARTIAL`。代码路径符合预期，但缺少真实Redis不可用场景和响应时间证据。
