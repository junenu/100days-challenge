# Day009 — markdown-preview

## 概要

Markdown ファイルをターミナルでカラー整形表示する Node.js 製 CLI ビューワー。
見出し・コードブロック・テーブル・引用・リストを色付きでレンダリングする。

## 技術スタック

- Language: Node.js (ESM)
- Library: marked (Markdown パーサー), chalk (ターミナル色付け), cli-table3 (テーブル描画)

## 起動方法

```bash
# セットアップ
cd day009_markdown-preview
npm install

# 実行
node src/index.js sample.md

# 任意の .md ファイルを指定
node src/index.js /path/to/file.md

# グローバルインストール（任意）
npm link
mdp sample.md
```

## 機能一覧

### 実装済み

- [x] H1〜H6 見出しをレベル別カラーで表示（magenta / cyan / blue）
- [x] コードブロックをボーダー付き・緑色で表示（言語名ラベル付き）
- [x] テーブルを罫線付きで整形表示（ヘッダー黄色）
- [x] 引用ブロックをグレーのバー付きで表示
- [x] 順序あり・なしリストをインデント付きで表示
- [x] 太字・イタリック・インラインコード・リンクのインライン装飾
- [x] 水平線の罫線表示
- [x] エラーハンドリング（ファイル未指定・非 Markdown・存在しないファイル）
- [x] `--help` フラグのサポート

### 今後の改善候補（任意）

- [ ] ページャー（less 風）による長文スクロール
- [ ] stdin からのパイプ入力対応 (`cat file.md | mdp`)
- [ ] シンタックスハイライト（言語別コード色付け）

## 開発ログ

### 学んだこと

- `marked` の `lexer()` で AST トークンを取得し、自前ウォーカーでレンダリングする方法
- `chalk` v5 が ESM only のため `"type": "module"` が必須
- `cli-table3` の `colWidths` を ANSI エスケープコード除去後の文字数で計算する必要がある点

### 詰まったこと・解決方法

- テーブルの列幅計算で ANSI カラーコードが文字数に含まれ、ズレが発生
  → `/\x1b\[[0-9;]*m/g` で除去してから計算することで解決

### 次回やってみたいこと

- React Ink を使ったインタラクティブなターミナル UI
