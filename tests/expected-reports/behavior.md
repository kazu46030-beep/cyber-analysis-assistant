# 挙動まとめ（期待出力）

## 要約

一般的なRuntime処理に加え、選定したmainの疑似コードでファイル作成・書込み・CloseHandleと単純XOR変換を確認した。実行時挙動は断定しない。

| 観点 | 分類 | Finding | 根拠 | 制約 |
|---|---|---|---|---|
| File／Directory操作 | `fact` | CreateFileA、WriteFile、CloseHandleをImport | F-001、`list_imports`、offset=0、limit=50 | 呼出し未確認 |
| File／Directory操作 | `fact` | mainがCreateFileA、WriteFile、CloseHandleを同一Handle処理で呼出し | F-006、`decompile_function` | 選定mainの静的コード |
| Process／Thread／Memory操作 | `unknown` | Process／Thread操作は未評価 | `list_imports` | 対象コード未確認 |
| Registry／Service／Task操作 | `unknown` | 構成変更は未評価 | U-002、`list_imports` | Strings・Xref未取得 |
| Network／IPC | `fact` | 確認した19件のImportに通信関連APIなし | F-003、`list_imports` | 確認範囲限定 |
| Network／IPC | `unknown` | 実行時通信とEndpointは未確認 | U-001 | 動的解決を含め未評価 |
| Discovery／Collection | `unknown` | 未評価 | `list_imports` | コード未確認 |
| Encoding／Encryption／Compression | `fact` | mainからsimple_xorへ0x5Aを渡し、CalleeでXOR演算 | F-007、`decompile_function` | 選定2関数、疑似コード非保存 |
| Encoding／Encryption／Compression | `fact` | simple_xorはbyte引数2個、Complexity 1、1 Basic Block、Loopなし | F-008、`analyze_control_flow` | 単純変換として整合 |
| Encoding／Encryption／Compression | `inference` | 0x5Aは単純XORのキー候補 | I-003 | 標準暗号またはCredentialではない |
| Encoding／Encryption／Compression | `unknown` | 標準暗号定数・暗号キー | U-004、`detect_crypto_constants` | Detector未実装 |
| Encoding／Encryption／Compression | `unknown` | kの詳細Dataflow | U-005、`analyze_dataflow` | 関数EntryにPCode操作なし。迂回せず停止 |
| Defense Evasion／Anti-analysis | `fact` | DetectorがCloseHandleをhigh候補として1件出力 | F-004、`find_anti_analysis_techniques` | Detector出力についてのfact |
| Defense Evasion／Anti-analysis | `inference` | CloseHandleは通常のファイルHandle終了であり、Detector誤検知の可能性 | I-002、F-006 | 選定mainに基づき信頼度high |
| Defense Evasion／Anti-analysis | `unknown` | main以外のAnti-debug処理 | U-003 | 全関数は未確認 |

静的解析の限定Evidenceであり、Importの存在だけで機能が実行されるとは判断しない。
