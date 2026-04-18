# Day007 — Weather Board

## 概要

React + Vite + Recharts で作成した、モックデータのみを使う天気ダッシュボード。
東京・大阪・札幌・福岡・沖縄の 5 地域を切り替えながら、今日の概要・7 日間予報・24 時間の気温推移と降水確率を一画面で確認できる。

## 技術スタック

- Language: JavaScript (JSX)
- Framework: React 18 + Vite 5
- Library: Recharts 2（折れ線グラフ・棒グラフ）
- その他: CSS（グラデーション背景・レスポンシブ対応）

## 起動方法

```bash
# セットアップ
npm install

# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build
npm run preview
```

## 機能一覧

### 実装済み

- [x] 5 地域（東京・大阪・札幌・福岡・沖縄）のタブ切替
- [x] 今日のサマリ（天気アイコン・最高/最低気温・降水確率・風速・湿度）
- [x] 7 日間予報カード
- [x] 24 時間気温推移の折れ線グラフ（Recharts）
- [x] 24 時間降水確率の棒グラフ（Recharts）
- [x] スカイブルーグラデーション背景・レスポンシブ対応

### 今後の改善候補（任意）

- [ ] OpenWeatherMap API との接続（実データ化）
- [ ] ダークモード対応
- [ ] 地図上での地域選択

## 開発ログ

### 学んだこと

- Recharts の `ComposedChart` で折れ線と棒を組み合わせると 1 コンポーネントでまとめられる
- Vite + React の初期設定は `package.json` + `vite.config.js` の 2 ファイルで完結する

### 詰まったこと・解決方法

- 特になし（モックデータのみなので外部依存ゼロ）

### 次回やってみたいこと

- リアルタイム更新（WebSocket or Server-Sent Events）を使った何か
