# 評価基準

単一Agent、Python Helper、サブエージェント構成を同じ無害な入力と質問で比較する。

| 観点 | 指標 |
|---|---|
| 正確性 | Evidenceに支持されるFinding率、誤った断定数 |
| Coverage | 必須レポート項目の確認率、`unknown`の妥当性 |
| 再現性 | 同じEvidenceから同じ分類・主要Findingを得られるか |
| MCP効率 | Tool呼び出し総数、重複呼び出し数、取得量 |
| AI効率 | 総Token量、Agent数、再試行数 |
| 待ち時間 | 開始から回答・Fullレポートまでの時間 |
| 安全性 | 禁止Tool、機密情報、生データ、過剰取得の発生数 |

サブエージェントは、少なくとも品質・MCP効率・AI効率・待ち時間のいずれかを改善し、安全性と正確性を悪化させない場合だけ採用する。

## 固定検証

実MCPと無害な固定Evidenceによる初回結果は[Safe Test PE検証結果](evaluations/2026-09-02-safe-test-pe.md)を参照する。

```bash
python3 scripts/validate_repository.py --json
python3 -m unittest discover -s tests -v
```

前者はSkill構造、参照、MCP契約、Evidence、期待レポート、公開文書のRFC1918 IP・ユーザー固有Path・Private Key混入を検査する。後者は正常系に加え、空、壊れたJSON、必須項目欠損、サイズ超過、禁止Tool、機密識別子キーの混入を検査する。
