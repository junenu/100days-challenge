# day032 — netwatch

Python + PostgreSQL + Docker Compose で作るネットワーク監視 CLI。

ping / traceroute の結果を PostgreSQL に記録し、可用性レポートを表示する。

## 技術スタック

| 要素 | 採用技術 |
|------|---------|
| 言語 | Python 3.11+ |
| DB | PostgreSQL 16 (Docker Compose) |
| DB ドライバ | psycopg2-binary |
| CLI 表示 | Rich |
| NW 操作 | ping / traceroute (OS コマンド) |

## セットアップ

```bash
# 1. DB 起動
docker compose up -d

# 2. 依存パッケージインストール
pip install -r requirements.txt

# 3. 環境変数 (デフォルトのままでも動作)
cp .env.example .env
```

## 使い方

```bash
# ホスト登録
python -m netwatch.main add 8.8.8.8 --name "Google DNS"
python -m netwatch.main add 1.1.1.1 --name "Cloudflare DNS"
python -m netwatch.main add example.com

# ホスト一覧
python -m netwatch.main list

# ping 実行 (結果を DB に保存)
python -m netwatch.main ping 8.8.8.8
python -m netwatch.main ping all --count 5

# 定期監視 (60 秒ごとに全ホストへ ping)
python -m netwatch.main watch --interval 60

# 可用性レポート
python -m netwatch.main report
python -m netwatch.main report 8.8.8.8 --limit 50

# traceroute
python -m netwatch.main trace 8.8.8.8

# ホスト削除
python -m netwatch.main remove example.com
```

## DB スキーマ

```
hosts            — 監視対象ホスト
ping_results     — ping 実行結果 (RTT, 成否)
traceroute_hops  — traceroute のホップ情報
```

## デモ

```
$ python -m netwatch.main ping all
  8.8.8.8         OK    RTT: 3.45 ms
  1.1.1.1         OK    RTT: 2.12 ms
  example.com     OK    RTT: 10.87 ms

$ python -m netwatch.main report 8.8.8.8

Google DNS (8.8.8.8)  可用性: 100.0%  (20/20)
  RTT — avg: 3.52 ms  min: 2.89 ms  max: 5.11 ms
```
