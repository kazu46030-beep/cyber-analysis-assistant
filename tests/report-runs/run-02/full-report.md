# Full静的解析レポート — Run 02

## 1. エグゼクティブサマリー

mainのファイル処理と、0x5Aを引数とする単純XOR変換を確認した。不審度は`assessment_deferred`。

## 2. 対象と解析範囲

識別子除去済みの無害PE。`list_imports`、関数一覧、Xref／Callee、mainとsimple_xorの`decompile_function`、Control Flowを確認した。

## 3. 不審度と判定上の制約

主要領域が未確認のため合計を確定しない。

## 4. 外部通信・IOC候補

`not_found_in_reviewed_scope`（F-003）。実行時通信は`unknown`（U-001）。IOC候補なし。

## 5. 挙動まとめ

`fact`: ファイルHandle処理（F-006）、simple_xorと0x5A（F-007）、低複雑度（F-008）。

## 6. 永続化

`unknown`（U-002）。

## 7. 難読化・Packing・Anti-analysisの兆候

`fact`: DetectorはCloseHandleをhigh候補化（F-004）。`inference`: main文脈から誤検知可能性が高い（I-002）。0x5Aは単純XORキー候補（I-003）。標準暗号は`unknown`（U-004）。

## 8. 注目関数

main、simple_xor。疑似コード本文は保存していない。

## 9. Findings一覧

F-003、F-004、F-006、F-007、F-008、I-002、I-003、U-001、U-002、U-004、U-005。

## 10. 未確認事項と追加調査候補

他関数、限定Strings、永続化関連参照。DataflowはPCode操作Addressの根拠が得られた場合だけ再検討する。

## 11. 利用Toolと取得範囲

`list_imports` limit=50、Xref／Callee limit=50、選定2関数の`decompile_function`、`analyze_control_flow`。

## 12. 静的解析の制約

実行時挙動、通信成立、永続化成功、悪性または安全性を断定しない。
