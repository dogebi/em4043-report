# AUTH-011 权限缓存命中（TTL>5min）测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-011 |
| 测试标题 | 权限缓存命中（TTL>5min） |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码实现了Redis主缓存命中直接返回和TTL低于5分钟才后台刷新的机制，但本轮未直接读取Redis TTL或统计Jira API调用次数，响应时间<50ms也未在服务内网环境完成测量。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 13 定义 `AUTH-011` 要求TTL>5min时从Redis主缓存返回，不触发Jira API，响应时间<50ms。 |
| 检查主缓存读取 | PASS | `ProjectAccessCacheService::getAccessibleProjects()` 先读取 `mainKey(userId)` 的Redis HASH。 |
| 检查命中后直接返回 | PASS | `cached['projects']` 存在时直接 `json_decode` 返回项目列表。 |
| 检查TTL>5min不刷新 | PASS | 仅当 `ttl < prefreshThreshold` 时调用 `backgroundRefresh()`；默认 `prefreshThreshold=300` 秒。 |
| 检查不触发Jira API | PARTIAL | 代码命中主缓存后在返回前不会进入 `fetchAccessibleProjects()`，但本轮未做Jira调用计数或日志验证。 |
| 检查响应时间<50ms | NOT RUN | 未在服务内网或本机Redis环境执行性能计时。远程HTTP网络耗时不能代表缓存命中服务内耗时。 |

## 技术检查记录

```text
main cache key: ai_work_perm:user:{uid}:projects.
cache hit branch returns cached projects before fetchAccessibleProjects().
prefresh threshold default: 300 seconds.
cache ttl default: 1800 seconds.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\config\ai_work.php`

## 当前结论

本用例应标记为 `PARTIAL`。代码机制满足缓存命中路径，但缺少Redis TTL现场证据、Jira调用计数证据和<50ms性能证据。
