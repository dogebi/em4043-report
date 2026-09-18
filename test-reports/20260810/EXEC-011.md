# EXEC-011 子 Agent 超时 300 秒测试报告

| 项目 | 内容 |
|---|---|
| 用例编号 | EXEC-011 |
| 测试标题 | 子Agent超时（300秒） |
| 执行日期 | 2026-08-10 |
| 当前状态 | FAIL |
| 结论 | Sub-Agent 超时机制存在，但实际使用 `AGENT_TASK_TIMEOUT=100` 秒，返回状态为 `timeout`，不是用例要求的 300 秒和 `partial_done`。 |

## 证据

- `Executor` 使用 `asyncio.wait_for(..., timeout=_SUB_AGENT_TIMEOUT)`。
- `app/config.py` 中 `AGENT_TASK_TIMEOUT=100`。
- 超时输出为 `status="timeout"`。

## 未满足项

- 超时时间不是 300 秒。
- 未返回 `partial_done`。
- 未发现指定提示文案和重新执行入口。
