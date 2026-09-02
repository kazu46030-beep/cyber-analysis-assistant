# GhidraMCP Tool利用方針

## 適用範囲

この表は、確認済みGhidraMCP v7.0.0、Commit `1e0211388d9fc1f85876b69b3343d1bd563c3b85`のTool定義を根拠とする。実行時のTool名とInput Schemaが一致する場合だけ適用する。

記載のないTool、名称やSchemaが異なるToolは`unknown`として使わない。

## 契約確認時だけ使うTool

Program解析やレポート作成では呼び出さず、実MCPとの契約snapshotを更新する検証作業で各1回だけ使う。

| Tool | 用途 | 制約 |
|---|---|---|
| `get_version` | MCP Plugin Versionの確認 | 空の入力だけを使い、応答を契約記録に限定する。 |
| `mcp_schema` | 実CatalogとInput Schemaの確認 | 空の入力だけを使い、検体由来情報として扱わない。 |

## 最初に使うTool

リスト系は`offset`と`limit`を指定し、1回の`limit`は原則100件以下とする。

| Tool | 用途 | 制約 |
|---|---|---|
| `get_metadata` | Programの基本情報 | 最初に1回だけ使う。 |
| `list_imports` | Importの概観 | 全件取得しない。 |
| `list_exports` | Exportの概観 | 全件取得しない。 |
| `list_functions_enhanced` | 関数Metadataの列挙と候補選定 | 1ページ100件以下で必要な範囲までページングする。 |
| `search_functions_enhanced` | 名前、Xref数、Thunk等による候補絞込み | `offset`と100以下の`limit`を指定する。 |

## 必要な時に使うTool

| Tool | 使用条件 | 制約 |
|---|---|---|
| `list_strings` | 確認語を絞れた | `filter`を使い、空Filterで取得しない。 |
| `get_function_by_address` | 対象Addressを選定できた | 選定根拠を残す。 |
| `decompile_function` | 候補関数の理解が必要 | 1関数ずつ`address`で呼ぶ。`functions`は使わない。 |
| `get_function_xrefs` | 関数の参照関係が必要 | `offset`と`limit`を指定する。 |
| `get_xrefs_to` / `get_xrefs_from` | 注目Addressの参照が必要 | `offset`と`limit`を指定する。 |
| `get_function_callers` / `get_function_callees` | 呼出元・呼出先が必要 | `offset`と`limit`を指定する。 |
| `get_function_call_graph` | 少数関数の関係が必要 | 深さを小さく保つ。 |
| `get_function_signature` | 選定関数の引数・戻り値が必要 | 1関数ずつ確認する。 |
| `get_function_variables` | 選定関数の変数が必要 | 100以下の`limit`を指定し、秘密値を出力しない。 |
| `get_function_jump_targets` | 選定関数の分岐先が必要 | `offset`と100以下の`limit`を指定する。 |
| `analyze_control_flow` | 選定関数の複雑度が必要 | 1関数ずつ確認し、難読化の証明にしない。 |
| `analyze_dataflow` | 選定した値の生成元・利用先が必要 | PCode操作を持つ根拠Addressと対象変数を絞り、`max_steps`は100以下にする。関数Entryだけで失敗した場合は迂回しない。 |
| `find_anti_analysis_techniques` | 静的なAnti-analysis兆候が必要 | 実行時挙動の証明にしない。 |
| `detect_crypto_constants` | Crypto定数の確認が必要 | 実装状態を確認し、アルゴリズム、キー、悪性用途を断定しない。 |
| `detect_malware_behaviors` | 静的パターンを補助確認する | 仮説として扱い、個別Evidenceで裏付ける。 |

これらの補助Detectorはヒューリスティックであり、FindingのSeverityをそのまま不審度へ転記しない。一般的API名だけのFindingは、Xrefや選定した関数の疑似コードでコード上の利用関係を確認できるまで低信頼の候補とする。`0件`は不存在の証明にしない。`Not yet implemented`等の実装状態を返した場合は、その分析領域を`unknown`とする。

確認済みCatalogに、専用のキー抽出、Entropy計算、難読化判定Toolはない。選定関数のDecompiler、Caller／Callee、限定Dataflowから、演算、ループ、テーブル参照、呼出側定数を確認する。埋込み変換定数や暗号キー候補は根拠付きで報告できるが、Credential、Token、API Key、Private Key等の秘密値は値を保持・転載しない。暗号定数と暗号キーを同一視せず、実行、Emulation、Memory読取り、全Strings取得へ迂回しない。

## Assemblyの補助利用

Decompilerで間接呼出し、制御フロー、演算幅、定数の由来を判断できない場合だけ、選定した少数関数のAssemblyを候補とする。利用条件は、MnemonicとOperandだけに限定でき、機械語Bytesを返さず、Instruction数または範囲の上限を指定できることである。

現行の`disassemble_function`は取得上限とBytes除外をSchemaで指定できず、`disassemble_bytes`と`search_instructions`はBytesを返すため使用しない。将来Schemaが条件を満たした場合は、契約snapshot、固定Evidence、上限テストを更新してから許可する。

## 使わないTool

- `list_functions`: ページングできないため使わず、同等の列挙は`list_functions_enhanced`で行う。
- `disassemble_function`、`disassemble_bytes`、`search_instructions`、`read_memory`、`inspect_memory_content`、`get_function_pcode`: 機械語Bytes、生データ、または上限なしの過大出力になり得る。
- `get_language_metadata`、`extract_iocs_with_context`、`search_byte_patterns`: 初版では取得範囲を安全に限定しにくい。
- `list_instances`、`connect_instance`、`list_tool_groups`、`load_tool_group`、`unload_tool_group`、`search_tools`、`check_tools`: 接続済み解析では使わない。
- `set_*`、`rename_*`、`create_*`、`delete_*`、`apply_*`、`save_*`、`open_*`、`close_*`: 状態変更のため使わない。
- `import_*`、`export_*`、`load_*`、`restore_*`、`archive_*`、`checkin_*`: File／Project操作のため使わない。
- `run_analysis`、`reanalyze`、`run_ghidra_script`、`run_script_inline`: AnalysisまたはCode実行のため使わない。
- `debugger_*`、`emulate_*`、`oracle_*`: 動的操作のため使わない。

GETであっても、状態を変える、出力が過大、または安全性が不明なら使わない。

## 標準レシピ

- 初期調査: `get_metadata` → `list_imports`／`list_exports` → `list_functions_enhanced`
- 関数調査: `get_function_by_address` → Xref／Caller／Callee → `decompile_function`
- 詳細解析: 選定関数を`decompile_function` → 必要なCalleeを個別追跡 → Control Flow／Dataflowで仮説を確認 → 疑似コードを要約Evidenceへ変換
- 文字列調査: 確認語を決める → `list_strings(filter=...)` → 参照関数を限定確認
