# 性能测试 PERF-001 的 HTTP 并发访问脚本
import argparse
import csv
import statistics
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone


def percentile(values, pct):
    if not values:
        return None
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) * pct + 99) // 100) - 1))
    return ordered[index]


def worker(worker_id, url, deadline, timeout, rows, lock):
    request_id = 0
    while time.monotonic() < deadline:
        request_id += 1
        started = time.perf_counter()
        status = "error"
        size = 0
        error = ""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "PERF-001-http-load/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read()
                status = str(response.status)
                size = len(body)
        except urllib.error.HTTPError as exc:
            status = str(exc.code)
            error = str(exc)
        except Exception as exc:
            error = type(exc).__name__ + ": " + str(exc)
        elapsed_ms = (time.perf_counter() - started) * 1000
        with lock:
            rows.append([
                datetime.now(timezone.utc).isoformat(),
                worker_id,
                request_id,
                round(elapsed_ms, 2),
                status,
                size,
                error,
            ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--duration-seconds", type=int, default=1800)
    parser.add_argument("--timeout-seconds", type=int, default=30)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    rows = []
    lock = threading.Lock()
    deadline = time.monotonic() + args.duration_seconds
    started = time.time()
    threads = [
        threading.Thread(
            target=worker,
            args=(idx + 1, args.url, deadline, args.timeout_seconds, rows, lock),
            daemon=True,
        )
        for idx in range(args.concurrency)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    ended = time.time()

    with open(args.csv, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp_utc", "worker_id", "request_id", "elapsed_ms", "status", "bytes", "error"])
        writer.writerows(rows)

    latencies = [float(row[3]) for row in rows]
    ok = [row for row in rows if row[4] == "200"]
    errors = [row for row in rows if row[4] != "200" or row[6]]
    summary = {
        "url": args.url,
        "concurrency": args.concurrency,
        "duration_seconds_requested": args.duration_seconds,
        "duration_seconds_actual": round(ended - started, 2),
        "total_requests": len(rows),
        "http_200": len(ok),
        "errors": len(errors),
        "error_rate": round(len(errors) / len(rows), 6) if rows else None,
        "rps": round(len(rows) / (ended - started), 3) if ended > started else None,
        "min_ms": round(min(latencies), 2) if latencies else None,
        "avg_ms": round(statistics.fmean(latencies), 2) if latencies else None,
        "p50_ms": percentile(latencies, 50),
        "p95_ms": percentile(latencies, 95),
        "p99_ms": percentile(latencies, 99),
        "max_ms": round(max(latencies), 2) if latencies else None,
    }

    with open(args.summary, "w", encoding="utf-8") as handle:
        for key, value in summary.items():
            handle.write(f"{key}: {value}\n")

    print(summary)


if __name__ == "__main__":
    main()
