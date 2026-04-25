# day014 — Py Share Server

Python 標準ライブラリだけで動く、ローカルファイル共有用の簡易 Web サーバー。
指定したディレクトリをブラウザから閲覧・ダウンロードでき、アクセスログとヘルスチェックも備えています。

## 機能

- 指定ディレクトリの静的ファイル配信
- ブラウザ向けのディレクトリ一覧表示
- `GET /healthz` によるヘルスチェック
- `HEAD` リクエスト対応
- アクセスログ出力
- `..` を使った共有ルート外アクセスの防止
- 隠しファイルを標準では非表示、`--show-hidden` で表示

## 使い方

```bash
# サンプルディレクトリを配信
python3 share_server.py public

# ポートを指定
python3 share_server.py public --port 9000

# LAN からアクセスできるように待ち受け
python3 share_server.py public --host 0.0.0.0 --port 8014

# 隠しファイルも一覧に表示
python3 share_server.py public --show-hidden
```

起動後、ブラウザで `http://127.0.0.1:8014/` を開きます。

## 動作確認

```bash
# ヘルスチェック
curl http://127.0.0.1:8014/healthz

# サンプルファイル取得
curl http://127.0.0.1:8014/hello.txt
```

## テスト

```bash
python3 -m unittest -v test_share_server.py
```

## 技術スタック

- Python 3.12
- 標準ライブラリのみ
  - `http.server`
  - `pathlib`
  - `argparse`
  - `mimetypes`

## 開発ログ

### 学んだこと

- `BaseHTTPRequestHandler` を継承すると、HTTP メソッドごとに処理を小さく分けられる
- ファイルサーバーではパス正規化と `Path.relative_to()` によるルート外アクセス防止が重要

### 詰まったこと・解決方法

- URL パスの `..` やクエリ文字列をそのまま扱うと危険なので、`urllib.parse` と `posixpath.normpath` で正規化してから実ファイルへ解決した

### 次回やってみたいこと

- 簡易アップロード機能
- Basic 認証
- QR コードで共有 URL を表示
