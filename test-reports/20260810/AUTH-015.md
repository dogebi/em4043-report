# AUTH-015 管理端功能权限控制测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-015 |
| 测试标题 | 管理端功能权限控制 |
| 执行日期 | 2026-08-10 |
| 当前状态 | PARTIAL |
| 结论 | 成员管理页面存在按钮级和接口级权限判断，但未验证到未授权接口返回 HTTP 403，也未确认未授权尝试被单独审计记录。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 14 定义 `AUTH-015` 要求菜单、按钮、接口权限一致控制，未授权用户不可见按钮，直接请求 API 返回 403，并记录审计日志。 |
| 检查菜单/页面入口权限 | PASS | `AdminUserController::index()` 在缺少 `member_view` 和 `department_view` 时返回 `not_permission`。 |
| 检查按钮级权限 | PASS | 新增、编辑、启停、初始化密码、删除按钮均通过 `userCan()` 控制可见性。 |
| 检查接口级权限 | PASS | `store()`、`update()` 中按 `member_create`、`member_edit`、`member_enable_disable`、`member_init_pass` 判断权限。 |
| 验证直接 API 返回 HTTP 403 | FAIL | 当前代码证据为 `response()->fail($this->trans('not_permission'))`，未看到显式 HTTP 403 状态设置。 |
| 验证未授权尝试审计日志 | NOT RUN | `OperationLog` 中间件会记录后台访问/操作日志，但本轮未用低权限账号执行未授权请求验证。 |

## 技术检查记录

```text
AdminUserController permissions:
- member_view
- member_create
- member_edit
- member_enable_disable
- member_init_pass
- member_delete
- department_view

Authorization failure:
return $this->response()->fail($this->trans('not_permission'));
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\Admin\Controllers\System\AdminUserController.php`
- `D:\dev\cscAI\esm\app\Admin\Middleware\OperationLog.php`

## 当前结论

本用例应标记为 `PARTIAL`。前端按钮和后端业务权限控制已覆盖主要操作，但缺少 HTTP 403 和未授权审计的端到端证据。
