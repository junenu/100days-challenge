# Day024 — 2048

## 概要

TypeScript + Canvas API で実装したブラウザ動作の 2048 パズルゲーム。
矢印キーまたはスワイプ操作でタイルをスライドさせ、同じ数字を合体させながら 2048 タイルを目指す。
ベストスコアは localStorage に永続保存。

## 技術スタック

- Language: TypeScript
- Framework/Library: Vite（バンドラー）
- Rendering: Canvas API（純粋な 2D 描画）
- Storage: localStorage（ベストスコア）
- 外部依存: なし（Vite/TypeScript のみ）

## 起動方法

```bash
# セットアップ
npm install

# 開発サーバー起動
npm run dev

# ビルド
npm run build
```

## 機能一覧

### 実装済み

- [x] 4×4 グリッドでの 2048 ゲームロジック（上下左右スライド・合体）
- [x] 矢印キー操作
- [x] タッチ / スワイプ操作（モバイル対応）
- [x] スコア表示・ベストスコアの localStorage 永続化
- [x] タイル出現・合体時のポップインアニメーション
- [x] 2048 達成時の勝利メッセージ + Keep Playing（継続プレイ）
- [x] ゲームオーバー判定と表示
- [x] New Game ボタンでリスタート
- [x] 数値に応じた伝統的カラーパレット

### 今後の改善候補（任意）

- [ ] スライドアニメーション（タイルが滑らかに移動する）
- [ ] アンドゥ機能
- [ ] 4096 / 8192 チャレンジモード

## 開発ログ

### 学んだこと

- Canvas の `save() / restore()` と `translate + scale` の組み合わせでアニメーションの中心点を簡単に制御できる
- 2048 のスライドロジックは「左スライド」に正規化し、行列の転置・反転で上下右方向を統一すると実装が大幅にシンプルになる
- イミュータブルな `grid.map(row => row.map(...))` パターンで副作用なく状態遷移が書ける

### 詰まったこと・解決方法

- `down` 方向の逆変換：`transpose → reverseRows` の順が正しいが、逆変換は `reverseRows → transpose` ではなく `transpose(reverseRows(working))` のため行列演算の順序に注意
- Canvas は accessibility snapshot に映らないため、スクリーンショットで動作確認

### 次回やってみたいこと

- WebSocket を使ったリアルタイム同期系ツール
