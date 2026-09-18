# AUTH-016 审计日志只读权限测试报告

## 基本信息

| 项目 | 内容 |
|---|---|
| 用例编号 | AUTH-016 |
| 测试标题 | 审计日志只读权限 |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | 日志页面具备查询和导出能力，但路由使用 resource 注册且控制器继承通用 `destroy()`，未证明删除 API 被禁止。 |

## 测试步骤与结果

| 步骤 | 结果 | 证据 |
|---|---|---|
| 确认用例预期 | PASS | `docx` TABLE 14 定义 `AUTH-016` 要求审计日志只读，仅允许查询/导出，禁止修改和删除。 |
| 检查日志查询页面 | PASS | `AdminOperationLogController::index()` 返回列表或导出结果。 |
| 检查导出能力 | PASS | `_action=export` 会调用通用 `Export::export()`，默认生成 `.xlsx` 文件。 |
| 检查 UI 删除入口 | PASS | `operateLogListSchema()` 未配置行删除按钮或批量删除按钮。 |
| 检查删除 API 是否被禁止 | FAIL | `routes.php` 使用 `$router->resource('log_system', AdminLog::class)`，父类 `AdminController::destroy($ids)` 会调用 `$this->repository->delete($ids)`。 |
| 检查日志不可修改 | FAIL | 未看到 `AdminOperationLogController` 覆盖 `store/update/destroy` 来显式禁止写操作。 |

## 技术检查记录

```text
app/Admin/routes.php:
$router->resource('log_system', AdminLog::class);

vendor/wangji/amis-admin/src/Controllers/AdminController.php:
public function destroy($ids): JsonResponse
{
    $rows = $this->repository->delete($ids);
    return $this->autoResponse($rows, admin_trans('admin.delete'));
}
```

## 关键代码位置

- `D:\dev\cscAI\esm\app\Admin\Controllers\AdminOperationLogController.php`
- `D:\dev\cscAI\esm\app\Admin\Repositories\AdminOperationLogRepository.php`
- `D:\dev\cscAI\esm\app\Admin\routes.php`
- `D:\dev\cscAI\esm\vendor\wangji\amis-admin\src\Controllers\AdminController.php`
- `D:\dev\cscAI\esm\vendor\wangji\amis-admin\src\Traits\Export.php`

## 当前结论

本用例应标记为 `FAIL`。UI 层没有删除按钮不足以满足只读要求，必须确认后端删除/修改接口不可用或返回 403。
