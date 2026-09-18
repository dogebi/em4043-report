# NTT CSC AI智能运维助手系统 - 改善推奨書

## 作成日: 2026-08-13

## 実行概要

全体テスト分析の結果、111件のテストケースのうち：
- **PASS**: 45件 (40.5%)
- **PARTIAL**: 52件 (46.8%)
- **FAIL**: 14件 (12.6%)

本書では特に重要な**高優先度課題**と**中優先度課題**に対する具体的な改善推奨事項を提示します。

---

## 高優先度（P0）課題詳細改善推奨

### P0-1: 工单-会话一対一対応問題 (TICKET-016)

#### 現状
- 同一工单の複数オープン時に複数の会話が作成される可能性
- `SessionService::createSession()` に一意性制約なし
- 会話名が工单番号と一致しない場合あり

#### 改善推奨
```php
// SessionService.php に追加
public function findOrCreateSessionForIssue($issueId, $remoteIssueKey)
{
    // 既存会話の確認
    $existingSession = Session::where('issue_id', $issueId)
        ->where('status', '!=', 'archived')
        ->first();
    
    if ($existingSession) {
        return $existingSession;
    }
    
    // 新規会話作成（一意性担保）
    return Session::create([
        'issue_id' => $issueId,
        'title' => $remoteIssueKey, // 工单番号を強制的に使用
        'status' => 'active',
        // ... その他フィールド
    ]);
}
```

#### 検証方法
1. 同一工单を複数回開いて、会話が1つのみ作成されることを確認
2. 会話名が工单番号と完全一致することを確認
3. 工单タイプ変更時に会話が再作成されないことを確認

---

### P0-2: Jira全量同期未実装 (KB-001)

#### 現状
- Jiraプロジェクト資産の全量クロール入口未実装
- デフォルトスライスが `chunk_token_num=128`（要件：500-1000文字+100文字重複）
- 全量同期後の検証未実施

#### 改善推奨
```php
// JiraProjectService.php に追加
public function fullSyncProjectAssets($projectId)
{
    // 1. Jira Attachments クロール
    $attachments = $this->jiraClient->getProjectAttachments($projectId);
    
    foreach ($attachments as $attachment) {
        // 2. ファイルダウンロード
        $content = $this->downloadAttachment($attachment);
        
        // 3. ドキュメントタイプ認識
        $docType = $this->detectDocumentType($attachment);
        
        // 4. OCR/解析（画像/PDFの場合）
        $text = $this->parseDocument($content, $docType);
        
        // 5. スライス（500-1000文字+100文字重複）
        $chunks = $this->sliceDocument($text, 500, 1000, 100);
        
        // 6. ベクトル化
        $embeddings = $this->generateEmbeddings($chunks);
        
        // 7. 索引作成
        $this->buildIndex($projectId, $chunks, $embeddings);
    }
}

private function sliceDocument($text, $minChunk, $maxChunk, $overlap)
{
    // スライスロジック実装
    $chunks = [];
    $length = mb_strlen($text);
    $position = 0;
    
    while ($position < $length) {
        $chunkSize = rand($minChunk, $maxChunk);
        $chunk = mb_substr($text, $position, $chunkSize);
        $chunks[] = $chunk;
        $position += $chunkSize - $overlap;
    }
    
    return $chunks;
}
```

#### 検証方法
1. 新規プロジェクト接続時に全量同期が実行されることを確認
2. スライスが500-1000文字+100文字重複であることを確認
3. OCR解析が正常に動作することを確認
4. 同期完了24時間以内に検索が可能であることを確認

---

### P0-3: SQL注入脆弱性検証 (SEC-014)

#### 現状
- Laravelパラメータバインディング使用（リスク低減）
- 実際のSQL注入Payloadテスト未実施
- すべてのエンドポイント検証未完了

#### 改善推奨
```python
# SQL注入テストスクリプト
import requests
import json

sql_payloads = [
    "' OR 1=1 --",
    "1' UNION SELECT username,password FROM users --",
    "'; DROP TABLE users--",
    "1' AND 1=1--",
    "<script>alert(1)</script>",
]

def test_sql_injection():
    base_url = "https://csc-ai.natec.cn"
    endpoints = [
        "/api/v1/issues",
        "/api/v1/knowledge/search",
        "/api/v1/sessions",
    ]
    
    results = []
    
    for endpoint in endpoints:
        for payload in sql_payloads:
            # GET parameter テスト
            response = requests.get(
                f"{base_url}{endpoint}",
                params={"query": payload},
                headers={"Authorization": f"Bearer {test_token}"}
            )
            
            if response.status_code != 400 and response.status_code != 422:
                results.append({
                    'endpoint': endpoint,
                    'payload': payload,
                    'status': response.status_code,
                    'risk': 'HIGH'
                })
            
            # POST body テスト
            response = requests.post(
                f"{base_url}{endpoint}",
                json={"query": payload},
                headers={"Authorization": f"Bearer {test_token}"}
            )
            
            if response.status_code != 400 and response.status_code != 422:
                results.append({
                    'endpoint': endpoint,
                    'payload': payload,
                    'method': 'POST',
                    'status': response.status_code,
                    'risk': 'HIGH'
                })
    
    return results

results = test_sql_injection()
print(json.dumps(results, indent=2))
```

#### 検証方法
1. すべてのAPIエンドポイントに対してSQL注入テスト実施
2. 悪意Payloadが適切に拒否されることを確認（HTTP 400/422）
3. データベースエラーが露出しないことを確認
4. パラメータバインディングがすべてのクエリで使用されていることを確認

---

### P0-4: 状態値統一問題 (EXEC-001)

#### 現状
- 会話状態が `active/archived` 使用
- 要件定義書では `running→completed` を要求
- モニタリングツールとの整合性問題

#### 改善推奨
```php
// 状態値定義
class SessionStatus
{
    const ACTIVE = 'active';      // 実行中（要件のrunningに対応）
    const PAUSED = 'paused';      // 一時停止
    const COMPLETED = 'completed'; // 完了
    const FAILED = 'failed';      // 失敗
    const EXPIRED = 'expired';    // 期限切れ
}

// 状態遷移マップ
$stateTransitions = [
    'active' => ['paused', 'completed', 'failed', 'expired'],
    'paused' => ['active', 'expired'],
    'completed' => [], // 最終状態
    'failed' => ['active'], // 再実行可能
    'expired' => [], // 最終状態
];
```

#### 検証方法
1. 状態遷移図を作成し、要件定義書との整合性確認
2. すべての状態遷移パターンテスト実施
3. モニタリングダッシュボードでの状態表示確認

---

### P0-5: Webhook認証ヘッダー統一 (TICKET-001)

#### 現状
- 要件: `X-Jira-Webhook-Secret`
- 実装: `X-Hub-Signature` (HMAC)
- Basic Authもサポート
- ヘッダー名の不一致による認証失敗リスク

#### 改善推奨
```php
// JiraWebhookController.php
public function webhook(Request $request)
{
    // 複数の認証方式をサポート
    $secret = null;
    
    // 1. X-Jira-Webhook-Secret（要件定義書）
    if ($request->hasHeader('X-Jira-Webhook-Secret')) {
        $providedSecret = $request->header('X-Jira-Webhook-Secret');
        if ($providedSecret === config('jira.webhook_secret')) {
            $secret = $providedSecret;
        }
    }
    
    // 2. X-Hub-Signature（現在の実装）
    elseif ($request->hasHeader('X-Hub-Signature')) {
        $signature = $request->header('X-Hub-Signature');
        $payload = $request->getContent();
        $expectedSignature = 'sha1=' . hash_hmac('sha1', $payload, config('jira.webhook_secret'));
        
        if (hash_equals($expectedSignature, $signature)) {
            $secret = $signature;
        }
    }
    
    // 3. Basic Auth
    elseif ($request->hasHeader('Authorization')) {
        // Basic Auth 検証ロジック
    }
    
    if (!$secret) {
        return response()->json(['error' => 'Unauthorized'], 401);
    }
    
    // Webhook処理継続
}
```

#### 検証方法
1. `X-Jira-Webhook-Secret` ヘッダーで認証成功することを確認
2. `X-Hub-Signature` ヘッダーでも認証成功することを確認
3. 間違ったSecretで401エラーが返ることを確認
4. Webhookログに認証成功/失敗が記録されることを確認

---

## 中優先度（P1）課題詳細改善推奨

### P1-1: RedisキャッシュTTL検証 (AUTH-011~013)

#### 現状
- Redisキャッシュの実際のTTL値未検証
- 主キャッシュ1800秒、staleキャッシュ604800秒（コード定義）
- 実際の動作検証不足

#### 改善推奨
```python
# Redisキャッシュ検証スクリプト
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

def test_permission_cache_ttl():
    # 1. 権限キャッシュシミュレーション
    user_id = "test_user_001"
    cache_key = f"ai_work_perm:user:{user_id}:projects"
    
    # キャッシュ書き込み
    cache_data = {
        'projects': ['project_a', 'project_b'],
        'timestamp': int(time.time())
    }
    r.setex(cache_key, 1800, json.dumps(cache_data))
    
    # 2. TTL確認
    ttl = r.ttl(cache_key)
    print(f"Cache TTL: {ttl} seconds (expected: 1800)")
    assert 1700 <= ttl <= 1800, "TTL not in expected range"
    
    # 3. 30分後にstaleキャッシュ確認
    time.sleep(1800)
    stale_key = f"{cache_key}:stale"
    stale_ttl = r.ttl(stale_key)
    print(f"Stale cache TTL: {stale_ttl} seconds (expected: 604800)")
    
    # 4. キャッシュ期限切れ後の挙動
    r.delete(cache_key)
    # Jira APIが呼び出されることをログで確認
    
if __name__ == '__main__':
    test_permission_cache_ttl()
```

#### 検証方法
1. キャッシュ作成時のTTLが1800秒であることを確認
2. キャッシュ期限切れ時にstaleキャッシュが使用されることを確認
3. staleキャッシュのTTLが604800秒（7日）であることを確認
4. Jiraサービス不可用時にstaleキャッシュが機能することを確認

---

### P1-2: 性能テスト実施 (PERF-004)

#### 現状
- 20並行ユーザーの負荷テスト未実施
- P95指標の測定未完了
- CPU/メモリ使用率のモニタリング未実施

#### 改善推奨（JMeterテスト計画）
```xml
<!-- jmeter_test_plan.jmx -->
<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <TestPlan>
      <stringProp name="TestPlan.comments">20並行ユーザー総合シーン</stringProp>
      <boolProp name="TestPlan.serialize_threadgroups">true</boolProp>
    </TestPlan>
    <hashTree>
      <!-- スレッドグループ: 20ユーザー -->
      <ThreadGroup>
        <stringProp name="ThreadGroup.num_threads">20</stringProp>
        <stringProp name="ThreadGroup.ramp_time">60</stringProp>
        <stringProp name="ThreadGroup.duration">1800</stringProp> <!-- 30分 -->
      </ThreadGroup>
      
      <!-- アクション1: 知識庫検索 (5ユーザー) -->
      <!-- アクション2: 診断実行 (5ユーザー) -->
      <!-- アクション3: 工单閲覧 (5ユーザー) -->
      <!-- アクション4: 管理操作 (5ユーザー) -->
      
      <!-- 結果収集 -->
      <ResultCollector/>
      
      <!-- CPU/メモリモニタリング -->
      <BackendListener/>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

#### 検証方法
1. JMeter/Locustで20並行ユーザーシナリオ実行
2. 30分間安定して動作することを確認
3. P95レスポンスタイムが目標以内であることを確認
4. CPU/メモリ使用率が80%未満であることを確認
5. エラー率が0.1%未満であることを確認

---

### P1-3: Audit Agent監査テスト (EXEC-010)

#### 現状
- Audit Agentのリアルタイム監査機能未検証
- 監査レポートの完全性未確認
- after_stageタイミング検証不足

#### 改善推奨
```javascript
// Audit Agent テストシナリオ
const auditTests = [
    {
        name: "正常監査",
        scenario: "段階完了後Audit Agentが自動起動",
        expected: "監査レポート生成、評価結果表示"
    },
    {
        name: "異常検知",
        scenario: "段階実行中に異常発生",
        expected: "リアルタイム監査、異常記録、警報"
    },
    {
        name: "タイミング検証",
        scenario: "audit_timing=after_stage設定",
        expected: "段階完了直後にAudit Agent起動"
    }
];

function testAuditAgent() {
    for (const test of auditTests) {
        console.log(`Testing: ${test.name}`);
        
        // 1. タスク方案実行
        executeTaskPlan();
        
        // 2. 段階完了待機
        waitForStageComplete();
        
        // 3. Audit Agent起動確認
        const auditStarted = checkAuditAgentStarted();
        
        // 4. 監査レポート確認
        const auditReport = getAuditReport();
        
        // 5. 評価
        assert(auditStarted, "Audit Agent started");
        assert(auditReport !== null, "Audit report generated");
        assert(auditReport.status === 'pass' || auditReport.status === 'fail', 
               "Audit report has valid status");
    }
}
```

#### 検証方法
1. 各段階完了後にAudit Agentが自動起動することを確認
2. 監査レポートが正しく生成されることを確認
3. リアルタイム監査で異常を検知できることを確認
4. 監査結果がユーザーに正しく表示されることを確認
5. 監査ログが完全に記録されることを確認

---

### P1-4: 知識蒸留完全テスト (KB-011~012)

#### 現状
- プロジェクトレベルSOP蒸留テスト未完了
- 任务方案レベルSOP蒸留テスト未完了
- SOP品質評価基準未適用

#### 改善推奨
```python
# 知識蒸留テストスクリプト
from datetime import datetime, timedelta

def test_project_level_distillation():
    # 1. 5件以上のクローズド工单を準備
    closed_issues = get_closed_issues('project_x', min_count=5)
    assert len(closed_issues) >= 5, "需要5件以上已关闭工单"
    
    # 2. 品質門確認
    for issue in closed_issues:
        # 完全性チェック
        assert issue.completeness >= 0.8, "工单完全性不足80%"
        
        # 実行時間チェック
        assert issue.duration > 300, "工单执行时长不足5分钟"
    
    # 3. 蒸留実行
    distillation_result = run_distillation(
        project_id='project_x',
        scope='project_level'
    )
    
    # 4. SOP生成確認
    assert distillation_result.sop_generated, "SOP未生成"
    assert distillation_result.scope_type == 'project', "SOP类型不正确"
    
    # 5. Jira回伝確認
    sop_in_jira = check_sop_in_jira_assets(
        project_id='project_x',
        sop_id=distillation_result.sop_id
    )
    assert sop_in_jira, "SOP未回伝至Jira"
    
    # 6. 検索可能確認
    search_result = search_knowledge_base(
        query="project_x故障处理",
        project_id='project_x'
    )
    assert distillation_result.sop_id in search_result, "SOP不可检索"

def test_task_plan_level_distillation():
    # 任务方案レベルSOP蒸留テスト
    cross_project_issues = get_closed_issues_by_task_plan(
        task_plan_id='incident_diagnosis',
        min_count=3
    )
    
    distillation_result = run_distillation(
        task_plan_id='incident_diagnosis',
        scope='task_plan_level'
    )
    
    assert distillation_result.scope_type == 'task_plan', "SOP类型错误"
    assert distillation_result.project_id is None, "任务方案SOP不应绑定项目"
    
    # 全ユーザー検索可能確認
    global_search = search_knowledge_base(
        query="incident诊断",
        project_id=None
    )
    assert distillation_result.sop_id in global_search, "SOP应全局可检索"
```

#### 検証方法
1. プロジェクトレベルSOP蒸留が正常に動作することを確認
2. 任务方案レベルSOP蒸留が正常に動作することを確認
3. 品質門（80%完全性、5分以上実行時間）が適用されることを確認
4. SOPが正しくJiraに回伝されることを確認
5. プロジェクトレベルSOPはプロジェクト内のみ検索可能であることを確認
6. 任务方案レベルSOPは全ユーザー検索可能であることを確認

---

### P1-5: 災害復旧テスト実施 (DR-002)

#### 現状
- MySQL主庫故障時のMHA切替テスト未実施
- 切替時間の10分目標未検証
- データロスト防止検証未完了

#### 改善推奨
```bash
#!/bin/bash
# MySQL MHA切替テストスクリプト

echo "=== MySQL MHA切替テスト開始 ==="

# 1. 現在の主庫確認
CURRENT_MASTER=$(mysql -h db-master -u monitor -p${MONITOR_PASS} -e "SHOW MASTER STATUS;" | tail -n 1)
echo "現在の主庫: ${CURRENT_MASTER}"

# 2. 主庫プロセス停止
echo "主庫プロセス停止..."
kubectl delete pod mysql-master-0 -n production

# 3. MHA切替監視
echo "MHA切替待機..."
START_TIME=$(date +%s)

while true; do
    NEW_MASTER=$(mysql -h db-slave -u monitor -p${MONITOR_PASS} -e "SHOW SLAVE STATUS\G" | grep "Master_Log_File" | awk '{print $2}')
    
    if [ "$NEW_MASTER" != "$CURRENT_MASTER" ]; then
        END_TIME=$(date +%s)
        DURATION=$((END_TIME - START_TIME))
        
        echo "MHA切替完了!"
        echo "切替時間: ${DURATION}秒"
        
        if [ $DURATION -lt 600 ]; then
            echo "✓ 切替時間目標達成 (<10分)"
        else
            echo "✗ 切替時間超過 (>=10分)"
        fi
        
        break
    fi
    
    sleep 5
done

# 4. データ整合性確認
echo "データ整合性確認..."
DATA_CHECK=$(mysql -h db-slave -u app -p${APP_PASS} -e "
    SELECT COUNT(*) FROM aigc_work_issues WHERE created_at > NOW() - INTERVAL 1 HOUR;
")

echo "確認データ: ${DATA_CHECK}"

# 5. アプリケーション接続確認
echo "アプリケーション接続確認..."
APP_TEST=$(curl -s https://csc-ai.natec.cn/api/v1/health | jq '.database.connected')

if [ "$APP_TEST" == "true" ]; then
    echo "✓ アプリケーション接続正常"
else
    echo "✗ アプリケーション接続異常"
fi

echo "=== MySQL MHA切替テスト完了 ==="
```

#### 検証方法
1. 主庫停止時の自動検知を確認（30秒以内）
2. 自動切替が実行されることを確認（10分以内）
3. 従庫が主庫に昇格することを確認
4. アプリケーション接続が自動回復することを確認
5. データロストがないことを確認（バイナリログ適用）
6. 切替後の書き込み/読み込みが正常であることを確認

---

## テスト自動化推奨

### 自動化テストフレームワーク構築

```javascript
// 自動化テストスイート構成
describe('NTT CSC AI智能运维助手系统', () => {
    
    describe('権限控制', () => {
        it('AUTH-001: Jira SSO正常登录', async () => {
            // SSOログインフローテスト
            const result = await testSSOLogin();
            expect(result.status).toBe('completed');
            expect(result.redisCache).toHaveProperty('ttl', 1800);
        });
        
        it('AUTH-011: 権限キャッシュ命中', async () => {
            // キャッシュヒットテスト
            const result = await testPermissionCacheHit();
            expect(result.hit).toBe(true);
            expect(result.responseTime).toBeLessThan(50);
        });
    });
    
    describe('工单管理', () => {
        it('TICKET-001: Webhook触发', async () => {
            // Webhookテスト
            const result = await testWebhookTrigger();
            expect(result.projectCreated).toBe(true);
            expect(result.issueCreated).toBe(true);
            expect(result.sessionCreated).toBe(true);
        });
        
        it('TICKET-016: 工单-会话一対一', async () => {
            // 一対一対応テスト
            const result = await testOneToOneMapping();
            expect(result.sessionCount).toBe(1);
            expect(result.sessionName).toBe(result.issueKey);
        });
    });
    
    describe('セキュリティ', () => {
        it('SEC-014: SQL注入防護', async () => {
            // SQL注入テスト
            const payloads = getSQLInjectionPayloads();
            for (const payload of payloads) {
                const result = await testSQLInjection(payload);
                expect(result.status).toBe(400); // 422でも可
            }
        });
    });
    
    describe('性能', () => {
        it('PERF-001: ページ読み込みP95<2秒', async () => {
            // 負荷テスト
            const result = await runLoadTest({
                users: 20,
                duration: 1800, // 30分
                target: 'page_load'
            });
            expect(result.p95).toBeLessThan(2000);
        });
    });
});
```

---

## 実施スケジュール

### Week 1 (8/13-8/17): P0課題緊急対応

| 日付 | 課題 | 担当 | 進捗確認 |
|---|---|---|---|
| 8/13 (月) | TICKET-016: 会話一対一対応修正 | Backend | コードレビュー |
| 8/14 (火) | KB-001: 全量同期実装開始 | Backend | 設計レビュー |
| 8/15 (水) | SEC-014: SQL注入検証実施 | Security | テスト実施 |
| 8/16 (木) | EXEC-001: 状態値統一 | Backend | コードレビュー |
| 8/17 (金) | TICKET-001: Webhookヘッダー統一 | Backend | 統合テスト |

### Week 2 (8/17-8/21): P1課題対応と性能テスト

| 日付 | 課題 | 担当 | 進捗確認 |
|---|---|---|---|
| 8/17 (月) | AUTH-011~013: Redisキャッシュ検証 | DevOps | テスト実施 |
| 8/18 (火) | PERF-004: 負荷テスト実施 | QA | テスト実施 |
| 8/19 (水) | EXEC-010: Audit Agent監査テスト | QA | テスト実施 |
| 8/20 (木) | KB-011~012: 知識蒸留テスト | QA | テスト実施 |
| 8/21 (金) | COMP-001~004: ブラウザ互換性 | QA | テスト実施 |

### Week 3 (8/21-8/28): 災害復旧と統合テスト

| 日付 | 課題 | 担当 | 進捗確認 |
|---|---|---|---|
| 8/21 (月) | DR-002: MHA切替テスト | DevOps | 本番テスト |
| 8/22 (火) | INT-001: 統合テスト実施 | QA | エンドツーエンド |
| 8/23 (水) | SEC-001~018: セキュリティ再検証 | Security | 完全検証 |
| 8/24 (木) | 回帰テスト開始 | QA | 全体回帰 |
| 8/25 (金) | 回帰テスト継続 | QA | 問題修正 |

### Week 4 (8/28-9/4): 最終検証とUAT準備

| 日付 | 課題 | 担当 | 進捗確認 |
|---|---|---|---|
| 8/28 (月) | 残課題修正 | All | 最終確認 |
| 8/29 (火) | 性能SLA最終検証 | QA | 全項目確認 |
| 8/30 (水) | セキュリティ最終検証 | Security | 全項目合格 |
| 8/31 (木) | UAT準備完了確認 | PM | 準備完了 |
| 9/1 (金) | UAT開始 | All | UAT実施 |

---

## 成功基準

### 短期目標 (8/17達成)
- P0課題: 5件すべて完了
- P0テスト通過率: 100% (69/69)
- 重要脆弱性: 0件

### 中期目標 (8/21達成)
- P1課題: 10件中8件以上完了
- P1テスト通過率: 95%以上 (40/42)
- 全体通過率: 90%以上 (100/111)

### 长期目標 (9/4達成)
- すべてのテストケース実施完了
- 全体通過率: 95%以上 (105/111)
- UAT準備完了
- 運用環境デプロイ可能

---

## 結論

本改善推奨書に基づき、優先順位の高い課題から体系的に対応することで、**9/4のSIT完了**と**9/30のUAT完了**を目標に達成可能です。

特に**P0課題の5項目**はUAT開始前（8/31）までの完了が必須であり、これによりシステムの基本品質とセキュリティが保証されます。

継続的な進捗管理と週次レビューを通じて、スケジュール遵守と品質向上を両立させていくことを推奨します。

---

**作成者**: AIテスト分析システム  
**最終更新**: 2026-08-13  
**文書バージョン**: 1.0
