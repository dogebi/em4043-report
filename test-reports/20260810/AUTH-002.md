# AUTH-002 浏览器插件 Jira 登录态自动提取测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-002 |
| 测试标题 | 浏览器插件 Jira 登录态自动提取 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | ESM 服务端已具备 Jira Session Cookie 校验和 SSO 签发路径，但当前浏览器插件缺少读取 Jira Cookie 的权限和实现，无法完成自动提取登录态 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 11 定义了 `AUTH-002` 需要插件自动读取 Jira Session Cookie、服务端校验并签发 JWT |
| 检查插件权限声明 | FAIL | `ai-assistant-browser-plugin/manifest.json` 仅声明 `scripting/tabs/activeTab/sidePanel/storage`，没有 `cookies` 权限 |
| 检查插件代码是否提取 Jira 会话 | FAIL | 插件源码中未发现 `session_cookie`、`jira_session`、`chrome.cookies`、`JSESSIONID`、`atlassian.xsrf` 等实现 |
| 检查服务端是否支持 Jira Session 登录 | PASS | ESM 侧存在 `verifySessionCookie()`、`getMyselfBySessionCookie()`、`exchangeBySessionCookie()` 和 `jira_session` SSO adapter 路径 |
| 综合判定是否可达到“插件自动登录”预期 | FAIL | 由于插件侧第一步无法执行，后续“服务端验证 Session”“签发系统 JWT”“插件显示已登录状态”均无法由当前实现触发 |

## 预期结果对照

- 插件 Content Script 读取 Jira Session Cookie：未实现。
- 服务端验证 Session 有效：服务端代码已具备能力，但当前插件未传入 Cookie，未实际触发。
- 签发系统 JWT：服务端代码已具备能力，但当前插件未触发该链路。
- 插件显示已登录状态：当前插件仅提供 AI 助手注入与侧边栏能力，未见登录态 UI。
- 无需跳转 OAuth 页面：无法验证，因为插件未进入自动提取流程。

## 技术检查记录

```text
Plugin manifest permissions: scripting, tabs, activeTab, sidePanel, storage
Plugin manifest host_permissions: <all_urls>
Plugin code search hits for cookie/session extraction: 0
Server code has Jira session auth path: verifySessionCookie + getMyselfBySessionCookie + jira_session adapter + exchangeBySessionCookie
```

## 2026-08-10 Manual Cookie / Bearer Token Retest

| Retest Item | Result | Evidence |
|---|---|---|
| Jira Session Cookie validity | PASS | Manual cookie request to Jira `/rest/api/2/myself` returned HTTP 200 and `X-Seraph-LoginReason: OK`. |
| Cookie-to-ESM JWT exchange | FAIL | Local `JiraPluginAuthService::loginByCookie()` call failed with `ServiceException: 未配置插件 SSO app（CSC_JIRA_PLUGIN_SSO_APP_ID / DEFAULT_AI_HUB_SSO_APPID）`. |
| Provided Bearer JWT validity | PASS | Token payload is currently within `iat=2026-08-10 16:14:38 +08:00` and `exp=2026-08-17 16:14:38 +08:00`; `app_id=WORKYtXC7mVE`, `sub=184`. |
| Browser plugin auto-login state | FAIL | Plugin still has no `cookies` permission and no `chrome.cookies` / Jira session extraction implementation. |

Manual token/cookie retest does not change the AUTH-002 status. Jira login state is valid, but the implemented browser-plugin flow still cannot automatically read Jira Cookie, call the backend exchange, receive the system JWT, and render logged-in state without OAuth navigation.

## 关键代码位置

- `D:\dev\cscAI\ai-assistant-browser-plugin\manifest.json`
- `D:\dev\cscAI\ai-assistant-browser-plugin\background.js`
- `D:\dev\cscAI\ai-assistant-browser-plugin\content.js`
- `D:\dev\cscAI\ai-assistant-browser-plugin\popup.js`
- `D:\dev\cscAI\esm\app\SSOAdapters\Contracts\AdapterSocialiteJiraPlugin.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraAuthService.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Clients\JiraClient.php`
- `D:\dev\cscAI\esm\app\AppAgent\Integrations\Csc\Services\JiraSessionTokenService.php`

## 当前结论

本用例应标记为 `FAIL`，不是 `BLOCKED`。原因不是环境缺失，而是当前浏览器插件实现本身不满足需求定义的首个必要条件，即“自动提取 Jira 登录态”。服务端支持路径已存在，但插件未声明 `cookies` 权限，也未实现任何 Jira Session Cookie 读取和上传逻辑。
