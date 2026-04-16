# コード解説 — notes-api

## 全体構造の俯瞰

```
main.go            ← エントリポイント。起動・配線
store/store.go     ← データ層。メモリ管理 + JSON 永続化
handler/handler.go ← HTTP 層。ルーティング + リクエスト処理
```

3 つのファイルが「**役割**」で分かれています。HTTP のことは handler しか知らない。ファイル保存のことは store しか知らない。main はその 2 つをつなぐだけ。これを **関心の分離** と呼びます。

---

## main.go — 起動と配線

```go
func main() {
    dataFile := envOr("DATA_FILE", "notes.json")  // (1)
    addr     := envOr("ADDR", ":8080")

    s := store.New(dataFile)    // (2)
    if err := s.Load(); err != nil {
        log.Fatalf("store load: %v", err)
    }

    mux := handler.NewMux(s)   // (3)

    log.Printf("notes-api listening on %s", addr)
    if err := http.ListenAndServe(addr, mux); err != nil {  // (4)
        log.Fatalf("server: %v", err)
    }
}
```

**(1) envOr** — 環境変数があればそれを使い、なければデフォルト値を返すユーティリティ。`ADDR=:3000 ./notes-api` のように起動時に差し替えられる。

**(2) store.New + Load** — Store を作ってから `Load()` で既存データをファイルから読み込む。この順番が重要で、起動するたびに前回のデータが復元される。

**(3) handler.NewMux(s)** — `*store.Store` を handler に渡している。`s` は**ポインタ**なので、handler が store のメソッドを呼ぶたびに同じ 1 つのデータが操作される（コピーではない）。

**(4) http.ListenAndServe** — TCP ソケットを開いてリクエストを待ち続けるブロッキング関数。正常終了はないので、返ってきたら必ずエラー。`log.Fatalf` でエラーを出力してプロセスを終了する。

---

## store/store.go — データ層

### 型定義

```go
type Note struct {
    ID        int      `json:"id"`
    Title     string   `json:"title"`
    Body      string   `json:"body"`
    Tags      []string `json:"tags"`
    CreatedAt string   `json:"created_at"`
    UpdatedAt string   `json:"updated_at"`
}
```

**バッククォートで囲まれた部分**（`json:"id"` など）は **struct タグ**。`json.Marshal` / `json.Unmarshal` が「Go の `ID` フィールド ↔ JSON の `"id"` キー」という変換ルールを知るための注釈。タグがないと Go の名前そのまま（`"ID"`, `"Title"`）になる。

```go
type Store struct {
    mu       sync.RWMutex  // (A)
    notes    []Note        // (B)
    nextID   int           // (C)
    dataFile string        // (D)
}
```

**(A) sync.RWMutex** — 複数の HTTP リクエストが同時に来ても壊れないようにするための**排他ロック**。`RLock`（読み取り専用ロック）は複数ゴルーチンが同時に取れる。`Lock`（書き込みロック）は 1 つしか取れず、他の全アクセスをブロックする。

**(B) notes** — メモを全件メモリに持つスライス。ファイル I/O は書き込み時のみ発生する（読み取りは常にメモリから）ので高速。

**(C) nextID** — 単調増加の ID カウンタ。削除しても ID が再利用されないため、古いデータとの混同を防ぐ。

**(D) dataFile** — どのファイルに保存するかのパス。`New()` で注入するので、テスト時に別ファイルを使うことが容易。

---

### 永続化

```go
type fileData struct {
    NextID int    `json:"next_id"`
    Notes  []Note `json:"notes"`
}
```

ファイルに書く JSON の形を表すプライベート型。`notes.json` の実際の中身はこの構造になっている：

```json
{
  "next_id": 4,
  "notes": [ { "id": 1, ... }, { "id": 2, ... } ]
}
```

`nextID` もファイルに保存しているのがポイント。保存しないと再起動後に ID が 1 から始まり直して重複する。

```go
func (s *Store) Load() error {
    s.mu.Lock()
    defer s.mu.Unlock()          // (E)

    data, err := os.ReadFile(s.dataFile)
    if errors.Is(err, os.ErrNotExist) {
        return nil               // (F)
    }
    ...
}
```

**(E) defer** — 関数が `return` で終わるときに必ず実行される。ロックを取った後どのパスで返っても必ず解放される保証。手動 `Unlock()` を忘れるバグを防ぐ Go の重要イディオム。

**(F) ErrNotExist の無視** — ファイルが初回起動時は存在しない。エラーではなく「空の状態」として扱い `nil` を返す。`errors.Is` で比較する理由は、`os.ReadFile` が内部でエラーをラップすることがあるため（`==` では比較できないケースがある）。

```go
func (s *Store) save() error {
    fd := fileData{NextID: s.nextID, Notes: s.notes}
    data, err := json.MarshalIndent(fd, "", "  ")  // (G)
    ...
    return os.WriteFile(s.dataFile, data, 0o644)   // (H)
}
```

**(G) MarshalIndent** — 普通の `Marshal` と違い、インデント付きの人間が読める JSON を生成する。`notes.json` を直接エディタで編集できるメリットがある。

**(H) 0o644** — ファイルのパーミッション（8 進数）。所有者は読み書き可、グループ・他者は読み取りのみ。

---

### CRUD 操作

#### List — 読み取り

```go
func (s *Store) List() []Note {
    s.mu.RLock()
    defer s.mu.RUnlock()
    result := make([]Note, len(s.notes))
    copy(result, s.notes)   // (I)
    return result
}
```

**(I) copy で防御コピー** — `s.notes` を直接返すと、呼び出し元が返却されたスライスの要素を書き換えたとき Store 内部のデータが壊れる可能性がある。コピーして返すことで Store の内部状態を保護している。

#### Create — 書き込み

```go
func (s *Store) Create(title, body string, tags []string) (Note, error) {
    s.mu.Lock()        // 書き込みロック（RLock より厳しい）
    defer s.mu.Unlock()

    now := time.Now().UTC().Format(time.RFC3339)  // (J)
    n := Note{ID: s.nextID, ...}
    s.nextID++
    s.notes = append(s.notes, n)
    return n, s.save()  // (K)
}
```

**(J) UTC + RFC3339** — タイムゾーンを統一して保存。`RFC3339` は `2026-04-16T05:00:00Z` のような ISO 8601 形式で、多くの言語・ツールが解釈できる。

**(K) 多値返却** — Go は複数の値を同時に返せる。`return n, s.save()` は「n を返しつつ、save() の返り値をエラーとして一緒に返す」という 1 行完結の書き方。

#### Update — イミュータブルな更新

```go
updated := s.notes[idx]           // (L) コピーを作る
updated.Title = title
updated.UpdatedAt = now

newNotes := make([]Note, len(s.notes))
copy(newNotes, s.notes)
newNotes[idx] = updated           // (M) コピーを置き換え
s.notes = newNotes
```

**(L)(M) イミュータブルパターン** — `s.notes[idx].Title = title` と直接書いても動くが、それは既存スライスの要素を破壊的に変更する。新しいスライスを作って置き換えることで、変更前のスライスを参照しているゴルーチンが壊れない。

#### Delete — フィルタリングによる削除

```go
newNotes := make([]Note, 0, len(s.notes))  // (N)
for _, n := range s.notes {
    if n.ID == id { found = true; continue }  // (O)
    newNotes = append(newNotes, n)
}
s.notes = newNotes
```

**(N) cap の事前確保** — `make([]Note, 0, len(s.notes))` は長さ 0・容量 `len(s.notes)` のスライスを作る。削除後の要素数は最大でも元の長さを超えないため、`append` での再アロケーションを回避できる。

**(O) continue で除外** — 削除したいものを「消す」のではなく、削除したい以外を「新しいスライスに集める」アプローチ。

---

### normalizeTags — タグの正規化

```go
func normalizeTags(tags []string) []string {
    seen := make(map[string]struct{}, len(tags))  // (P)
    for _, t := range tags {
        t = strings.ToLower(strings.TrimSpace(t))
        if t == "" { continue }
        if _, exists := seen[t]; !exists {        // (Q)
            seen[t] = struct{}{}
            result = append(result, t)
        }
    }
}
```

**(P) `map[string]struct{}`** — 値を持たない Set（集合）を表す Go イディオム。`bool` を使う人もいるが、`struct{}` はメモリを 0 バイトしか使わないため効率的。

**(Q) 重複排除** — `seen` に登録済みかどうかチェック。`_, exists := seen[t]` は「キーが存在すれば `exists = true`」という 2 値代入。`_` は値（`struct{}{}`）が不要なので無視。

---

## handler/handler.go — HTTP 層

### ルーティング

```go
mux.HandleFunc("/notes", ...)   // (R)
mux.HandleFunc("/notes/", ...) // (S)
```

**(R) `/notes`（スラッシュなし）** — 完全一致。`GET /notes`、`POST /notes` のみにマッチ。

**(S) `/notes/`（スラッシュあり）** — **前方一致**。`/notes/1`、`/notes/42`、`/notes/search` すべてにマッチする。Go の `http.ServeMux` はスラッシュで終わるパターンをプレフィックスマッチとして扱う仕様。

```go
mux.HandleFunc("/notes/", func(w http.ResponseWriter, r *http.Request) {
    if strings.HasSuffix(r.URL.Path, "/search") {  // (T)
        handleSearch(...)
        return
    }
    id, err := parseID(r.URL.Path, "/notes/")      // (U)
    ...
})
```

**(T) search の先行チェック** — `/notes/search` が来たときに `parseID` を呼ぶと `"search"` を整数に変換しようとして失敗する。なので**数値 ID より前に** `/search` かどうかを確認する。

**(U) parseID の実装**

```go
func parseID(path, prefix string) (int, error) {
    raw := strings.TrimPrefix(path, prefix)  // "/notes/42" → "42"
    raw = strings.TrimSuffix(raw, "/")       // "42/" → "42"（末尾スラッシュ対応）
    return strconv.Atoi(raw)                 // "42" → 42
}
```

---

### noteInput と validate

```go
type noteInput struct {
    Title string   `json:"title"`
    Body  string   `json:"body"`
    Tags  []string `json:"tags"`
}

func (n noteInput) validate() string {
    if strings.TrimSpace(n.Title) == "" {
        return "title is required"
    }
    if len(n.Title) > 200 {
        return "title must be 200 characters or fewer"
    }
    return ""  // (V)
}
```

`Note`（保存用）と `noteInput`（受信用）を分けているのがポイント。`id` や `created_at` はサーバー側で決めるものなので、クライアントから受け取る型には含めない。

**(V) エラーを string で返す** — 本来は `error` 型で返すことが多いが、エラーメッセージをそのままレスポンスに使いたいためシンプルに `string` を選択。空文字 = エラーなし。

---

### handleCreate の流れ

```go
func handleCreate(w http.ResponseWriter, r *http.Request, s *store.Store) {
    var input noteInput
    if err := decodeBody(r, &input); err != nil {     // (W)
        writeError(w, http.StatusBadRequest, "invalid JSON")
        return
    }
    if msg := input.validate(); msg != "" {           // (X)
        writeError(w, http.StatusUnprocessableEntity, msg)
        return
    }
    note, err := s.Create(input.Title, input.Body, input.Tags)
    if err != nil {
        writeError(w, http.StatusInternalServerError, "failed to save")
        return
    }
    writeJSON(w, http.StatusCreated, note)            // (Y)
}
```

**(W) デコード失敗** — JSON が壊れている・型が違う → 400 Bad Request

**(X) バリデーション失敗** — title が空・長すぎる → 422 Unprocessable Entity（構文は正しいが意味が不正）

**(Y) 201 Created** — 200 ではなく **201** を返す。REST の慣習で「リソースが新しく作られた」ことを意味する。

---

### writeJSON

```go
func writeJSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)                           // (Z)
    _ = json.NewEncoder(w).Encode(v)
}
```

**(Z) Header → WriteHeader → Body の順番** — `WriteHeader` を呼んだ後はヘッダーを変更できない。必ずこの順番で書く必要がある Go の `net/http` の制約。`_ =` でエラーを捨てているのは、`w` への書き込み失敗は通常ネットワーク切断を意味し、その時点ではクライアントに何も伝えられないため。

---

## リクエストが来てから返るまでの全体フロー

`GET /notes/1` を例に、コードのどこを通るかを追う。

```
HTTP GET /notes/1
    │
    ▼
http.ServeMux  ("/notes/" に前方一致)
    │
    ▼
handler.go の匿名 func
  → "/search" サフィックスでない
  → parseID("/notes/1", "/notes/") = 1
  → r.Method == "GET" → handleGet(w, r, s, 1)
    │
    ▼
handleGet
  → s.GetByID(1)
    │
    ▼
store.GetByID
  → s.mu.RLock()
  → notes をループして ID=1 を探す
  → 見つかったら Note を返す
  → s.mu.RUnlock()  ← defer で保証
    │
    ▼
handleGet
  → writeJSON(w, 200, note)
      → Content-Type ヘッダーをセット
      → 200 ステータスを書く
      → JSON エンコードしてレスポンスボディに書く
```
