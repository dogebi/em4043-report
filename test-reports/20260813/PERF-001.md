# PERF-001 页面加载时间 P95 < 2 秒

| 项目 | 内容 |
| --- | --- |
| 当前状态 | FAIL |
| 执行时间 | 2026-08-13 14:42:36 至 15:12:46 +08:00 |
| 目标 URL | https://csc-ai.natec.cn/work-agent/#/project/4/process/task/20 |
| 执行方式 | 20 并发 HTTP 用户，持续 1800 秒，重复 GET 页面入口 URL |
| 需求依据 | 20 并发用户持续访问 30 分钟，页面加载 P95 < 2 秒 |
| 实际结果 | 总请求 3280，HTTP 200 为 136，错误 3144，错误率 95.8537%，P95 11385.88 ms |
| 结论 | 未满足 P95 < 2 秒，也未满足稳定访问要求。 |

## 指标

| 指标 | 值 |
| --- | ---: |
| 并发数 | 20 |
| 计划持续时间 | 1800 秒 |
| 实际持续时间 | 1810.49 秒 |
| 总请求数 | 3280 |
| HTTP 200 | 136 |
| 错误数 | 3144 |
| 错误率 | 95.8537% |
| RPS | 1.812 |
| 最小响应时间 | 3046.63 ms |
| 平均响应时间 | 11018.42 ms |
| P50 | 11183.36 ms |
| P95 | 11385.88 ms |
| P99 | 11905.62 ms |
| 最大响应时间 | 31818.69 ms |

## 错误分布

| Count | Status / Error |
| ---: | --- |
| 3128 | URLError: SSL UNEXPECTED_EOF_WHILE_READING |
| 16 | RemoteDisconnected: Remote end closed connection without response |
| 136 | HTTP 200 |

## 证据文件

- `test-evidence/20260813/PERF-001-http-load.csv`
- `test-evidence/20260813/PERF-001-summary.txt`
- `run_perf_001_http_load.py`

## 范围说明

本轮按用户指定 URL 做 HTTP 入口访问压测。该 URL 的 hash 片段不会发送到服务器，因此本轮测量的是 `/work-agent/` 页面壳 HTTP 响应，不是浏览器内路由渲染完成时间或真实用户 RUM 页面加载时间。
