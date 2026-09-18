# AUTH-004 管理端独立账号登录测试报告
## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-004 |
| 测试标题 | 管理端独立账号登录 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 管理端存在账号密码登录、Token签发和审计日志能力，但未实现前端RSA加密传输，服务端也不是“解密后校验并签发JWT”的实现，和验收标准不一致。 |

## 测试步骤与结果
| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 11 定义 `AUTH-004` 为管理端独立账号登录，要求 RSA 加密传输、后端解密校验、签发系统 JWT、进入 Dashboard、记录审计日志。 |
| 检查登录页是否对密码做前端 RSA 加密 | FAIL | `app/Admin/Controllers/AuthController.php` 的 `loginPage()` 直接提交 `TextControl('password')->type('input-password')`，未发现 `JSEncrypt`、公钥下发或加密脚本。 |
| 检查服务端是否执行“解密后 bcrypt 校验” | FAIL | `app/Admin/Controllers/AuthController.php` 的 `login()` 直接使用 `Hash::check($request->password, $user->password)`，未发现私钥解密或密文解析流程。 |
| 检查是否签发系统 JWT | FAIL | `login()` 调用 `$user->createToken('admin')->plainTextToken`，`config/admin.php` 中 guard 为 `sanctum`，属于 Sanctum Token，不是 JWT。 |
| 检查登录成功后是否可进入管理端并记录日志 | PASS | `login()` 成功后返回 token；`createOperationLog('登录', $user)` 会写入操作日志；`config/admin.php` 已挂载 `App\Admin\Middleware\OperationLog`。 |

## 预期结果对照

- 前端 RSA 公钥加密密码传输，未实现。
- 后端解密后 bcrypt 校验，未实现。
- 签发系统 JWT，未实现，当前为 Sanctum Token。
- 登录后进入管理端 Dashboard，具备基础支持。
- 记录审计日志，已实现。

## 技术检查记录
```text
Admin login page submits username/password directly through amis form.
No RSA encryption script or public-key login flow found in admin auth controller.
Server verifies password with Hash::check(request password, stored bcrypt hash).
Token issued by createToken('admin')->plainTextToken under sanctum guard.
Operation log is written both by createOperationLog() and admin OperationLog middleware.
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\Admin\Controllers\AuthController.php`
- `D:\dev\cscAI\esm\config\admin.php`
- `D:\dev\cscAI\esm\app\Admin\Contracts\OperationLog.php`
- `D:\dev\cscAI\esm\app\Admin\Middleware\OperationLog.php`

## 当前结论

本用例应标记为 `FAIL`。当前实现可以完成管理端账号登录与日志记录，但与用例要求的 RSA 加密传输、后端解密流程和 JWT 签发标准不一致。
