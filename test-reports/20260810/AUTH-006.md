# AUTH-006 工单/资产数据权限镜像验证测试报告
## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-006 |
| 测试标题 | 工单/资产数据权限镜像验证 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 当前实现具备 Jira 权限镜像、用户级 OAuth Token 透传和无权限提示能力，但对无权限项目的处理是 HTTP 403 拒绝，而不是用例要求的“返回空结果”。 |

## 测试步骤与结果
| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 11 定义 `AUTH-006` 为用户A仅有项目X权限时，请求项目X正常返回，请求项目Y返回空结果并提示“无权限访问该项目”，且透传 OAuth Token 到 Jira API。 |
| 检查权限镜像是否按用户可见 Jira 项目构建 | PASS | `JiraProjectAccessService::getAccessibleProjects()` 使用用户自己的 `jira_access_token` 调 `/rest/api/2/project` 获取可见项目，再与本地已引入 Jira 项目按 `remote_project_key` 取交集。 |
| 检查项目X数据访问是否存在放行路径 | PASS | `ProjectAccessMiddleware` 和 `GuardsProjectAccessTrait` 通过 `hasProjectAccessByKey/Id()` 判断；`IssueService`、`IssueListService` 在有权限时继续查询项目工单数据。 |
| 检查项目Y无权限时是否返回空结果 | FAIL | `ProjectAccessMiddleware::deny()` 明确返回 HTTP 403，`IssueService`/`IssueListService` 在调用 `guardProjectAccess()` 失败时也是拒绝访问，不是返回空列表。 |
| 检查是否提示“无权限访问该项目” | PASS | `ProjectAccessMiddleware::deny()` 返回 `message => '无权限访问该项目'`，并带详细说明。 |
| 检查是否透传 OAuth Token 到 Jira API | PASS | `JiraAuthService::getAccessToken()` 从用户 `extends` 取 `jira_access_token`；`JiraProjectAccessService` 用该 token 构造 `new JiraClient(token: $token)` 访问 Jira；`JiraClient` 默认发送 `Authorization: Bearer <user token>`。 |

## 预期结果对照

- 项目X数据正常返回，具备实现路径。
- 项目Y返回空结果，未满足，当前实现为 HTTP 403 拒绝。
- 提示“无权限访问该项目”，已实现。
- 透传 OAuth Token 到 Jira API，已实现。

## 技术检查记录
```text
ProjectAccessMiddleware checks project_key/project_id and denies unauthorized access with HTTP 403.
ProjectAccessCacheService builds accessible projects from local member mirror plus Jira authority supplement.
JiraProjectAccessService fetches visible Jira projects with the user's own access token.
IssueService and IssueListService call guardProjectAccess(projectId) before returning issue data.
```

## 2026-08-10 Manual Bearer Token Retest

| Retest Item | Result | Evidence |
|---|---|---|
| Provided Bearer JWT identity | PASS | Payload identifies `sub=184` and `app_id=WORKYtXC7mVE`; token time window is currently valid. |
| Work API project list with provided token | PASS | `GET http://csc-ai.natec.cn/agent-work-api/v1/projects` returned HTTP 200 and included accessible Jira project `id=3`, `remote_project_key=EM4043`. |
| Project X issue data request | PASS | `GET http://csc-ai.natec.cn/agent-work-api/v1/projects/3/issues` returned HTTP 200, `code=0`, `item_count=14`. |
| Project X / Project Y live contrast | BLOCKED | Exact Project X and Project Y identifiers were not provided, so a real authorized-vs-unauthorized data comparison cannot be executed safely. |
| Unauthorized project response standard | FAIL | Code path still returns HTTP 403 via `ProjectAccessMiddleware::deny()` / `guardProjectAccess()` instead of the required empty result. |

Manual token retest does not change the AUTH-006 status. The token authenticates successfully and Project X-like data returns normally, but the implementation still rejects unauthorized projects with HTTP 403 rather than returning an empty result.

## 关键代码位置

- `D:\dev\cscAI\esm\app\AppAgent\Middleware\ProjectAccessMiddleware.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\ProjectAccessCacheService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraProjectAccessService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraAuthService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Clients\JiraClient.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Services\AiWork\IssueListService.php`

## 当前结论

本用例应标记为 `FAIL`。当前系统的权限镜像方向是对的，但验收标准要求“项目Y返回空结果”，而实际实现统一返回 HTTP 403 拒绝访问。
