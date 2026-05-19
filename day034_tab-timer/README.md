# Day034 — Tab Timer

## 概要

各タブ（ドメイン別）の閲覧時間を計測する Chrome 拡張機能。
ポップアップでランキング・バーグラフ・合計時間をリアルタイム表示します。

## 技術スタック

- Language: JavaScript (Vanilla ES2022)
- Platform: Chrome Extensions API (Manifest V3)
- Storage: `chrome.storage.local`
- Background: Service Worker + `chrome.alarms`
- その他: Favicon 取得（Google S2 API）

## 起動方法

```bash
# Chrome の拡張機能管理ページを開く
# chrome://extensions/

# 「デベロッパーモード」を ON にする（右上のトグル）

# 「パッケージ化されていない拡張機能を読み込む」→ day034_tab-timer/ を選択
```

読み込み後、Chrome ツールバーのパズルピースアイコンから Tab Timer をピン留めすると使いやすくなります。

## 機能一覧

### 実装済み

- [x] タブ切り替えを検知してドメイン別に閲覧時間を積算
- [x] ウィンドウがフォーカスを失った場合に計測を一時停止
- [x] 10 秒ごとの定期フラッシュ（サービスワーカー再起動後も継続）
- [x] 日付を跨いだ場合に自動リセット
- [x] ポップアップでランキング表示（順位・ファビコン・ドメイン名・バーグラフ・時間）
- [x] 現在閲覧中のドメインをアニメーション点滅で強調
- [x] リアルタイム更新（5 秒間隔でポップアップを再描画）
- [x] 今日の合計閲覧時間を表示
- [x] 今日のデータをリセットするボタン
- [x] `chrome://` などの内部ページは計測対象外

### 今後の改善候補（任意）

- [ ] 計測除外リスト（特定ドメインをスキップ）
- [ ] 週次・月次のグラフ表示
- [ ] 1 日の上限時間アラート

## 開発ログ

### 学んだこと

- Manifest V3 ではバックグラウンドスクリプトが Service Worker になるため、メモリ上の状態を持ち続けられない。`chrome.storage.local` への都度書き込みが必須。
- `chrome.alarms` は Service Worker が落ちていても定期起動できる唯一の手段。
- ファビコン取得には Google の `s2/favicons` エンドポイントが手軽。

### 詰まったこと・解決方法

- Service Worker の再起動時に計測中だった時間を失う問題 → `flushActive()` でタイマーを都度リセットし、ストレージをソースオブトゥルースにすることで解決。
- `tabs.onActivated` だけだと URL 更新（SPA のルーティングなど）を取りこぼす → `tabs.onUpdated` と組み合わせて対応。

### 次回やってみたいこと

- Rust で CLI ツールに挑戦
- IndexedDB を使った履歴グラフ
