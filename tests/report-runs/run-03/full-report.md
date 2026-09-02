# Full静的解析レポート — Run 03

## 1. エグゼクティブサマリー

ファイル書込みと単純XORを確認。不審度は`assessment_deferred`。

## 2. 対象と解析範囲

無害な固定Evidence。識別子除去済み。`list_imports`と選定関数の`decompile_function`等を利用。

## 3. 不審度と判定上の制約

Coverage不足のため合計なし。

## 4. 外部通信・IOC候補

`not_found_in_reviewed_scope`（F-003）。通信は`unknown`（U-001）。

## 5. 挙動まとめ

`fact`: mainのFile API（F-006）、simple_xor／0x5A（F-007）、Complexity 1（F-008）。

## 6. 永続化

`unknown`（U-002）。

## 7. 難読化・Packing・Anti-analysisの兆候

`fact`: Detector出力F-004。`inference`: 誤検知候補I-002、XORキー候補I-003。`unknown`: 標準暗号U-004、Dataflow U-005。

## 8. 注目関数

mainとsimple_xor。疑似コード本文は非保存。

## 9. Findings一覧

F-003、F-004、F-006、F-007、F-008、I-002、I-003、U-001、U-002、U-004、U-005。

## 10. 未確認事項と追加調査候補

他関数、Strings、永続化参照。

## 11. 利用Toolと取得範囲

`list_imports` limit=50、Xref／Callee limit=50、Decompiler 2関数、`analyze_control_flow` 1関数。

## 12. 静的解析の制約

実行時挙動、通信、永続化、悪性、安全性は未確認。
