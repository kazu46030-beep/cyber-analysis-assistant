# Behavior — Run 03

## fact

- mainはCreateFileA→WriteFile→CloseHandleを扱う（F-006、`decompile_function`）。
- mainはsimple_xorへ0x5Aを渡し、CalleeはXOR演算を行う（F-007）。
- simple_xorは2 byte引数、Complexity 1、1 Block、Loop 0（F-008、`analyze_control_flow`）。
- DetectorはCloseHandleをAnti-debug highとした（F-004）。

## inference

- 0x5Aは単純XORキー候補（I-003）。
- Detector判定はmainの通常Handle処理と整合せず、誤検知可能性が高い（I-002）。

## unknown

- 標準暗号・暗号キー（U-004）
- 詳細Dataflow（U-005）

静的解析だけでは実行時挙動を断定しない。根拠Toolは`list_imports`、`decompile_function`、`get_function_variables`、`analyze_control_flow`。
