# Day008 — pet-cli

## 概要

ターミナルに住む小さなペットを育てる CLI ゲーム。
ご飯・遊び・休息の 3 コマンドでステータスを管理し、放置するとお腹が空いて機嫌が悪くなる。
データは `~/.pet-cli/pet.json` に永続化される。

## 技術スタック

- Language: Go 1.23
- Framework/Library: cobra（CLI フレームワーク）
- その他: JSON ファイル永続化、時間経過による自動ステータス減衰

## 起動方法

```bash
# ビルド（Go 1.23 が必要）
make build
# または
/opt/homebrew/opt/go@1.23/bin/go build -o pet .

# 新しいペットを迎える
./pet new <名前>

# 様子を見る
./pet status

# ごはんをあげる
./pet feed

# 一緒に遊ぶ
./pet play

# 休ませる
./pet rest

# お別れする（データ削除）
./pet goodbye
```

## 機能一覧

### 実装済み

- [x] ペットの新規作成・永続化（JSON）
- [x] Hunger / Happiness / Energy の 3 ステータス管理
- [x] 時間経過による自動ステータス減衰（1 時間ごとに減少）
- [x] 状態に応じた顔文字・セリフの変化
- [x] エネルギー切れ時に遊べない制約
- [x] 日齢（Age）表示
- [x] ASCII バー表示でステータスを視覚化

### 今後の改善候補

- [ ] 進化・成長段階の実装（赤ちゃん→子供→大人）
- [ ] 病気・回復イベントの追加
- [ ] ミニゲーム（タイピング対決など）

## 開発ログ

### 学んだこと

- Go 1.22 は macOS 26 (Sequoia beta) で `missing LC_UUID` エラーが発生、Go 1.23 で解決
- `time.Since` で経過時間を取り、ステータス減衰を自然に表現できる

### 詰まったこと・解決方法

- Go 1.22 + macOS 26 の `dyld: missing LC_UUID` → `brew install go@1.23` で解決

### 次回やってみたいこと

- ターミナルアニメーション（ペットが動く表現）
- Web UI 版（React + WebSocket でリアルタイム表示）
