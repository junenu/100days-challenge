# Day002 — Pomodoro Timer

## 概要

ターミナルで動作するポモドーロタイマー CLI。作業 25 分 → 短い休憩 5 分 → 4 セット後に長い休憩 15 分 のサイクルを管理する。ANSI カラー・プログレスバー・キーボード操作に対応。外部パッケージ不要（Node.js 標準ライブラリのみ）。

## 技術スタック

- Language: JavaScript (Node.js)
- Framework/Library: なし（標準ライブラリのみ: `readline`, `process.stdout`）
- その他: ANSI エスケープコード、Keypress イベント

## 起動方法

```bash
# Node.js >= 18 が必要
node --version

# 実行
node main.js

# または
npm start

# 時間をカスタマイズして実行（環境変数）
WORK_MINUTES=50 SHORT_BREAK_MINUTES=10 node main.js
```

## 操作方法

| キー | 動作 |
|------|------|
| `Space` / `p` | 一時停止 / 再開 |
| `s` | 現在のセッションをスキップ |
| `q` / `Ctrl+C` | 終了（完了数を表示） |

## 機能一覧

### 実装済み

- [x] 作業セッション（デフォルト 25 分）のカウントダウン
- [x] 短い休憩（デフォルト 5 分）のカウントダウン
- [x] 長い休憩（デフォルト 15 分、4 ポモドーロごと）のカウントダウン
- [x] ANSI カラーによるセッション種別の視覚的区別
- [x] リアルタイム プログレスバー & パーセント表示
- [x] 完了ポモドーロ数の追跡
- [x] 絵文字ドット（次の長い休憩までの進捗）
- [x] 一時停止 / 再開
- [x] セッションスキップ
- [x] 環境変数による時間カスタマイズ
- [x] 終了時のサマリー表示

### 今後の改善候補（任意）

- [ ] 音声通知（macOS `say` コマンド連携）
- [ ] セッション履歴の JSON 保存
- [ ] 統計表示（週次・月次）

## 開発ログ

### 学んだこと

- Node.js の `readline.emitKeypressEvents` + `stdin.setRawMode(true)` でターミナルの raw モード入力が実現できる
- ANSI エスケープコード `\x1b[2J\x1b[H` で画面クリア + カーソル先頭移動が可能
- イミュータブルな状態更新（`{ ...state, key: value }`）でバグが減る

### 詰まったこと・解決方法

- **TTY チェック**: `process.stdin.isTTY` が falsy の場合（パイプ等）は `setRawMode` を呼ばないよう条件分岐が必要
- **タイマーの重複起動**: `startTick` 冒頭で `if (tickInterval) return` のガードを入れることで解決

### 次回やってみたいこと

- Web ブラウザ版（Svelte/React + Web Audio API）
- Rust で同様の CLI を実装し、パフォーマンスを比較
