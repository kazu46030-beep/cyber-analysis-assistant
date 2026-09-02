# 永続化レポート（期待出力）

## 判定

`unknown`

## Findings

| 分類 | 内容 | 根拠 | 制約 |
|---|---|---|---|
| `fact` | 確認した19件のImportからは永続化固有のAPI関係を確認できない | `list_imports`、offset=0、limit=50 | Import確認だけではCoverage不足 |
| `inference` | 現在の限定Evidenceは永続化を支持しない | U-002 | 不存在の証明ではない |
| `unknown` | Run／RunOnce、Service、Scheduled Task、Startup、COM、Winlogon、WMI、Side-loading | U-002 | Strings・Xref・疑似コード未取得 |

静的解析だけでは永続化の実行または成功を断定できない。追加確認する場合は、永続化関連語を限定した`list_strings`と、根拠を得たAddressに対するXref確認が必要である。
