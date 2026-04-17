# Day 006 - netdiag

ネットワーク診断 CLI ツール。

## 概要

`netdiag` は Linux コマンドライン文化に沿った操作感で、よく使うネットワーク調査タスクを 1 本にまとめたツールです。

## コマンド一覧

### `subnet` — CIDR サブネット計算

```
netdiag subnet 192.168.1.0/24
netdiag subnet 10.0.0.0/8
```

- ネットワークアドレス・サブネットマスク・ブロードキャストアドレス
- ホスト範囲 (First / Last)・有効ホスト数
- IP クラス (A/B/C/D/E) と RFC1918 プライベート判定

### `dns` — DNS レコード検索

```
netdiag dns example.com
netdiag dns example.com --type A,MX,TXT
netdiag dns 8.8.8.8 --reverse
```

- A / AAAA / MX / NS / CNAME / TXT / PTR に対応
- `--reverse` フラグで逆引き (PTR)
- クエリ応答時間を表示

### `scan` — TCP ポートスキャン

```
netdiag scan 192.168.1.1
netdiag scan 192.168.1.1 --ports 1-1024
netdiag scan 10.0.0.1 --ports 22,80,443,3306
netdiag scan 192.168.1.1 --common
```

- Goroutine による並列スキャン (デフォルト 100 並列)
- ネットワークエンジニアがよく使うポートにサービス名を自動付与 (SSH/RDP/BGP/SNMP 等)
- `--common` フラグで既知サービスポートのみスキャン

### `iface` — インターフェース一覧

```
netdiag iface
```

- ホスト上の全ネットワークインターフェースを表示
- MAC アドレス・フラグ (UP/BROADCAST/LOOPBACK 等)・IPv4/IPv6 アドレス

## ディレクトリ構成

```
day006_netdiag/
├── main.go
├── cmd/
│   ├── root.go      # cobra ルートコマンド
│   ├── subnet.go    # subnet サブコマンド
│   ├── dns.go       # dns サブコマンド
│   ├── scan.go      # scan サブコマンド
│   └── iface.go     # iface サブコマンド
└── internal/
    ├── subnet/
    │   ├── calculator.go       # CIDR 計算ロジック
    │   └── calculator_test.go
    ├── dns/
    │   └── lookup.go           # DNS 検索ロジック
    ├── scanner/
    │   ├── port.go             # TCP ポートスキャナー
    │   └── port_test.go
    └── iface/
        └── info.go             # インターフェース情報取得
```

## 技術的なポイント

- **Go 標準ライブラリのみでネットワーク処理** — `net` パッケージで DNS 解決・TCP 接続・インターフェース取得
- **並列スキャン** — Goroutine + semaphore パターンで最大同時接続数を制御
- **CGO_ENABLED=0** — macOS の dyld 問題を回避しつつポータブルなバイナリを生成
- **cobra** — サブコマンド構造・フラグ・ヘルプを自動管理

## ビルド・実行

```bash
# ビルド
CGO_ENABLED=0 go build -o netdiag .

# テスト
CGO_ENABLED=0 go test ./internal/subnet/... ./internal/scanner/...

# インストール
make install
```
