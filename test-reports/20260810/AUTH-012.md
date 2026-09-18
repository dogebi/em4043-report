# AUTH-012 缓存过期后Jira重新查询测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-012 |
| 测试标题 | 缓存过期后Jira重新查询 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 代码实现了主缓存未命中后获取10秒分布式锁、查询Jira、写入主缓存和stale备份、释放锁的流程，但本轮未清空/等待真实主缓存过期并观测Redis写入。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 13 定义 `AUTH-012` 要求主缓存过期后获取分布式锁，查询Jira，写入主缓存30min+stale7天+MySQL，释放锁并返回数据。 |
| 检查分布式锁 | PASS | `acquireLock()` 使用 `Redis::set(lockKey, '1', 'EX', lockTtl, 'NX')`，默认 `lock_ttl=10` 秒。 |
| 检查Jira重新查询 | PASS | 缓存未命中且获得锁后调用 `fetchAccessibleProjects()`，内部调用 `JiraProjectAccessService::getAccessibleProjects()`。 |
| 检查写入主缓存 | PASS | `writeCache()` 写入 `projects/role/cached_at/source/version` 并设置主缓存TTL。 |
| 检查写入stale备份 | PASS | `writeStale()` 写入stale HASH并设置默认7天TTL。 |
| 检查释放锁 | PASS | `finally` 分支调用 `releaseLock()` 删除锁。 |
| 检查MySQL持久化 | FAIL | 当前实现注释明确“不实现 user_permissions_cache DB 表”，未发现按用例要求写入MySQL权限缓存表。 |
| 实际缓存过期复测 | NOT RUN | 本轮未等待30分钟或手动删除Redis key后复测。 |

## 技术检查记录

```text
cache_ttl default: 1800 seconds.
stale_ttl default: 604800 seconds.
lock_ttl default: 10 seconds.
ProjectAccessCacheService comment says user_permissions_cache DB table is not implemented.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\config\ai_work.php`

## 当前结论

本用例应标记为 `PARTIAL`。缓存刷新主流程存在，但MySQL权限缓存落库缺失，且缺少真实过期后的运行证据。
