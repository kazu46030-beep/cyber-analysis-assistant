# 外部通信・IOCレポート（期待出力）

## 判定

`not_found_in_reviewed_scope`

19件のImportを確認した範囲では、通信関連APIまたはEndpoint候補を支持する静的Evidenceは確認されなかった。これは外部通信が存在しないことの証明ではない。

## 通信機能

| 分類 | 内容 | 根拠 | 制約 |
|---|---|---|---|
| `fact` | 確認した19件のImportに通信関連APIは含まれない | `list_imports`、offset=0、limit=50 | Importだけを確認 |
| `inference` | 確認範囲内では通信機能を支持する根拠が弱い | F-003、選定mainの`decompile_function` | Stringsと他関数は未確認 |
| `unknown` | 実行時通信、動的解決API、Endpointの有無 | U-001 | main以外のコードとStringsは網羅していない |

## IOC候補

該当なし。URL、Domain、IP、Emailを外部照会していない。

## 誤検知要因と未確認事項

- 動的API解決や独自通信実装は確認していない。
- 静的解析だけでは実行時通信の有無を断定できない。
