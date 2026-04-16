# Day005 — notes-api

## 概要

Go 製のメモ管理 REST API サーバー。外部ライブラリなし、JSON ファイルに永続化。
CRUD + 全文検索をシンプルな HTTP API で提供する。

## 技術スタック

- Language: Go 1.22+
- Framework/Library: 標準ライブラリのみ（`net/http`, `encoding/json`）
- データ永続化: JSON ファイル（`notes.json`）

## 起動方法

```bash
# ビルド
cd day005_notes-api
CGO_ENABLED=0 go build -o notes-api .

# 起動（デフォルト :8080）
./notes-api

# ポート・データファイルを変更する場合
ADDR=:3000 DATA_FILE=my-notes.json ./notes-api
```

## API 一覧

| Method | Path | 説明 |
|--------|------|------|
| GET | `/health` | ヘルスチェック |
| GET | `/notes` | 全メモ一覧 |
| POST | `/notes` | メモ作成 |
| GET | `/notes/{id}` | 1 件取得 |
| PUT | `/notes/{id}` | 更新 |
| DELETE | `/notes/{id}` | 削除（204） |
| GET | `/notes/search?q=` | タイトル・本文・タグ全文検索 |

### リクエスト例

```bash
# メモ作成
curl -X POST http://localhost:8080/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"Go メモ","body":"goroutine の使い方","tags":["go","memo"]}'

# 一覧
curl http://localhost:8080/notes

# 1 件取得
curl http://localhost:8080/notes/1

# 更新
curl -X PUT http://localhost:8080/notes/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Go メモ（更新）","body":"channel も使う","tags":["go","channel"]}'

# 削除
curl -X DELETE http://localhost:8080/notes/1

# 検索
curl "http://localhost:8080/notes/search?q=go"
```

### レスポンス例（POST 201）

```json
{
  "id": 1,
  "title": "Go メモ",
  "body": "goroutine の使い方",
  "tags": ["go", "memo"],
  "created_at": "2026-04-16T05:00:00Z",
  "updated_at": "2026-04-16T05:00:00Z"
}
```

## 機能一覧

### 実装済み

- [x] CRUD（作成・取得・更新・削除）
- [x] 全文検索（タイトル・本文・タグ）
- [x] JSON ファイル永続化
- [x] スレッドセーフ（`sync.RWMutex`）
- [x] 入力バリデーション（title 必須・200 文字以内）
- [x] エラーレスポンス（404 / 400 / 422）
- [x] 環境変数でポート・データファイルを設定可能
- [x] ヘルスチェックエンドポイント

### 今後の改善候補（任意）

- [ ] タグ一覧エンドポイント `GET /tags`
- [ ] ページネーション `?page=&limit=`
- [ ] Markdown 本文のレンダリング

## 開発ログ

### 学んだこと

- Go 標準の `net/http` だけで RESTful ルーティングが実装できる
- `sync.RWMutex` で読み書きを分離するとスループットが上がる
- macOS 15 (Sequoia) + Go 1.22 では `CGO_ENABLED=0` でビルドしないと dyld エラーが出る

### 詰まったこと・解決方法

- `go run` / `go build` で dyld `missing LC_UUID` エラー → `CGO_ENABLED=0 go build` で解決
- `/notes/search` と `/notes/{id}` のルート競合 → `/notes/` ハンドラ内でパスサフィックスを判定して振り分け

### 次回やってみたいこと

- Rust の `axum` で同じ API を実装して比較
- SQLite 永続化バージョン
