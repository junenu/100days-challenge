# Day004 — expense-tracker

## 概要

Python 製の CLI 家計簿。支出の追加・一覧・削除・月次サマリーをターミナル上で管理できる。
データは CSV ファイルに保存し、外部ライブラリ不要（Python 標準ライブラリのみ）。
ANSI カラー + ASCII バーグラフでカテゴリ別支出を可視化。

## 技術スタック

- Language: Python 3.10+
- Framework/Library: 標準ライブラリのみ（csv, pathlib, datetime, collections）
- データ永続化: CSV（expenses.csv）

## 起動方法

```bash
# セットアップ（依存なし）
cd day004_expense-tracker

# 支出を追加（対話式）
python expense_tracker.py add

# 支出一覧
python expense_tracker.py list

# 今月 / 年間サマリー（ASCII グラフ）
python expense_tracker.py summary

# 特定月の絞り込み
python expense_tracker.py list --month 2026-04
python expense_tracker.py summary --month 2026-04

# カテゴリ絞り込み
python expense_tracker.py list --cat food

# 支出削除
python expense_tracker.py delete 3

# ヘルプ
python expense_tracker.py help
```

## 機能一覧

### 実装済み

- [x] 支出の追加（金額・カテゴリ・説明・日付）
- [x] 全支出一覧表示
- [x] 月別・カテゴリ別フィルタリング
- [x] 支出の削除（ID 指定）
- [x] 月次・年間カテゴリ別サマリー（ASCII バーグラフ）
- [x] CSV 永続化（外部 DB 不要）
- [x] ANSI カラー表示
- [x] 入力バリデーション

### 今後の改善候補（任意）

- [ ] 予算アラート（カテゴリごとに上限を設定）
- [ ] 月次レポートの CSV エクスポート
- [ ] 定期支出の自動登録

## 開発ログ

### 学んだこと

- Python の `csv.DictWriter` / `DictReader` で手軽に CSV 永続化ができる
- `defaultdict(float)` で集計処理をシンプルに書ける
- ANSI エスケープコードは Windows の旧 cmd では動作しない場合がある（Windows Terminal は OK）

### 詰まったこと・解決方法

- カラー出力の文字幅ズレ：ANSI コードを含む文字列の `:<N>` フォーマットは見かけ上ずれるため、バー部分は固定幅で調整した

### 次回やってみたいこと

- Rust で同じ CLI を実装してパフォーマンス比較
- TUI ライブラリ（Rich / Textual）を使ったリッチな画面構成
