# AUTH-003 插件端 Jira 退出登录联动失效测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-003 |
| 测试标题 | 插件端 Jira 退出登录联动失效 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 当前浏览器插件未实现 Jira 登录态持久化、失效检测、本地 JWT 清理和重新登录提示，因此无法满足退出登录联动要求 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 11 定义了 `AUTH-003` 需要在 Jira Web 退出后联动插件回到未登录状态 |
| 检查插件是否存在已登录状态管理 | FAIL | 插件源码仅见 `aiAssistantConfig` 配置存储，未见 Jira 登录状态或用户会话状态存储 |
| 检查插件是否检测 Jira Session 失效 | FAIL | 未发现 `chrome.cookies`、Cookie 轮询、失效回调、401 监听或 Jira Session 失效检测实现 |
| 检查插件是否清除本地 JWT | FAIL | 未发现本地 JWT 保存、刷新、清除逻辑，也未见退出后 token 删除代码 |
| 检查插件是否回到未登录状态并提示重登 | FAIL | 当前插件 UI 仅提供侧边栏/悬浮入口和 AI 助手配置，未见登录态展示或重登提示界面 |

## 预期结果对照

- 插件检测到 Jira Session 失效：未实现。
- 插件立即清除本地 JWT：未实现。
- 插件回到未登录状态：未实现。
- 提示用户重新登录 Jira：未实现。

## 技术检查记录

```text
Plugin code search hits for logout/session invalidation handling: no Jira-specific implementation found
Plugin code search hits for local JWT storage/clear flow: no Jira-specific implementation found
Plugin persistent storage usage found: aiAssistantConfig only
AUTH-003 prerequisite "plugin already logged in" is not supported by current plugin implementation
```

## 关键代码位置

- `D:\dev\cscAI\ai-assistant-browser-plugin\manifest.json`
- `D:\dev\cscAI\ai-assistant-browser-plugin\background.js`
- `D:\dev\cscAI\ai-assistant-browser-plugin\content.js`
- `D:\dev\cscAI\ai-assistant-browser-plugin\popup.js`
- `D:\dev\cscAI\ai-assistant-browser-plugin\ai.assistant.js`

## 当前结论

本用例应标记为 `FAIL`。当前问题不是单纯缺少现场操作，而是浏览器插件本身尚未具备 Jira 登录态管理能力，因此既无法形成“插件已登录”的前置状态，也无法在 Jira Web 退出后执行会话失效联动。
