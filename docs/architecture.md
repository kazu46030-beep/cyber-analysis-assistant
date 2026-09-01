# アーキテクチャ

## 責務

```text
主Agent
├─ 利用者との対話
├─ MCP Toolの選択と直列呼び出し
├─ Evidenceの限定・整理
├─ fact / inference / unknownの分類
└─ レポートSkillへの引き渡し

レポートSkill
├─ 外部通信・IOC
├─ 挙動
├─ 永続化
├─ 不審度
└─ Fullレポート
```

GhidraMCPは外部管理の接続先であり、このリポジトリはGhidraMCPやGhidraをラップしない。

## Python Helperの判断基準

次の条件を満たす処理だけPython化する。

- 同じ変換または検証を繰り返している。
- AIの自由度より決定論性が重要である。
- 入出力を限定Schemaで定義できる。
- AIやMCPが停止しても単体テストできる。

常駐オーケストレーター、独自AI Provider、検体を直接読むCollectorは初版対象外とする。
