#!/usr/bin/env python3
"""
API 보안 테스트 스크립트
- SQL Injection 테스트 (SEC-014)
- 권한 확인 테스트 (SEC-001, SEC-002)
- XSS 테스트 (SEC-015)
- CSRF 테스트 (SEC-016)
- Rate Limiting 테스트 (SEC-017)
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class APISecurityTester:
    def __init__(self, base_url: str = "https://csc-ai.natec.cn"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

    def log(self, message: str):
        """로그 출력"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")

    def test_sql_injection(self) -> Dict[str, Any]:
        """SQL Injection 테스트 (SEC-014)"""
        self.log("="*60)
        self.log("SEC-014: SQL Injection 테스트 시작")
        self.log("="*60)

        sql_payloads = [
            "' OR 1=1 --",
            "1' UNION SELECT username,password FROM users --",
            "'; DROP TABLE users--",
            "1' AND 1=1--",
            "admin'--",
            "' OR '1'='1",
        ]

        endpoints = [
            "/api/v1/issues",
            "/api/v1/knowledge/search",
            "/api/v1/sessions",
            "/api/v1/projects",
        ]

        results = []

        for endpoint in endpoints:
            self.log(f"\n엔드포인트 테스트: {endpoint}")

            for payload in sql_payloads:
                # GET 파라미터 테스트
                try:
                    response = self.session.get(
                        f"{self.base_url}{endpoint}",
                        params={"query": payload},
                        timeout=10
                    )

                    result = {
                        'endpoint': endpoint,
                        'payload': payload[:50] + '...',
                        'method': 'GET',
                        'status_code': response.status_code,
                        'safe': response.status_code in [400, 401, 403, 404, 422],
                        'response_preview': response.text[:100]
                    }

                    if result['safe']:
                        self.log(f"  ✓ {payload[:30]}... -> {response.status_code} (차단됨)")
                    else:
                        self.log(f"  ✗ {payload[:30]}... -> {response.status_code} (위험!)")
                        result['risk'] = 'HIGH'

                    results.append(result)

                except Exception as e:
                    self.log(f"  ⚠ GET 요청 실패: {e}")
                    results.append({
                        'endpoint': endpoint,
                        'payload': payload[:50],
                        'method': 'GET',
                        'error': str(e)
                    })

                # POST 바디 테스트
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"query": payload},
                        timeout=10
                    )

                    result = {
                        'endpoint': endpoint,
                        'payload': payload[:50] + '...',
                        'method': 'POST',
                        'status_code': response.status_code,
                        'safe': response.status_code in [400, 401, 403, 404, 422],
                        'response_preview': response.text[:100]
                    }

                    if result['safe']:
                        self.log(f"  ✓ POST {payload[:30]}... -> {response.status_code} (차단됨)")
                    else:
                        self.log(f"  ✗ POST {payload[:30]}... -> {response.status_code} (위험!)")
                        result['risk'] = 'HIGH'

                    results.append(result)

                except Exception as e:
                    self.log(f"  ⚠ POST 요청 실패: {e}")
                    results.append({
                        'endpoint': endpoint,
                        'payload': payload[:50],
                        'method': 'POST',
                        'error': str(e)
                    })

        # 결과 집계
        safe_count = sum(1 for r in results if r.get('safe', False))
        total_count = len(results)

        self.log(f"\nSQL Injection 테스트 결과:")
        self.log(f"  총 테스트: {total_count}건")
        self.log(f"  안전함: {safe_count}건 ({safe_count/total_count*100:.1f}%)")
        self.log(f"  위험함: {total_count - safe_count}건")

        self.results['tests']['sql_injection'] = results
        return results

    def test_authorization(self) -> Dict[str, Any]:
        """권한 확인 테스트 (SEC-001, SEC-002)"""
        self.log("\n" + "="*60)
        self.log("SEC-001/002: 권한 확인 테스트 시작")
        self.log("="*60)

        # SEC-001: 횡向 권한 테스트 (프로젝트 간 권한)
        self.log("\n[SEC-001] 횡向 권한 테스트")
        self.log("시나리오: 사용자 A가 프로젝트 X만 접근 가능할 때, 프로젝트 Y 접근 시도")

        # SEC-002: 종向 권한 테스트 (일반 사용자 → 관리자 API)
        self.log("\n[SEC-002] 종向 권한 테스트")
        self.log("시나리오: 일반 사용자가 관리자 API 접근 시도")

        test_cases = [
            {
                'name': '횡向 권한 - 다른 프로젝트 워크 접근',
                'method': 'GET',
                'endpoint': '/api/v1/issues/{issue_id}',
                'expected': 403
            },
            {
                'name': '횡向 권한 - 다른 프로젝트 자산 접근',
                'method': 'GET',
                'endpoint': '/api/v1/assets/{asset_id}',
                'expected': 403
            },
            {
                'name': '종向 권한 - 관리자 API 접근',
                'method': 'POST',
                'endpoint': '/api/v1/admin/users',
                'expected': 403
            },
            {
                'name': '종向 권한 - 시스템 설정 변경',
                'method': 'PUT',
                'endpoint': '/api/v1/admin/settings',
                'expected': 403
            }
        ]

        results = []

        for test_case in test_cases:
            self.log(f"\n테스트: {test_case['name']}")

            try:
                # 실제 테스트에서는 유효한 토큰이 필요함
                # 여기서는 시나리오만 설명
                self.log(f"  예상 상태 코드: {test_case['expected']}")
                self.log("  시나리오: 토큰: user_a_token 으로 다른 프로젝트 접근")

                result = {
                    'name': test_case['name'],
                    'method': test_case['method'],
                    'endpoint': test_case['endpoint'],
                    'expected_status': test_case['expected'],
                    'status': 'MANUAL_TEST_REQUIRED',
                    'note': '유효한 토큰과 실제 리소스 ID 필요'
                }

                results.append(result)

            except Exception as e:
                self.log(f"  ✗ 테스트 실패: {e}")
                results.append({
                    'name': test_case['name'],
                    'error': str(e)
                })

        self.results['tests']['authorization'] = results
        return results

    def test_xss(self) -> Dict[str, Any]:
        """XSS 테스트 (SEC-015)"""
        self.log("\n" + "="*60)
        self.log("SEC-015: XSS 공격 방어 테스트")
        self.log("="*60)

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "'><script>alert(String.fromCharCode(88,83,83))</script>",
            "\"onfocus=alert('XSS') autofocus=\"",
            "<svg onload=alert('XSS')>",
        ]

        endpoints = [
            "/api/v1/sessions/{session_id}/message",
            "/api/v1/issues/{issue_id}/comment",
        ]

        results = []

        for endpoint in endpoints:
            self.log(f"\n엔드포인트 테스트: {endpoint}")

            for payload in xss_payloads:
                try:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={"content": payload},
                        timeout=10
                    )

                    # 응답에 XSS 코드가 그대로 반환되는지 확인
                    response_safe = payload not in response.text

                    result = {
                        'endpoint': endpoint,
                        'payload': payload[:50] + '...',
                        'status_code': response.status_code,
                        'safe': response_safe,
                        'xss_in_response': not response_safe
                    }

                    if response_safe:
                        self.log(f"  ✓ XSS 차단됨: {payload[:30]}...")
                    else:
                        self.log(f"  ✗ XSS 위험: {payload[:30]}...")
                        result['risk'] = 'HIGH'

                    results.append(result)

                except Exception as e:
                    self.log(f"  ⚠ 요청 실패: {e}")
                    results.append({
                        'endpoint': endpoint,
                        'payload': payload[:50],
                        'error': str(e)
                    })

        safe_count = sum(1 for r in results if r.get('safe', False))
        total_count = len(results)

        self.log(f"\nXSS 테스트 결과:")
        self.log(f"  총 테스트: {total_count}건")
        self.log(f"  안전함: {safe_count}건 ({safe_count/total_count*100:.1f}%)")

        self.results['tests']['xss'] = results
        return results

    def test_csrf(self) -> Dict[str, Any]:
        """CSRF 테스트 (SEC-016)"""
        self.log("\n" + "="*60)
        self.log("SEC-016: CSRF 방어 테스트")
        self.log("="*60)

        # CSRF 토큰 없이 POST 요청 시도
        self.log("\n시나리오: CSRF 토큰 없이 상태 변경 요청")

        test_endpoints = [
            ('POST', '/api/v1/admin/users'),
            ('PUT', '/api/v1/admin/settings'),
            ('DELETE', '/api/v1/sessions/{id}'),
        ]

        results = []

        for method, endpoint in test_endpoints:
            self.log(f"\n테스트: {method} {endpoint}")

            try:
                # CSRF 토큰 헤더 없이 요청
                headers = {
                    'Content-Type': 'application/json',
                    # 'X-CSRF-TOKEN' 헤더 제외
                }

                if method == 'POST':
                    response = self.session.post(
                        f"{self.base_url}{endpoint}",
                        json={},  # 빈 바디
                        headers=headers,
                        timeout=10
                    )
                elif method == 'PUT':
                    response = self.session.put(
                        f"{self.base_url}{endpoint}",
                        json={},
                        headers=headers,
                        timeout=10
                    )
                elif method == 'DELETE':
                    response = self.session.delete(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        timeout=10
                    )

                result = {
                    'method': method,
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'protected': response.status_code in [403, 401, 422],
                    'csrf_required': True
                }

                if result['protected']:
                    self.log(f"  ✓ CSRF 보호 작동: {response.status_code}")
                else:
                    self.log(f"  ⚠ CSRF 보호 미작동: {response.status_code}")

                results.append(result)

            except Exception as e:
                self.log(f"  ⚠ 요청 실패: {e}")
                results.append({
                    'method': method,
                    'endpoint': endpoint,
                    'error': str(e)
                })

        self.results['tests']['csrf'] = results
        return results

    def test_rate_limiting(self) -> Dict[str, Any]:
        """Rate Limiting 테스트 (SEC-017)"""
        self.log("\n" + "="*60)
        self.log("SEC-017: Rate Limiting 테스트")
        self.log("="*60)

        self.log("\n시나리오: 1분 내 10회 이상 로그인 요청")

        results = []
        login_endpoint = f"{self.base_url}/api/v1/auth/login"

        self.log(f"\n로그인 엔드포인트: {login_endpoint}")

        for i in range(15):  # 15회 요청
            try:
                start_time = time.time()

                response = self.session.post(
                    login_endpoint,
                    json={
                        "username": "test_user",
                        "password": "wrong_password"  # 의도적으로 잘못된 비밀번호
                    },
                    timeout=10
                )

                elapsed_time = (time.time() - start_time) * 1000  # ms

                self.log(f"  요청 #{i+1}: {response.status_code} ({elapsed_time:.0f}ms)")

                result = {
                    'request_number': i + 1,
                    'status_code': response.status_code,
                    'response_time_ms': round(elapsed_time, 2),
                    'rate_limited': response.status_code == 429
                }

                if response.status_code == 429:
                    self.log(f"    ✓ Rate Limiting 발동! (요청 #{i+1})")
                    result['rate_limit_threshold'] = i + 1
                    break

                results.append(result)

            except Exception as e:
                self.log(f"  요청 #{i+1} 실패: {e}")
                results.append({
                    'request_number': i + 1,
                    'error': str(e)
                })

        self.results['tests']['rate_limiting'] = results
        return results

    def test_data_exposure(self) -> Dict[str, Any]:
        """데이터 노출 테스트 (SEC-006)"""
        self.log("\n" + "="*60)
        self.log("SEC-006: 데이터 노출 테스트")
        self.log("="*60)

        self.log("\n시나리오: 민감 정보 포함 응답 확인")

        # 에러 응답에 스택 트레이스 노출 확인
        test_cases = [
            {
                'name': '잘못된 API 엔드포인트',
                'url': f"{self.base_url}/api/v1/invalid-endpoint-xyz123",
                'check': 'stack_trace'
            },
            {
                'name': '잘못된 파라미터',
                'url': f"{self.base_url}/api/v1/issues",
                'params': {'invalid_param': 'value'},
                'check': 'stack_trace'
            },
            {
                'name': '잘못된 JSON 형식',
                'url': f"{self.base_url}/api/v1/sessions",
                'json': 'invalid json{{{',
                'check': 'stack_trace'
            }
        ]

        results = []

        for test_case in test_cases:
            self.log(f"\n테스트: {test_case['name']}")

            try:
                if test_case.get('params'):
                    response = self.session.get(
                        test_case['url'],
                        params=test_case['params'],
                        timeout=10
                    )
                elif test_case.get('json'):
                    response = self.session.post(
                        test_case['url'],
                        data=test_case['json'],
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                else:
                    response = self.session.get(test_case['url'], timeout=10)

                # 스택 트레이스 노출 확인
                has_stack_trace = any(keyword in response.text.lower() for keyword in [
                    'stack trace', 'exception', 'error in sql',
                    'mysql', 'database error', 'query failed',
                    'file.php', 'line ', 'traceback'
                ])

                # 민감 정보 노출 확인
                has_sensitive_data = any(keyword in response.text.lower() for keyword in [
                    'password', 'secret', 'api_key', 'token',
                    'private key', 'database', 'connection string'
                ])

                result = {
                    'name': test_case['name'],
                    'status_code': response.status_code,
                    'has_stack_trace': has_stack_trace,
                    'has_sensitive_data': has_sensitive_data,
                    'safe': not (has_stack_trace or has_sensitive_data)
                }

                if result['safe']:
                    self.log(f"  ✓ 안전한 에러 처리")
                else:
                    self.log(f"  ✗ 정보 노출 위험!")
                    if has_stack_trace:
                        self.log(f"    - 스택 트레이스 노출")
                    if has_sensitive_data:
                        self.log(f"    - 민감 정보 노출")

                results.append(result)

            except Exception as e:
                self.log(f"  ⚠ 요청 실패: {e}")
                results.append({
                    'name': test_case['name'],
                    'error': str(e)
                })

        self.results['tests']['data_exposure'] = results
        return results

    def generate_report(self) -> Dict[str, Any]:
        """테스트 보고서 생성"""
        self.log("\n" + "="*60)
        self.log("API 보안 테스트 결과 보고서")
        self.log("="*60)

        # 모든 테스트 실행
        self.test_sql_injection()
        self.test_authorization()
        self.test_xss()
        self.test_csrf()
        self.test_rate_limiting()
        self.test_data_exposure()

        # 결과 요약
        self.log("\n" + "="*60)
        self.log("테스트 결과 요약")
        self.log("="*60)

        total_tests = 0
        passed_tests = 0

        for test_name, test_results in self.results['tests'].items():
            if isinstance(test_results, list):
                total_tests += len(test_results)
                passed = sum(1 for r in test_results if r.get('safe', False) or r.get('protected', False))
                passed_tests += passed

                self.log(f"\n{test_name}:")
                self.log(f"  테스트 수: {len(test_results)}")
                self.log(f"  통과: {passed} ({passed/len(test_results)*100:.1f}%)")

        self.log(f"\n총계:")
        self.log(f"  전체 테스트: {total_tests}건")
        self.log(f"  통과: {passed_tests}건 ({passed_tests/total_tests*100:.1f}%)")
        self.log(f"  실패: {total_tests - passed_tests}건")

        return self.results

def main():
    """메인 실행 함수"""
    print("="*60)
    print("API 보안 테스트 스크립트")
    print("실행 일시:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*60)

    # 테스터 인스턴스 생성
    tester = APISecurityTester()

    try:
        # 모든 테스트 실행 및 보고서 생성
        results = tester.generate_report()

        # 보고서 저장
        report_file = 'D:\\dev\\cscAI\\TestCase111\\test-reports\\20260810\\SEC-API-TEST-RESULTS.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 보고서 저장 완료: {report_file}")

        return 0

    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"\n✗ 실행 실패: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
