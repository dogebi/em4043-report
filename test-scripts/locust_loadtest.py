#!/usr/bin/env python3
"""
부하 테스트 스크립트 - Locust
20명 동시 접속 시나리오 (PERF-004)

사용법:
    pip install locust --break-system-packages
    locust -f locust_loadtest.py --host=https://csc-ai.natec.cn --users=20 --spawn-rate=5 --run-time=1800 --html
"""

from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import random
import time
from datetime import datetime

# 테스트 사용자 클래스
class CSCUser(HttpUser):
    """NTT CSC AI 시스템 테스트 사용자"""

    # 요청 사이의 대기 시간 (1~3초)
    wait_time = between(1, 3)

    def on_start(self):
        """사용자 시작 시 실행"""
        self.user_id = f"test_user_{random.randint(1000, 9999)}"
        self.project_id = f"project_{random.randint(1, 5)}"
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 사용자 시작: {self.user_id}")

    @task(3)
    def view_dashboard(self):
        """대시보드 조회 (PERF-001)"""
        with self.client.get("/api/v1/appinfo", catch_response=True, name="앱 정보 조회") as response:
            if response.status_code == 200:
                # P95 목표: 2초 미만
                if response.elapsed.total_seconds() > 2:
                    events.request_failure.fire(
                        request_type="GET",
                        name="앱 정보 조회",
                        response_time=response.elapsed.total_seconds(),
                        response_length=len(response.content),
                        exception="Response time > 2s"
                    )

    @task(5)
    def search_knowledge(self):
        """지식库 검색 (PERF-003)"""
        queries = [
            "데이터베이스 연결",
            "서버 성능 저하",
            "네트워크 설정",
            "백업 방법",
            "모니터링 도구"
        ]
        query = random.choice(queries)

        self.client.get(
            f"/api/v1/knowledge/search?query={query}",
            name="지식库 검색"
        )

    @task(2)
    def list_projects(self):
        """프로젝트 목록 조회"""
        self.client.get("/api/v1/projects", name="프로젝트 목록")

    @task(4)
    def view_issues(self):
        """워크 목록 조회 (20명 중 5명)"""
        self.client.get("/api/v1/issues", name="워크 목록 조회")

    @task(3)
    def create_diagnostic_request(self):
        """진단 요청 생성 (EXEC-021)"""
        # 실제 환경에서는 유효한 세션 ID와 토큰 필요
        with self.client.post(
            "/api/v1/sessions",
            json={
                "issue_key": f"TEST-{random.randint(1000, 9999)}",
                "task_type": "diagnosis"
            },
            catch_response=True,
            name="진단 요청 생성"
        ) as response:
            # 진단 요청은 5초 이내 응답 기대
            if response.ok and response.elapsed.total_seconds() > 5:
                events.request_failure.fire(
                    request_type="POST",
                    name="진단 요청 생성",
                    response_time=response.elapsed.total_seconds(),
                    response_length=len(response.content),
                    exception="Response time > 5s"
                )

    @task(1)
    def upload_document(self):
        """문서 업로드 (지식库)"""
        # 실제 파일 업로드는 multipart/form-data 필요
        # 여기서는 API 호출만 시뮬레이션
        self.client.post(
            "/api/v1/knowledge/upload",
            json={"filename": f"doc_{random.randint(1000, 9999)}.pdf"},
            name="문서 업로드 시도"
        )

    @task(2)
    def view_statistics(self):
        """통계 데이터 조회"""
        endpoints = [
            "/api/v1/stats/overview",
            "/api/v1/stats/performance",
            "/api/v1/stats/issues"
        ]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, name="통계 데이터 조회")


class AdminUser(HttpUser):
    """관리자 테스트 사용자 (20명 중 5명)"""

    wait_time = between(2, 5)

    @task(3)
    def view_admin_dashboard(self):
        """관리자 대시보드"""
        self.client.get("/api/v1/admin/dashboard", name="관리자 대시보드")

    @task(2)
    def list_all_users(self):
        """전체 사용자 목록"""
        self.client.get("/api/v1/admin/users", name="사용자 목록 관리")

    @task(2)
    def view_audit_logs(self):
        """감사 로그 조회"""
        self.client.get(
            "/api/v1/admin/audit-logs",
            params={"page": random.randint(1, 10)},
            name="감사 로그 조회"
        )


# 사용자 비율 설정 (20명 중 15명은 일반 사용자, 5명은 관리자)
class WebsiteUser(HttpUser):
    pass


class LoadTestShape:
    """부하 테스트 형상 설정"""

    # 단계별 사용자 증가
    # 0~5분: 5명
    # 5~10분: 10명
    # 10~15분: 20명
    # 15~30분: 20명 유지

    def tick(self):
        run_time = self.runner.get_run_time()

        if run_time < 300:  # 5분
            user_count = 5
        elif run_time < 600:  # 10분
            user_count = 10
        elif run_time < 900:  # 15분
            user_count = 20
        else:  # 15분 이후
            user_count = 20

        # 일반 사용자 80%, 관리자 20%
        normal_users = int(user_count * 0.8)
        admin_users = user_count - normal_users

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 부하 조정: 총 {user_count}명 (일반: {normal_users}, 관리: {admin_users})")

        # 사용자 수 조정 (실제 구현시 필요)
        # Locust는 자동으로 users 파라미터를 따름


# 실행 예시 커맨드
print("""
========================================
NTT CSC AI 부하 테스트 - Locust
========================================

테스트 시나리오:
- 총 사용자: 20명
- 실행 시간: 30분 (1800초)
- 사용자 증가율: 5명/5초

사용자 유형:
- 일반 사용자 (16명):
  * 앱 정보 조회 (3)
  * 지식库 검색 (5)
  * 프로젝트 목록 (2)
  * 워크 목록 (4)
  * 진단 요청 (3)
  * 통계 데이터 (2)
  * 문서 업로드 (1)

- 관리자 (4명):
  * 관리자 대시보드 (3)
  * 사용자 관리 (2)
  * 감사 로그 (2)

성능 목표 (PERF-001, 002, 003, 004):
- P95 페이지 로딩: < 2초
- P95 첫 토큰 응답: < 5초
- P95 지식库 검색: < 2초
- CPU/메모리: < 80%
- 요청 시간초: 0%

실행 방법:
    pip install locust --break-system-packages
    locust -f locust_loadtest.py --host=https://csc-ai.natec.cn \\
          --users=20 --spawn-rate=5 --run-time=1800 \\
          --html --csv=test_results

웹 UI 실행:
    locust -f locust_loadtest.py --host=https://csc-ai.natec.cn \\
          --users=20 --spawn-rate=5 --run-time=1800 \\
          --headless --html --csv=test_results

Docker 실행:
    docker run -p 8089:8089 -v $PWD:/mnt/locust \\
      locustio/locust -f /mnt/locust/locust_loadtest.py \\
      --host=https://csc-ai.natec.cn \\
      --users=20 --spawn-rate=5 --run-time=1800 \\
      --headless --html --csv=/mnt/locust/test_results
""")
