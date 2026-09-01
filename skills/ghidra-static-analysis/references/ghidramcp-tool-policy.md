# GhidraMCP Tool利用方針

## 適用範囲

この表は、確認済みGhidraMCP v7.0.0、Commit `1e0211388d9fc1f85876b69b3343d1bd563c3b85`のTool定義を根拠とする。実行時のTool名とInput Schemaが一致する場合だけ適用する。

記載のないTool、名称やSchemaが異なるToolは`unknown`として使わない。

## 最初に使うTool

リスト系は`offset`と`limit`を指定し、1回の`limit`は原則100件以下とする。

| Tool | 用途 | 制約 |
|---|---|---|
| `get_metadata` | Programの基本情報 | 最初に1回だけ使う。 |
| `list_imports` | Importの概観 | 全件取得しない。 |
| `list_exports` | Exportの概観 | 全件取得しない。 |
| `list_functions_enhanced` | 候補関数の選定 | 必要なページだけ確認する。 |

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
| `find_anti_analysis_techniques` | 静的なAnti-analysis兆候が必要 | 実行時挙動の証明にしない。 |
| `detect_crypto_constants` | Crypto定数の確認が必要 | アルゴリズムや悪性用途を断定しない。 |
| `detect_malware_behaviors` | 静的パターンを補助確認する | 仮説として扱い、個別Evidenceで裏付ける。 |

## 使わないTool

- `list_functions`: ページングできないため使わない。
- `disassemble_function`、`disassemble_bytes`、`read_memory`、`inspect_memory_content`、`get_function_pcode`: 生データまたは過大出力になり得る。
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
- 文字列調査: 確認語を決める → `list_strings(filter=...)` → 参照関数を限定確認
