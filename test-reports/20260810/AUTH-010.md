# AUTH-010 权限变更同步验证测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-010 |
| 测试标题 | 权限变更同步验证 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 权限缓存机制具备30分钟主缓存、Jira重新查询、stale降级和手动刷新能力，但本轮未实际在Jira移除用户项目权限并等待30分钟，因此只能判定代码级部分通过，不能判定端到端通过。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 12 定义 `AUTH-010` 要求缓存过期前仍可访问，30分钟后重新查询Jira，权限变更后不可访问项目Y。 |
| 检查主缓存TTL | PASS | `config/ai_work.php` 默认 `cache_ttl=1800`，即30分钟。 |
| 检查缓存命中行为 | PASS | `ProjectAccessCacheService::getAccessibleProjects()` 主缓存存在时直接返回，并在TTL低于阈值时后台刷新。 |
| 检查缓存过期后重新查询Jira | PASS | 缓存未命中且获得 `refresh_lock` 后调用 `fetchAccessibleProjects()`，其中调用 `JiraProjectAccessService::getAccessibleProjects()`。 |
| 检查手动刷新/重建缓存 | PASS | `refreshUser()` 删除主缓存和stale后重新计算并写入主缓存与stale。 |
| 实际Jira权限移除验证 | NOT RUN | 本轮未对Jira执行移除用户A项目Y权限操作，也未等待30分钟。 |
| 权限变更后不可访问项目Y | NOT RUN | 缺少实际变更后的ProjectY ID/key和等待窗口，无法端到端验证。 |

## 技术检查记录

```text
config ai_work.permission_cache.cache_ttl = 1800 seconds.
config ai_work.permission_cache.stale_ttl = 604800 seconds.
config ai_work.permission_cache.lock_ttl = 10 seconds.
ProjectAccessCacheService cache miss path calls JiraProjectAccessService.
refreshUser deletes main/stale cache and rebuilds both.
```

## 关键代码位置

- `D:\dev\cscAI\esm\config\ai_work.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectAccessService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Controllers\Admin\ProjectAccessCacheController.php`

## 当前结论

本用例应标记为 `PARTIAL`。代码机制与用例预期基本一致，但端到端验收需要实际Jira权限变更、等待或强制过期缓存、再访问ProjectY的证据。
