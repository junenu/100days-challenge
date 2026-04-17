# netdiag

ネットワーク診断 CLI ツール。サブネット計算・DNS 検索・ポートスキャン・インターフェース確認を 1 コマンドで行えます。

## ビルド

```bash
make build
```

実行ファイル `netdiag` がカレントディレクトリに生成されます。

### パスを通してどこからでも使えるようにする

```bash
make install
```

`/usr/local/bin/netdiag` にコピーされます。

## 使い方

### subnet — サブネット計算

CIDR からネットワーク情報を計算します。

```bash
./netdiag subnet 192.168.1.0/24
./netdiag subnet 10.0.0.0/8
./netdiag subnet 172.16.0.0/12
```

```
[ Subnet Calculator: 192.168.1.0/24 ]

┌───────────────────┬─────────────────────┐
│ Network Address   │ 192.168.1.0/24      │
│ Subnet Mask       │ 255.255.255.0 (/24) │
│ Broadcast Address │ 192.168.1.255       │
│ First Host        │ 192.168.1.1         │
│ Last Host         │ 192.168.1.254       │
│ Total Hosts       │ 256                 │
│ Usable Hosts      │ 254                 │
│ IP Class          │ C                   │
│ Private Range     │ Yes (RFC1918)       │
└───────────────────┴─────────────────────┘
```

### dns — DNS レコード検索

```bash
# 全レコードを取得
./netdiag dns example.com

# レコードタイプを絞り込む
./netdiag dns example.com --type A,MX,TXT

# 逆引き (PTR)
./netdiag dns 8.8.8.8 --reverse
```

対応レコードタイプ: `A` `AAAA` `MX` `NS` `CNAME` `TXT` `PTR`

### scan — TCP ポートスキャン

```bash
# よく使うポートをスキャン (デフォルト)
./netdiag scan 192.168.1.1

# ポート範囲を指定
./netdiag scan 192.168.1.1 --ports 1-1024

# ポートをカンマ区切りで指定
./netdiag scan 192.168.1.1 --ports 22,80,443,3306

# 既知サービスポートのみ (SSH/HTTP/BGP/SNMP 等)
./netdiag scan 192.168.1.1 --common
```

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `--ports` | スキャン対象ポート | — |
| `--common` | 既知サービスポートのみ | false |
| `--concurrency` | 並列スキャン数 | 100 |
| `--timeout` | 接続タイムアウト (ms) | 500 |

### iface — インターフェース一覧

```bash
./netdiag iface
```

MAC アドレス・フラグ (UP/BROADCAST/LOOPBACK 等)・IPv4/IPv6 アドレスを一覧表示します。

## テスト

```bash
make test
```

## 動作環境

- Go 1.22 以上
