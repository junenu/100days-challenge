# Day001 — habit-tracker

## 概要

習慣をコマンドラインで管理する CLI ツール。毎日の完了記録、ストリーク計算、過去 30 日のカレンダー表示に対応。データは `~/.habit-tracker.json` に保存される。

## 技術スタック

- Language: Go 1.21
- Framework/Library: 標準ライブラリのみ
- Storage: JSON ファイル（`~/.habit-tracker.json`）

## 起動方法

```bash
# ビルド（カレントディレクトリで ./habit として使う）
go build -o habit .

# PATH に追加してどこからでも使う（任意）
go build -o habit . && mv habit /usr/local/bin/habit
```

## 使い方

```bash
# 習慣を追加
habit add "毎日読書"
habit add "英語学習"
habit add "運動30分"

# 今日の習慣を完了としてマーク
habit done "毎日読書"

# 今日の一覧を表示
habit list

# ストリーク情報を確認
habit streak "毎日読書"

# 過去 30 日のカレンダーを表示
habit history "毎日読書"

# 習慣を削除
habit delete "運動30分"

# ヘルプ
habit help
```

## 機能一覧

### 実装済み

- [x] 習慣の追加・削除
- [x] 今日の完了マーク（重複防止）
- [x] 今日の一覧表示（完了/未完了・ストリーク）
- [x] ストリーク計算（連続達成日数）
- [x] 過去 30 日カレンダー表示（週次グリッド）
- [x] ANSI カラー出力
- [x] データの永続化（JSON）

### 今後の改善候補（任意）

- [ ] 目標達成率の週次サマリー
- [ ] 習慣のリマインダー通知

## 開発ログ

### 学んだこと

- `time.Weekday()` の日曜=0 を月曜始まりに変換する処理（`startWd--` + `if wd==0 { wd=6 }`）
- `os.WriteFile` の権限を `0600` にして JSON を安全に保存するパターン

### 詰まったこと・解決方法

- カレンダーの週グリッド表示で、先頭行のオフセット計算がずれた → `startWd` の曜日変換を月曜基準に統一して解決

### 次回やってみたいこと

- Go の `cobra` を使ったサブコマンド設計
- `bubbletea` を使ったインタラクティブ TUI
