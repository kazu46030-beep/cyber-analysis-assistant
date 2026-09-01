# Cyber Analysis Assistant

Codexと承認済みMCPを使うサイバー解析支援のための、Agentルール、Skill、Tool方針、レポート形式を管理するリポジトリです。

## 構成

```text
SOCアナリスト
    ↓
Codex（主Agent）
    ├─ ghidra-static-analysis Skill → 外部管理のGhidraMCP
    └─ malware-analysis-report Skill
           ↓
       根拠付き回答／目的別Markdownレポート
```

| 場所 | 役割 |
|---|---|
| `AGENTS.md` | 全作業共通の安全・開発ルール |
| `skills/ghidra-static-analysis/` | GhidraMCPのTool制御と限定Evidence収集 |
| `skills/malware-analysis-report/` | 通信・IOC、挙動、永続化、不審度、Fullレポート |
| `docs/architecture.md` | 現行アーキテクチャ |
| `docs/roadmap.md` | Python Helperとサブエージェントの導入順序 |
| `docs/evaluation.md` | 品質・コスト・待ち時間の比較基準 |

MCP Server、Ghidra、FLARE-VM、検体はこのリポジトリへ含めません。

## 開発方針

- 初版は単一の主Agent＋Skillで成立させる。
- Pythonは反復する決定論的処理が確認された場合だけ追加する。
- サブエージェントはMCPを直接呼ばず、限定Evidenceの要約・検証・レポート検査だけを担当する。
- マルウェアかどうかは断定せず、根拠付きの不審度と調査Coverageを報告する。

## ブランチ

- `main`: 安定版
- `development`: 次の統合先
- `feature/*`、`fix/*`、`docs/*`、`test/*`: 個別作業
