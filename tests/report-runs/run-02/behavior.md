# 挙動レポート — Run 02

| 分類 | Finding | Evidence |
|---|---|---|
| `fact` | mainはCreateFileA、WriteFile、CloseHandleを同一Handle処理で呼ぶ（F-006） | `decompile_function` |
| `fact` | mainはsimple_xorへ0x5Aを渡し、CalleeにXOR演算がある（F-007） | `decompile_function` |
| `fact` | simple_xorはbyte引数2件、Complexity 1、1 Basic Block、Loopなし（F-008） | `get_function_variables`、`analyze_control_flow` |
| `inference` | 0x5Aは単純XORキー候補であり、Credentialではない（I-003） | F-007 |
| `inference` | CloseHandleをAnti-debug highとしたDetector結果は誤検知の可能性が高い（F-004、I-002） | mainのコード文脈 |
| `unknown` | 標準暗号と暗号キー（U-004） | `detect_crypto_constants`が未実装 |
| `unknown` | kの詳細Dataflow（U-005） | `analyze_dataflow`はEntryにPCodeなし |

静的解析結果であり、実行時挙動や悪性を断定しない。
