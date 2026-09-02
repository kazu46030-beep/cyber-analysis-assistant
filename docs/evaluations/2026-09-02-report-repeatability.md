# 現行PE レポート反復評価（2026-09-02）

## 目的

現在の無害PEから正規化した固定Evidenceを入力として、外部通信・IOC、挙動、永続化、不審度、Fullの5モードが毎回生成され、主要な意味が変化しないことを確認する。

## 方法

- 入力: `tests/fixtures/evidence/valid-safe-test-pe.json`
- Run 01: `tests/expected-reports/`
- Run 02: `tests/report-runs/run-02/`
- Run 03: `tests/report-runs/run-03/`
- MCP再実行: なし
- 比較単位: 文章の完全一致ではなく、判定、主要Finding ID、Evidence Tool、静的解析上の制約

## 合格条件

- 3 Runすべてで5/5モードが生成される。
- 通信=`not_found_in_reviewed_scope`、永続化=`unknown`、不審度=`assessment_deferred`が一致する。
- F-003、F-004、F-006、F-007、F-008、I-002、I-003、U-001、U-002、U-004、U-005がFullレポートに残る。
- 全モードで`fact`、`inference`、`unknown`、Evidence Tool、静的解析の制約を確認できる。
- 悪性、安全性、実行時通信、永続化成功を根拠なく断定しない。

## 結果

| 指標 | 結果 |
|---|---|
| Run数 | 3 |
| レポート数 | 5 × 3 = 15 |
| 生成成功 | 15/15 |
| 判定一致 | 3/3 |
| 主要Finding一致 | 3/3 |
| 禁止断定 | 0件 |
| MCP再実行 | 0回 |

`python3 scripts/evaluate_report_runs.py`は`status=pass`、`semantic_consistency=true`を返した。

## 制約

3 Runは同じCodex会話内で順次作成したため、完全に独立したモデル実行ではない。異なるSession、Model Version、Temperature相当の条件を跨いだ再現性は`unknown`であり、将来の評価対象とする。
