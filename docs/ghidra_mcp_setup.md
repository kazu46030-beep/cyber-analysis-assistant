# FLARE-VM + Ghidra + GhidraMCP セットアップメモ

## 目的

FLARE-VM 上に以下の環境を構築する。

- Ghidra 12.1.2
- GhidraMCP
- MCP Bridge
- Host-Only ネットワーク経由でホスト側の Codex / WSL Codex から Ghidra を操作

最終構成：

```text
Host Windows
└─ WSL
   └─ Codex CLI
        │
        │ MCP / Streamable HTTP
        ▼
   FLARE-VM Host-Only IP:8081
        │
        ▼
   MCP Bridge
        │
        │ localhost
        ▼
   127.0.0.1:8089
        │
        ▼
   GhidraMCP Plugin
        │
        ▼
   Ghidra 12.1.2
```

Ghidra 本体の API（8089）は FLARE-VM 内の localhost のみに閉じ、
MCP Bridge の 8081 のみ Host-Only ネットワークへ公開する。

> **注意**
>
> バージョン番号・IPアドレス・パスは固定値として信用せず、セットアップ時点の README / `pom.xml` / `preflight` の結果を正とすること。

## 実行上の境界

- 本書は隔離したFLARE-VMを利用者が構築するための手順であり、Agentが依存導入、Clone、Build、Deploy、ネットワーク変更を自動実行する指示ではない。実行前に利用者の承認を得る。
- GhidraMCPのRelease、Commit、Ghidra対応Versionは配布元で確認する。取得物のHashまたは署名が提供されている場合は照合する。
- `8081`はVMware Host-Only Segmentだけへ公開し、Bridged、NAT、Internet側へ公開しない。`8089`はFLARE-VM内のlocalhostに限定する。
- 設定、コマンド履歴、画面、ログへCredential、Token、API Key、Private Keyを記録しない。
- 本書の`192.0.2.135`はRFC 5737の文書用ダミーアドレスであり、実環境の値ではない。

---

# 1. Java 21 のセットアップ

```powershell
winget install -e --id EclipseAdoptium.Temurin.21.JDK --source winget
java -version
javac -version
```

期待値：

```text
Java 21.x
javac 21.x
```

`msstore` 関連のエラーが出る場合は `--source winget` を付ける。

---

# 2. Ghidra のセットアップ

公式 Release：

https://github.com/NationalSecurityAgency/ghidra/releases

FLARE-VM には Ghidra がプリインストールされている場合があるが、GhidraMCP が要求するバージョンと異なる可能性があるため、既存版を上書きせず別ディレクトリへ展開する。

例：

```text
C:\Tools\
├─ ghidra_old\
└─ ghidra_12.1.2_PUBLIC\
```

今回の環境では Ghidra 12.1.2 を使用。

起動：

```powershell
cd "<GHIDRA_PATH>"
.\ghidraRun.bat
```

`<GHIDRA_PATH>` は `ghidraRun.bat` と `Ghidra\` があるルートディレクトリ。

---

# 3. Python の確認

```powershell
python --version
```

Python 3.10+ を使用。

---

# 4. Apache Maven のセットアップ

```powershell
choco install maven -y
refreshenv
mvn --version
```

期待値：

```text
Apache Maven 3.9.x
Java version: 21.x
```

Maven が Java 21 を使用していることを確認する。

---

# 5. uv のセットアップ

```powershell
uv --version
```

無い場合：

```powershell
python -m pip install uv
```

確認：

```powershell
where uv
uv --version
```

`Requirement already satisfied` と表示されても `uv.exe` が PATH に無い場合があるので注意。

---

# 6. GhidraMCP の取得

今回使用する GhidraMCP は `tools.setup` / `bridge-mcp-ghidra` を使う構成。

```powershell
git clone https://github.com/bethington/ghidra-mcp.git
cd ghidra-mcp
git remote -v
```

---

# 7. Preflight

```powershell
python -m tools.setup preflight --ghidra-path "<GHIDRA_PATH>"
```

例：

```powershell
python -m tools.setup preflight --ghidra-path "C:\Tools\ghidra_12.1.2_PUBLIC"
```

成功例：

```text
Python: ...
Maven: ...
uv: available
Java: available on PATH
Project version: 7.0.0
Ghidra version from pom.xml: 12.1.2
Ghidra version from path: 12.1.2
Preflight checks passed.
```

`pom.xml` の Ghidra バージョンと指定した Ghidra のバージョンが一致していること。

---

# 8. 依存関係セットアップ

```powershell
python -m tools.setup ensure-prereqs --ghidra-path "<GHIDRA_PATH>"
```

---

# 9. ビルド

```powershell
python -m tools.setup build
```

---

# 10. Deploy

```powershell
python -m tools.setup deploy --ghidra-path "<GHIDRA_PATH>"
```

初回 Deploy 時に Ghidra が起動中だと、MCP がまだ無いため `WinError 10061 / Connection refused` が出ることがある。

その場合：

1. Ghidra の作業内容を保存
2. Ghidra を完全終了
3. Deploy を再実行

---

# 11. GhidraMCP Plugin の確認

Ghidra で CodeBrowser を開く。

正常時の例：

```text
GhidraMCP Server Status

UDS: Running
TCP: Running (port 8089)
Strict naming enforcement: true
Version: 7.0.0
Endpoints: 239
```

---

# 12. GhidraMCP API の確認

FLARE-VM 内で実施。

```powershell
curl http://127.0.0.1:8089/check_connection
curl http://127.0.0.1:8089/get_version
netstat -ano | findstr :8089
```

理想：

```text
127.0.0.1:8089    LISTENING
```

Ghidra API は localhost のみに bind しておく。

---

# 13. Host-Only へ変更

Ghidra / GhidraMCP のセットアップが完了したら VMware のネットワークを Host-Only に変更。

切り替え前 Snapshot 例：

```text
FLARE-GhidraMCP-installed-pre-hostonly
```

切り替え後、疎通確認まで完了したら：

```text
FLARE-GhidraMCP-hostonly-baseline
```

---

# 14. Host-Only IP の確認

FLARE-VM：

```powershell
ipconfig
```

以下では Host-Only IP を `<FLARE_HOST_ONLY_IP>` とする。

IP が変わると Codex の MCP URL も変わるため、必要に応じて固定IP化する。

---

# 15. MCP Bridge を Host-Only に公開

GhidraMCP の生 API（8089）は localhost のままにし、MCP Bridge のみ Host-Only 側へ公開する。

```powershell
cd "<GHIDRA_MCP_PATH>"

uv run bridge-mcp-ghidra --transport streamable-http --mcp-host <FLARE_HOST_ONLY_IP> --mcp-port 8081
```

例：

```powershell
uv run bridge-mcp-ghidra --transport streamable-http --mcp-host 192.0.2.135 --mcp-port 8081
```

成功例：

```text
Auto-connecting via TCP (http://127.0.0.1:8089) to ghidra
Auto-registered 238 tools from ghidra
Starting MCP bridge (streamable-http)
MCP endpoint: http://192.0.2.135:8081/mcp
```

確認：

```powershell
netstat -ano | findstr :8081
```

---

# 16. ホスト Windows から疎通確認

```powershell
Test-NetConnection <FLARE_HOST_ONLY_IP> -Port 8081
```

成功：

```text
TcpTestSucceeded : True
```

---

# 17. WSL から疎通確認

```bash
nc -vz <FLARE_HOST_ONLY_IP> 8081
```

または：

```bash
curl -v http://<FLARE_HOST_ONLY_IP>:8081/mcp
```

HTTP エラーでも Connection Refused / Timeout でなければネットワーク経路は到達している。

---

# 18. WSL Codex に MCP を登録

```bash
codex mcp add ghidra-flare --url http://<FLARE_HOST_ONLY_IP>:8081/mcp
codex mcp list
```

例：

```bash
codex mcp add ghidra-flare --url http://192.0.2.135:8081/mcp
```

WSL 側では `~/.codex/config.toml` に保存される。

Windows 版 Codex と WSL 版 Codex の設定は別なので注意。

---

# 19. Codex → Ghidra 疎通テスト

Ghidra で解析対象を CodeBrowser で開いた状態で Codex に入力。

```text
Ghidra MCPを使用して、
現在開いているプログラム名と
Ghidraのバージョンを確認してください。
```

Ghidra から実際のプログラム名・バージョンが返れば以下まで疎通成功。

```text
WSL Codex
    ↓
Host-Only
    ↓
MCP Bridge :8081
    ↓
GhidraMCP :8089
    ↓
Ghidra
```

---

# 20. Bridge 起動を BAT 化

`Start-GhidraMCP-Bridge.bat` を作成。

```bat
@echo off

cd /d "<GHIDRA_MCP_PATH>"

uv run bridge-mcp-ghidra ^
  --transport streamable-http ^
  --mcp-host <FLARE_HOST_ONLY_IP> ^
  --mcp-port 8081

pause
```

これにより毎回長いコマンドを手入力する必要がなくなる。

---

# 21. 通常利用時の起動フロー

```text
1. FLARE-VM 起動
2. Ghidra 起動
3. 解析対象を CodeBrowser で開く
4. Start-GhidraMCP-Bridge.bat を起動
5. WSL で Codex 起動
6. Codex から Ghidra MCP を利用
```

Codex の MCP 登録は初回のみ。

---

# 22. 推奨ネットワーク構成

```text
Internet
   │
   ▼
Host Windows
   │
   ├── WSL
   │    └── Codex
   │
   │ VMware Host-Only
   ▼
FLARE-VM
   │
   ├── MCP Bridge
   │    <Host-Only IP>:8081
   │
   └── GhidraMCP
        127.0.0.1:8089
             │
             ▼
           Ghidra
```

ポイント：

- FLARE-VM は Internet に直接接続しない
- Ghidra API :8089 は localhost のみ
- MCP Bridge :8081 のみ Host-Only へ公開
- AI / Codex はホストまたは WSL 側で動作
- マルウェア解析環境と AI クライアントを分離する

---

# 23. Snapshot 推奨ポイント

## Snapshot 1

GhidraMCP セットアップ完了・Host-Only変更前。

```text
FLARE-GhidraMCP-installed-pre-hostonly
```

## Snapshot 2

以下が全て成功した状態。

```text
Host-Only
Ghidra
GhidraMCP
Bridge
Host / WSL → Bridge
Codex → Ghidra
```

例：

```text
FLARE-GhidraMCP-hostonly-baseline
```

通常はこちらを解析開始時のベースラインとして利用する。

---

# 24. トラブルシューティング

## Maven が見つからない

```text
Unable to locate Maven
```

```powershell
choco install maven -y
refreshenv
mvn --version
```

## uv が見つからない

```powershell
where uv
uv --version
```

## Ghidra Version mismatch

`Ghidra version from pom.xml` と `Ghidra version from path` が一致しているか確認する。

FLARE プリインストール版と新規導入版を混同しないこと。

## Project is Locked

別 Ghidra が同じ Project を開いていないか確認する。

## Bridge に接続できない

FLARE：

```powershell
netstat -ano | findstr :8081
```

Host：

```powershell
Test-NetConnection <FLARE_HOST_ONLY_IP> -Port 8081
```

## GhidraMCP に接続できない

```powershell
curl http://127.0.0.1:8089/check_connection
curl http://127.0.0.1:8089/get_version
```

---

# 25. セットアップ確認チェックリスト

```text
[ ] Java 21
[ ] javac 21
[ ] Python 3.10+
[ ] Maven 3.9+
[ ] uv
[ ] 対応バージョンの Ghidra
[ ] Ghidra単体起動
[ ] GhidraMCP preflight
[ ] ensure-prereqs
[ ] build
[ ] deploy
[ ] GhidraMCP Plugin Running
[ ] 127.0.0.1:8089 LISTENING
[ ] /check_connection 成功
[ ] /get_version 成功
[ ] Host-Only 化
[ ] Bridge :8081 起動
[ ] Host → FLARE :8081 疎通
[ ] WSL → FLARE :8081 疎通
[ ] Codex MCP 登録
[ ] Codex → Ghidra 疎通
[ ] Snapshot 作成
```
