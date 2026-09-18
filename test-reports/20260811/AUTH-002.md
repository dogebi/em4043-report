# AUTH-002 Jira 登录态自动检测复测报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-002 |
| 执行日期 | 2026-08-11 |
| 当前状态 | FAIL |
| 判定 | Cookie 读取、服务端 Session 验证和 JWT 签发链路已存在，但未实现“点击插件图标后自动检测”及“显示已登录状态”。 |

## 验证结果

| 验证标准 | 结果 | 证据 |
|---|---|---|
| Content Script 读取 Jira Session Cookie | PARTIAL | `manifest.json:11` 已声明 `cookies`；`popup.js:47-65` 通过 `chrome.cookies.getAll` 读取当前 Jira Cookie，但实现位于 Popup，不是 Content Script。 |
| 服务端验证 Session 有效 | PASS（代码路径） | `AdapterSocialiteJiraPlugin.php:57-62` 调用 `JiraAuthService::verifySessionCookie()`；`JiraClient.php:276-280` 使用 Cookie 请求 Jira `/rest/api/2/myself`。 |
| 签发系统 JWT | PASS（代码路径） | `JiraPluginAuthService.php:175-185` 明确签发并返回 JWT。 |
| 插件显示已登录状态 | FAIL | `popup.js:96-104` 仅保存 token 并弹出成功提示，没有登录状态展示或状态读取 UI。 |
| 无需跳转 OAuth 页面 | PARTIAL | Popup 调用 `/sso/login`，不主动导航浏览器；服务端 Jira Session 分支仍可能执行后台 OAuth token exchange。 |
| 点击插件图标后自动检测 | FAIL | `popup.js:179-187` 只有点击 `jira-login` 按钮时才执行 `collectJiraSession()`。 |

## 已执行检查

```text
node --check D:\dev\cscAI\ai-assistant-browser-plugin\popup.js       PASS
php -l JiraPluginAuthService.php                                      PASS
php -l JiraAuthService.php                                             PASS
php -l JiraClient.php                                                   PASS
php -l AdapterSocialiteJiraPlugin.php                                  PASS
```

## 结论

本次复测不能标记为 PASS。现有代码已覆盖 Cookie → Session 校验 → SSO JWT 的主要技术链路，但 AUTH-002 要求的入口行为仍不满足：打开插件 Popup 后必须自动检测，并显示已登录状态。
