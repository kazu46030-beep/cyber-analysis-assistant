# 不審度評価 — Run 02

## 総合

`assessment_deferred`。合計値は確定しない。

- `fact`: mainのファイル処理（F-006）、単純XOR（F-007、F-008）、Detector出力（F-004）。根拠は`decompile_function`、`analyze_control_flow`、`list_imports`。
- `inference`: 0x5AはXORキー候補（I-003）。CloseHandleのAnti-debug判定はコード文脈から誤検知可能性が高い（I-002）。
- `unknown`: 通信（U-001）、永続化（U-002）、標準暗号（U-004）、詳細Dataflow（U-005）。

本結果は静的解析によるトリアージ優先度であり、マルウェアまたは安全性の判定ではない。調査Coverageが主要領域を満たしていない。
