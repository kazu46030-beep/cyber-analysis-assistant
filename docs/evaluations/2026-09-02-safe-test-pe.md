# Safe Test PE 検証結果（2026-09-02）

## 結論

実MCPの接続、許可ToolのSchema一致、限定Evidence取得、5種の期待レポート生成を確認した。安全境界と異常系の自動検査結果は、下記コマンドの実行結果を正とする。

## 対象と保護

- 対象はユーザー作成の無害なWindows PE。
- Program名、実行ファイルPath、Address等のローカル識別子はfixtureへ保存していない。
- 検体、バイト列、全Strings、全逆アセンブル、全疑似コードは取得していない。
- IOCの外部照会、DNS、HTTP、Sandbox提出は行っていない。

## 実MCP契約

| 項目 | 結果 |
|---|---|
| Codex runtime公開Tool総数 | 273 |
| 実MCP `mcp_schema` Tool総数 | 239 |
| Policy許可Tool | 解析用22 Toolと契約確認用2 Toolが公開Catalogに存在 |
| Input Schema | 24/24が保存済み契約と一致 |
| 未記載Tool | 249、default-denyで`blocked_unlisted` |
| Server Version | GhidraMCP 7.0.0、Ghidra 12.1.2 |
| Commit | `unknown`（`get_version`応答には含まれない） |

Codex runtime snapshotは`tests/fixtures/ghidramcp-tool-catalog.json`、実Server Schemaは`tests/fixtures/ghidramcp-server-schema.json`、Versionは`tests/fixtures/ghidramcp-version.json`、独立した期待契約は`tests/contracts/ghidramcp-allowed-tools.json`に保存した。273対239の差は、Codex側に公開された管理・Debugger等の別名またはWrapperを含むためである。許可24 Toolは両方に存在し、Schemaが一致した。

## Evidence取得

| 順序 | Tool | 入力範囲 | 結果 |
|---:|---|---|---|
| 1 | `get_metadata` | 現在Program、引数なし、1回 | 成功 |
| 2 | `list_imports` | offset=0、limit=50 | 19件 |
| 3 | `list_exports` | offset=0、limit=50 | 29件 |
| 4 | `list_functions_enhanced` | offset=0、limit=50 | 32件 |
| 5 | `find_anti_analysis_techniques` | 現在Program | 1件。CloseHandleをhigh候補化 |
| 6 | `detect_crypto_constants` | 現在Program | Tool成功、Detector実装は未完了 |
| 7 | `detect_malware_behaviors` | 現在Program | 0件 |
| 8 | `get_function_by_address` | Detector根拠のmain | 成功 |
| 9 | `get_function_xrefs` | main、offset=0、limit=50 | 2件 |
| 10 | `decompile_function` | main、1関数、timeout=60 | 成功、本文非保存 |
| 11 | `get_function_callees` | main、offset=0、limit=50 | 10件、simple_xorを選定 |
| 12 | `get_function_by_address` | simple_xor | 成功 |
| 13 | `decompile_function` | simple_xor、1関数、timeout=60 | XOR演算を確認、本文非保存 |
| 14 | `get_function_variables` | simple_xor、limit=50 | byte引数2件、Local 2件 |
| 15 | `analyze_control_flow` | simple_xor | Complexity 1、1 Basic Block、Loop 0 |
| 16 | `analyze_dataflow` | simple_xor Entry、k、backward、max_steps=20 | PCode操作なし。迂回せず停止 |

固定Evidenceは`tests/fixtures/evidence/valid-safe-test-pe.json`へ正規化した。

## レポート評価

| モード | 判定 | 根拠分離 | 制約明記 |
|---|---|---|---|
| 外部通信・IOC | `not_found_in_reviewed_scope` | fact／inference／unknown | 済 |
| 挙動 | mainのファイル処理、0x5Aによる単純XOR、Detector誤検知可能性high | fact／inference／unknown | 済 |
| 永続化 | `unknown` | fact／inference／unknown | 済 |
| 不審度 | `assessment_deferred` | fact／inference／unknown | 済 |
| Full | Coverage不足を明示 | fact／inference／unknown | 済 |

期待出力は`tests/expected-reports/`に保存した。静的解析だけで悪性、安全性、通信、永続化を断定していない。

## 評価指標

| 観点 | 実測 |
|---|---|
| 正確性 | 全Findingにfixture内IDまたは取得Toolを付与 |
| Coverage | 5/5モードを生成。未取得領域を`unknown`化 |
| 再現性 | 固定JSON Evidenceと期待Markdownを保存 |
| MCP効率 | 解析16回、契約確認2回、重複0回、各listのlimit=50 |
| 安全性 | 禁止Tool呼出し0、状態変更0、外部IOC照会0 |

## Detector品質上のFinding

- `find_anti_analysis_techniques`は、一般的なCloseHandleを`debugger_detection`、Severity `high`として返した。
- Detector Severityはコード上の利用関係を示さないため、そのまま不審度へ反映すると誤検知につながる。
- `detect_crypto_constants`はCatalogとSchemaには存在するが、実処理は未実装だった。暗号定数またはキーが存在しないという意味ではない。
- 公開Catalogに専用のキー抽出、Entropy、難読化判定Toolは確認できなかった。
- 個別Decompilerでは、simple_xorのXOR演算と、mainから渡される0x5Aをキー候補として確認できた。専用Detectorがなくても、選定関数のCaller／Calleeと疑似コードを要約すれば詳細解析が可能である。
- Control Flowは選定関数の単純さを定量化できた。Dataflowは関数EntryではPCode操作を得られず、必要なInstruction Addressの根拠がないため停止した。

## 確認コマンド

```bash
python3 scripts/validate_repository.py --json
python3 -m unittest discover -s tests -v
```

成功時はvalidatorが`"status": "pass"`を返し、unittestは全件`ok`となる。失敗時は対象ファイルと違反したInvariantが標準エラーへ表示される。

2026-09-02の最終実行結果は、validator `pass`、レポート反復評価`pass`、unittest 14件すべて`ok`だった。
