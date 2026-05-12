# Day031 — booklog

## 概要

PostgreSQL + Docker Compose をバックエンドにした読書ログ管理 CLI。
本の追加・一覧・評価・統計を psycopg2 経由で操作する。

## 技術スタック

- Language: Python 3.11+
- Library: psycopg2-binary, python-dotenv
- DB: PostgreSQL 16 (Docker Compose)

## 起動方法

```bash
# 1. 環境変数ファイルを作成
cp .env.example .env

# 2. PostgreSQL を起動
docker compose up -d

# 3. 依存パッケージをインストール
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 4. 実行（初回起動時に自動マイグレーション）
python -m booklog --help
```

## 機能一覧

### 実装済み

- [x] 本の追加 (`add`)
- [x] 一覧表示・絞り込み (`list --status / --genre`)
- [x] 詳細表示 (`show <id>`)
- [x] 評価・メモ・状態更新 (`review <id>`)
- [x] 削除 (`delete <id>`)
- [x] 読書統計 (`stats`)
- [x] 自動マイグレーション（初回起動時に `books` テーブル作成）
- [x] パラメータ化クエリ（SQL インジェクション防止）

### 使用例

```bash
# 本を追加
python -m booklog add "SQLアンチパターン" "Bill Karwin" --genre tech --pages 328 --status reading

# 一覧
python -m booklog list
python -m booklog list --status read

# 読了・評価
python -m booklog review 1 --status read --rating 5 --notes "DB設計のバイブル"

# 統計
python -m booklog stats

# 削除
python -m booklog delete 1
```

## 開発ログ

### 学んだこと

- `psycopg2.extras.RealDictCursor` でカラム名付き辞書として取得できる
- Docker Compose の `healthcheck` で DB の準備完了を待てる
- `dataclass(frozen=True)` でイミュータブルなモデルを定義

### 詰まったこと・解決方法

- `RETURNING` 句で INSERT/UPDATE/DELETE 直後に値を取得できる
- パラメータ化クエリで `ILIKE %s` を使う場合は `f"%{value}%"` をパラメータとして渡す

### 次回やってみたいこと

- CSV インポート機能
- ISBN 検索 API 連携（書誌情報自動取得）
