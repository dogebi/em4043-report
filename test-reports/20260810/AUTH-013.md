# AUTH-013 Jira不可用时stale降级测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-013 |
| 测试标题 | Jira不可用时stale降级 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 代码具备stale降级函数，但Jira不可用在 `fetchAccessibleProjects()` 内部被捕获后直接降级为本地成员镜像，通常不会进入用例要求的“Jira失败后使用Redis stale备份”路径。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 13 定义 `AUTH-013` 要求主缓存未命中、Jira调用失败、使用stale 7天缓存、主缓存TTL缩至5分钟并正常返回权限数据。 |
| 检查stale备份存在机制 | PASS | `writeStale()` 写入 `staleKey(userId)` 并设置 `stale_ttl=604800` 秒。 |
| 检查stale降级函数 | PASS | `tryDegrade()` 命中stale后用 `DEGRADED_TTL=300` 写回主缓存。 |
| 检查Jira不可用触发stale | FAIL | `fetchAccessibleProjects()` 捕获 `JiraProjectAccessService` 异常后设置 source 为 `MEMBER_MIRROR_DEGRADED` 并返回本地成员镜像，不向上抛出，外层通常不会调用 `tryDegrade()`。 |
| 检查用户正常获取权限数据 | PARTIAL | 如果本地成员镜像存在，用户可获得权限数据；但这不是用例要求的stale优先降级。 |
| 实际停止Jira复测 | NOT RUN | 本轮未停止Jira服务。 |

## 技术检查记录

```text
stale_ttl default: 604800 seconds.
DEGRADED_TTL: 300 seconds.
Jira exception inside fetchAccessibleProjects is caught and converted to member mirror degraded source.
tryDegrade uses stale only when fetchAccessibleProjects throws or lock contention fallback reaches degrade.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\config\ai_work.php`

## 当前结论

本用例应标记为 `FAIL`。实现有stale能力，但Jira不可用的主路径与验收标准要求的stale降级链不一致。
