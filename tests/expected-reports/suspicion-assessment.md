# 不審度評価（期待出力）

## 総合判定

- レベル: `assessment_deferred`
- 合計: 確定しない
- 理由: 主要領域のコード関係、Strings、Anti-analysisが未確認

| 評価軸 | 暫定点 | 分類 | 根拠・反証 |
|---|---:|---|---|
| 外部通信 | 0 | `fact` / `unknown` | 19 Importsに通信APIなし。ただしEndpointと動的解決は未確認（F-003、U-001、`list_imports`） |
| 永続化 | 0 | `unknown` | 支持Evidenceなし。ただしCoverage不足（U-002） |
| Process／Memory操作 | 0 | `unknown` | 未評価 |
| Discovery／Collection／Credential | 0 | `unknown` | 未評価 |
| 難読化／Packing／Anti-analysis | 1 | `fact` / `inference` / `unknown` | 単純XOR候補あり。CloseHandle Detector結果はmainのコード文脈から誤検知の可能性が高い（F-004、F-006、F-007、I-002、I-003） |
| 破壊的処理／権限操作／Security干渉 | 0 | `unknown` | 未評価 |

## inference

CreateFileA、WriteFile、CloseHandleはmain内で通常のファイルHandle処理として利用される。Anti-analysis DetectorがCloseHandleをhighとした結果はコード文脈と整合せず、I-002を誤検知可能性highとする。0x5Aによる単純XORは変換能力を示すが、単独で悪性または強い難読化根拠にはしない。

## 調査Coverage

- 確認済み: Metadata 1件、Imports 19件、Exports 29件、Functions一覧32件、補助Detector 3種、main Xref／Callee、mainとsimple_xorの個別Decompiler
- 未確認: Strings、main以外の広範なXref、実行時挙動
- Tool制約: Crypto Detectorは未実装で、キー抽出結果は得られない

本評価は静的解析に基づくトリアージ優先度であり、マルウェア判定ではない。
