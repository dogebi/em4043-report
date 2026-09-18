# CSC AI 대화창에 테스트 질문을 순서대로 전송하고 결과 보고서를 저장하는 자동화 스크립트
"""사용법:

    pip install playwright
    playwright install chromium
    python run_chat_cases.py --case-file ..\\..\\Testcase915.md --headed

최초 실행에서 브라우저가 열리면 로그인하고, 이후 같은 프로필을 재사용합니다.
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


DEFAULT_URL = "https://csc-ai.natec.cn/work-agent/yuN2YtXC7mVE?_slug=jira#/project/3/process"
EDITOR = 'div[contenteditable="true"][role="textbox"]'
QUESTION = re.compile(r"^\s*\**\s*###\s*Q\s*[:：]\s*(.+?)\s*\**\s*$")


def load_questions(path: Path) -> list[str]:
    questions = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = QUESTION.match(line)
        if match and match.group(1).strip():
            questions.append(match.group(1).strip())
    if not questions:
        raise ValueError(f"Q 항목을 찾지 못했습니다: {path}")
    return questions


async def visible_editor(page, timeout_ms: int):
    deadline = time.perf_counter() + timeout_ms / 1000
    editors = page.locator(EDITOR)
    while time.perf_counter() < deadline:
        for index in range(await editors.count()):
            editor = editors.nth(index)
            if await editor.is_visible():
                return editor
        await page.wait_for_timeout(200)
    raise TimeoutError("표시된 채팅 입력창을 찾지 못했습니다.")


async def send_and_collect(page, question: str, timeout_ms: int) -> tuple[str, float]:
    editor = await visible_editor(page, timeout_ms)
    before = await page.locator("body").inner_text()
    await editor.click()
    await page.keyboard.press("Control+A")
    await page.keyboard.press("Delete")
    started = time.perf_counter()
    await page.keyboard.insert_text(question)
    await page.keyboard.press("Enter")

    deadline = time.perf_counter() + timeout_ms / 1000
    changed_at = None
    last = before
    while time.perf_counter() < deadline:
        current = await page.locator("body").inner_text()
        now = time.perf_counter()
        if current != last:
            last = current
            changed_at = changed_at or now
        elif changed_at and now - changed_at >= 1.2:
            return current, now - started
        await page.wait_for_timeout(250)
    raise TimeoutError("응답이 제한 시간 안에 안정화되지 않았습니다.")


def write_reports(results: list[dict], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    rows = []
    for item in results:
        rows.append(
            "<tr><td>{id}</td><td>{q}</td><td class='{status}'>{status}</td>"
            "<td>{elapsed}</td><td><pre>{answer}</pre></td></tr>".format(
                id=item["id"], q=html.escape(item["question"]),
                status=item["status"], elapsed=item.get("elapsed", "-"),
                answer=html.escape(item.get("answer", item.get("error", ""))),
            )
        )
    page = """<!doctype html><meta charset='utf-8'><title>CSC AI 테스트 결과</title>
<style>body{font:14px sans-serif;margin:24px}table{border-collapse:collapse;width:100%}
td,th{border:1px solid #ddd;padding:8px;vertical-align:top}pre{white-space:pre-wrap}
.PASS{color:green}.FAIL{color:#b00}</style><h1>CSC AI 테스트 결과</h1>
<p>생성 시각: {created}</p><table><tr><th>ID</th><th>질문</th><th>상태</th>
<th>초</th><th>응답</th></tr>{rows}</table>""".format(
        created=datetime.now().isoformat(timespec="seconds"), rows="".join(rows)
    )
    output.with_suffix(".html").write_text(page, encoding="utf-8")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-file", type=Path, required=True, help="### Q: 형식의 Markdown 파일")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--profile", type=Path, default=Path(".cscai-browser-profile"))
    parser.add_argument("--output", type=Path, default=Path("chat-test-results.json"))
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--limit", type=int, help="앞에서부터 실행할 케이스 수")
    parser.add_argument("--headless", action="store_true", help="브라우저 창 숨김")
    args = parser.parse_args()
    questions = load_questions(args.case_file)
    if args.limit:
        questions = questions[: args.limit]

    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            str(args.profile), headless=args.headless, viewport={"width": 1440, "height": 900}
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(args.url, wait_until="domcontentloaded", timeout=args.timeout * 1000)
        await visible_editor(page, args.timeout * 1000)
        results = []
        for index, question in enumerate(questions, 1):
            try:
                answer, elapsed = await send_and_collect(page, question, args.timeout * 1000)
                results.append({"id": f"TC-{index:02d}", "question": question,
                                "status": "PASS", "elapsed": round(elapsed, 2), "answer": answer})
                print(f"TC-{index:02d} PASS {elapsed:.1f}s")
            except Exception as exc:
                results.append({"id": f"TC-{index:02d}", "question": question,
                                "status": "FAIL", "error": str(exc)})
                print(f"TC-{index:02d} FAIL {exc}")
        write_reports(results, args.output)
        await context.close()
        print(f"결과 저장: {args.output} / {args.output.with_suffix('.html')}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    asyncio.run(main())
