# Suspicion Assessment — Run 03

- 総合: `assessment_deferred`
- `fact`: F-004、F-006、F-007、F-008
- `inference`: Detector誤検知候補I-002、XORキー候補I-003
- `unknown`: 通信U-001、永続化U-002、標準暗号U-004、Dataflow U-005
- 根拠: `list_imports`、`decompile_function`、`analyze_control_flow`
- 調査Coverage: mainとsimple_xor中心。他関数とStringsは未網羅

静的解析による優先度評価であり、悪性または安全性を断定しない。
