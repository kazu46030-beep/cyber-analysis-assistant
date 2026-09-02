# Full静的解析レポート（期待出力）

## 1. エグゼクティブサマリー

限定された静的Evidenceから、mainによるファイル作成・書込み・Handle終了と、0x5Aをキー候補とする単純XOR変換を確認した。Anti-analysis DetectorのCloseHandle high候補は、Decompiler上の通常Handle処理と整合せず誤検知の可能性が高い。通信、永続化、標準暗号等はCoverage不足であり、不審度は`assessment_deferred`とする。

## 2. 対象と解析範囲

- 対象: `safe-test-pe`（ユーザー作成の無害なWindows PE、識別子除去済み）
- 取得: Metadata、Imports 19件、Exports 29件、Functions一覧32件
- 詳細確認: mainのXref／Callee、mainとsimple_xorの個別Decompiler
- 非取得: 全Strings、全関数疑似コード、バイト列、全逆アセンブル

## 3. 不審度と判定上の制約

総合判定は`assessment_deferred`。主要6軸のコード関係が未確認で、合計値を確定できない。ファイルAPIは一般的な正当用途を持つ。

## 4. 外部通信・IOC候補

- `fact`: 確認した19件のImportに通信関連APIなし（F-003、`list_imports`）。
- `inference`: 確認範囲内では通信機能を支持するEvidenceが弱い。
- `unknown`: Endpoint、動的API解決、実行時通信（U-001）。
- IOC候補: なし。外部照会は実施していない。

## 5. 挙動まとめ

- `fact`: CreateFileA、WriteFile、CloseHandleをImport（F-001）。
- `fact`: main内のファイル作成・書込み・Handle終了（F-006）。
- `fact`: simple_xorのXOR演算と呼出側定数0x5A（F-007）。
- `inference`: 0x5Aは単純XORキー候補であり、Credentialまたは標準暗号の証明ではない（I-003）。
- `unknown`: Process、Registry、Service、Task、Discovery、Crypto等のコード利用関係。

## 6. 永続化

判定は`unknown`。永続化に関するStrings、Xref、疑似コードを確認しておらず、不存在または成功を断定しない（U-002）。

## 7. 難読化・Packing・Anti-analysisの兆候

- `fact`: Detectorがmain内のCloseHandleをdebugger-detection／high候補として1件出力（F-004、`find_anti_analysis_techniques`）。
- `inference`: main疑似コードではCloseHandleが通常ファイルHandleの終了に使われ、Detector誤検知の可能性が高い（I-002）。
- `unknown`: main以外のAnti-debug処理（U-003）。
- `unknown`: `detect_crypto_constants`は未実装状態を返し、暗号定数・アルゴリズム・キー候補を評価できない（U-004）。

## 8. 注目関数

- main: File APIとsimple_xorの呼出元。Xref 2件、Callee 10件を限定確認。
- simple_xor: XOR演算を行う選定Callee。byte引数2個、Complexity 1、1 Basic Block、Loopなし。呼出側のキー候補は0x5A。
- 疑似コード本文とAddressはレポートへ保存していない。

## 9. Findings一覧

| ID | 分類 | Finding | 根拠 | 信頼度 |
|---|---|---|---|---|
| F-001 | `fact` | ファイル関連APIをImport | `list_imports`、offset=0、limit=50 | high（Import存在について） |
| F-002 | `fact` | 一般的なRuntime APIをImport | `list_imports`、offset=0、limit=50 | high（Import存在について） |
| F-003 | `fact` | 確認Import内に通信APIなし | `list_imports`、19件 | high（確認範囲について） |
| I-001 | `inference` | ファイル作成・書込み能力候補 | F-001 | low |
| U-001 | `unknown` | 通信とEndpoint | 未取得 | N/A |
| U-002 | `unknown` | 永続化 | 未取得 | N/A |
| U-003 | `unknown` | Anti-analysis | 未取得 | N/A |
| F-004 | `fact` | DetectorがCloseHandleをhigh候補化 | `find_anti_analysis_techniques` | high（Detector出力について） |
| I-002 | `inference` | Detector誤検知の可能性 | F-001、F-004 | medium |
| U-004 | `unknown` | 暗号定数・キー候補 | `detect_crypto_constants`未実装 | N/A |
| F-005 | `fact` | Malware behavior Detectorは0件 | `detect_malware_behaviors` | high（Detector出力について） |
| F-006 | `fact` | mainのファイルHandle処理 | `decompile_function` | high（静的コードについて） |
| F-007 | `fact` | simple_xorと呼出側0x5A | `decompile_function` | high（静的コードについて） |
| I-003 | `inference` | 0x5Aは単純XORキー候補 | F-007 | high |
| F-008 | `fact` | simple_xorは低複雑度の単純変換 | `get_function_variables`、`analyze_control_flow` | high |
| U-005 | `unknown` | kの詳細Dataflow | `analyze_dataflow`はEntryにPCodeなし | N/A |

## 10. 未確認事項と追加調査候補

必要性が生じた場合のみ、確認語を限定した`list_strings`、根拠AddressのXref、選定した1関数の`decompile_function`を主Agentが直列実行する。

## 11. 利用Toolと取得範囲

| Tool | 範囲 |
|---|---|
| `get_metadata` | 現在Program、1回 |
| `list_imports` | offset=0、limit=50、19件 |
| `list_exports` | offset=0、limit=50、29件 |
| `list_functions_enhanced` | offset=0、limit=50、32件 |
| `find_anti_analysis_techniques` | 現在Program、1件 |
| `detect_crypto_constants` | 現在Program、未実装応答 |
| `detect_malware_behaviors` | 現在Program、0件 |
| `get_function_by_address` | main、simple_xorの2関数 |
| `get_function_xrefs` | main、offset=0、limit=50、2件 |
| `get_function_callees` | main、offset=0、limit=50、10件 |
| `decompile_function` | main、simple_xorを個別取得。本文非保存 |
| `get_function_variables` | simple_xor、limit=50、4件 |
| `analyze_control_flow` | simple_xor、1関数 |
| `analyze_dataflow` | simple_xor Entry、k、backward、max_steps=20。PCodeなしで停止 |

## 12. 静的解析の制約

> 本レポートは静的解析で確認できた範囲に限定される。検体を実行していないため、実行時挙動、通信の成立、永続化の成功、条件分岐後の動作および環境依存動作を確認したものではない。
