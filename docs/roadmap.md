# Roadmap

## 現在地

- Phase 0は、GhidraMCP 7.0.0のVersion、実Catalog、Input Schema、Tool分類、無害PEでの接続確認まで完了した。
- Phase 1は、無害PE 1件でDecompiler中心の限定Evidence収集、5種の期待レポート、正常系・異常系テストまで完了した。次は通信、永続化、暗号・難読化等の評価ケースを増やす。
- 実測結果は[Safe Test PE検証結果](evaluations/2026-09-02-safe-test-pe.md)を参照する。

## Phase 0: 契約確認

- 実MCPの配布元、Version、Tool Catalog、Input Schemaを記録する。
- Toolを「最初に使う」「必要な時に使う」「使わない」へ分類する。
- 無害なテスト対象で接続と取得量を確認する。

## Phase 1: 単一Agent

- Ghidra静的解析Skillで限定Evidenceを取得する。
- 目的別レポートSkillで通信・IOC、挙動、永続化、不審度、Fullを生成する。
- 代表的な無害PEで品質と再現性を評価する。

## Phase 2: Python Helper

- 実利用で反復が確認されたSchema検証、正規化、重複排除、差分比較、Markdown／JSON変換だけを実装する。
- 依存追加前に標準ライブラリでの代替を検討する。

## Phase 3: サブエージェント

- 関数要約、Finding検証、レポート検査を候補とする。
- 主AgentだけがMCPを呼び、サブエージェントには限定Evidenceだけを渡す。
- 単一Agentより品質または効率が改善した役割だけ残す。

## 将来候補

- Packing／難読化・Anti-analysis分析
- MITRE ATT&CK候補マッピング
- Evidence Coverage検査
- YARA／Sigma等の検知ルール案
- 複数MCPの個別Policyと統合レポート
