# AUTH-001 Jira SSO  login测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-001 |
| 测试标题 | 用户端 Jira SSO 正常登录 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | ESM 回调、用户首页、appinfo 和项目列表已确认；Access Token/JWT 的敏感值检查及 Redis 权限缓存仍未完整确认 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 访问用户端 `/login` 页面 | PASS | 浏览器加载 ESM 用户端登录页面 |
| 手动完成 Jira/SSO 登录 | PASS | 由测试人员在浏览器中完成，未自动输入凭据 |
| OAuth 回调返回 ESM | PASS | 浏览器地址切换到 `csc-ai.natec.cn/work-agent/...`，随后加载用户端页面；完整会话标识未记录 |
| ESM Access Token/JWT 签发 | PARTIAL | 登录后的页面能够访问受保护用户端；未读取、保存或输出 Token 明文，Token 的有效期字段尚未单独取证 |
| 跳转用户首页 | PASS | 首页显示用户区域、项目一览、活跃项目和项目卡片 |
| Redis 权限缓存创建 | NOT VERIFIED | 当前本地 Redis Ping 成功，但 `ai_work_perm:user:*:projects` 匹配键数量为 0 |
| Redis TTL | NOT VERIFIED | 因本地没有权限缓存键，无法读取有效 TTL |
| appinfo API | PASS | `GET https://csc-ai.natec.cn/agent-work-api/v1/appinfo`，带前端 `hubid` 请求，HTTP 200，响应 `code=0`，返回 `no/name/config` 等字段 |
| 项目 API/页面 | PASS（浏览器） | 首页显示项目列表，包括 `AI运维测试` 等项目；脱离浏览器会话直接调用项目 API 返回未授权 HTML，符合需要登录态的路由保护 |

## 预期结果对照

- Jira/SSO 登录后回调 ESM：已确认。
- 用户端首页：已确认。
- `appinfo`：已确认 HTTP 200、`code=0` 和核心配置字段。
- 项目列表：已通过登录后的浏览器页面确认。
- Access Token/JWT 8 小时、Refresh Token 30 天：未读取明文，当前只能确认登录态已被用户端使用，不能确认具体过期时间。
- Redis 权限缓存 30 分钟 TTL：未确认。当前本地 Redis 中没有 `ai_work_perm:user:*:projects` 键。

## 技术检查记录

```text
PHP CLI: 8.2.31
PHP redis extension: loaded
Redis TCP 127.0.0.1:6379: reachable
Redis ping: 1
Permission cache keys: 0
```

代码定义的主缓存键格式为：

```text
ai_work_perm:user:{user_id}:projects
```

代码定义的主缓存 TTL 默认值为 1800 秒，stale 缓存默认值为 604800 秒。

## 证据

- [Jira 手动认证截图](../../test-evidence/20260810/AUTH-001-01-jira-reauth.png)
- [ESM 用户首页和项目列表截图](../../test-evidence/20260810/AUTH-001-02-esm-home-projects.png)

## 当前结论

本用例不能标记为 PASS。已确认 ESM 登录后的回调、用户首页、appinfo 和项目页面；Redis 权限缓存/TTL 以及 Token/JWT 过期时间仍需要在与当前用户会话对应的 ESM 运行环境中补充验证。

## 安全规则

- 密码、OAuth 凭据、Cookie、Access Token 和 Refresh Token 必须由测试人员手动输入或确认。
- 报告、脚本和截图不得保存或输出上述敏感值。
- 自动化只检查跳转、HTTP 状态、非敏感响应字段、Redis 键存在性和 TTL。
