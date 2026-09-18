# AUTH-005 Access Token过期处理测试报告
## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-005 |
| 测试标题 | Access Token过期处理 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 当前实现存在登录有效期控制，但默认有效期不是 8 小时；过期时主中间件返回的是业务码 JSON 而非 HTTP 401；也未找到通用前端“清除本地 token 并跳转登录页”的完整闭环。 |

## 测试步骤与结果
| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 11 定义 `AUTH-005` 为 Access Token 过期处理，要求 8 小时到期后请求返回 HTTP 401，并由前端清 token、跳转登录页、提示重新登录。 |
| 检查系统是否有登录有效期控制 | PASS | `app/Http/Middleware/ApiAuthenticate.php` 根据 `app_login_validity_rule` 与 `app_login_validity_ttl` 判定登录过期。 |
| 检查默认有效期是否为 8 小时 | FAIL | `app/Models/Config.php` 默认 `app_login_validity_ttl` 为 `7 * 24 * 60` 分钟，即 7 天；`config/jwt.php` 的 `ttl` 还是 3 个月。 |
| 检查过期后是否返回 HTTP 401 | FAIL | `ApiAuthenticate.php` 在 token 失效、登录过期等分支均使用 `response()->json([...])`，未显式设置 401 状态码。 |
| 检查前端是否通用清理本地 token 并跳转登录 | FAIL | 已发现 `workflow-editor.blade.php` 仅对特定页面定义 `WORKFLOW_EDITOR_TOKEN_EXPIRED_CALLBACK`，其行为是跳 `#/login` 并 toast；未发现通用 App 前端统一清 token 与登录跳转闭环。 |

## 预期结果对照

- 8 小时后 Access Token 过期，未满足，当前默认有效期为 7 天，JWT 配置为 3 个月。
- API 返回 HTTP 401，未满足，当前主中间件返回业务 JSON。
- 前端清除本地 token，未找到通用实现证据。
- 前端跳转登录页，未找到通用实现证据。
- 提示“登录已过期，请重新登录”，仅在局部页面可见相近处理，不构成整体验收通过。

## 技术检查记录
```text
ApiAuthenticate enforces login validity using global_config(app_login_validity_ttl/app_login_validity_rule).
Expired login branch returns JSON with AUTH_FAILURE code and message, but no explicit HTTP 401.
Default app_login_validity_ttl in Config model is 7 days.
JWT ttl in config/jwt.php is 3 months.
workflow-editor view reads localStorage token and defines a token-expired callback, but this is page-specific.
```

## 2026-08-10 Manual Bearer Token Retest

| Retest Item | Result | Evidence |
|---|---|---|
| Provided Bearer JWT is currently usable by time window | PASS | Payload window is `iat=2026-08-10 16:14:38 +08:00` to `exp=2026-08-17 16:14:38 +08:00`. |
| Token lifetime matches 8-hour standard | FAIL | The provided token lifetime is 7 days, not 8 hours. |

Manual token retest strengthens the existing AUTH-005 failure conclusion. The token is valid now, but its actual TTL does not satisfy the case standard requiring 8-hour expiration handling.

## 关键代码位置

- `D:\dev\cscAI\esm\app\Http\Middleware\ApiAuthenticate.php`
- `D:\dev\cscAI\esm\app\Models\Config.php`
- `D:\dev\cscAI\esm\config\jwt.php`
- `D:\dev\cscAI\esm\app\AppAgent\Views\workflow-editor.blade.php`

## 当前结论

本用例应标记为 `FAIL`。当前系统具备“登录有效期”概念，但与用例要求的 8 小时、HTTP 401、前端统一清 token 和重新登录引导不一致。
