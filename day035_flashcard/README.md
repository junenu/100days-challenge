# Day035 — FlashCard

## 概要

Svelte + TypeScript で作ったフラッシュカード暗記アプリ。
デッキ管理・カード作成・3D フリップアニメーションによる学習・SM-2 アルゴリズムによる間隔反復スケジューリングを備え、データは localStorage に永続化される。

## 技術スタック

- Language: TypeScript
- Framework/Library: Svelte 5 + Vite
- Algorithm: SM-2 Spaced Repetition
- Storage: localStorage（外部依存なし）

## 起動方法

```bash
# セットアップ
npm install

# 開発サーバー
npm run dev

# プロダクションビルド
npm run build
```

ブラウザで `http://localhost:5173` を開く。

## 機能一覧

### 実装済み

- [x] デッキ作成・編集・削除
- [x] カード作成・編集・削除（表面 / 裏面）
- [x] 3D フリップアニメーション（タップ / クリックで裏返し）
- [x] SM-2 アルゴリズムによる間隔反復スケジューリング
  - 4 段階評価: もう一度 / 難しい / 良い / 簡単
  - 評価に応じて次回復習日・インターバルを自動調整
- [x] 学習セッション（当日期限カードのみ出題、シャッフル）
- [x] セッション完了画面（正解数・正答率表示）
- [x] デッキ一覧に due 枚数バッジ表示
- [x] カード一覧に次回復習日表示
- [x] localStorage によるデータ永続化
- [x] サンプルデッキ自動生成

### 今後の改善候補（任意）

- [ ] ダークモード対応
- [ ] CSV インポート / エクスポート
- [ ] 学習履歴グラフ

## 開発ログ

### 学んだこと

- Svelte の `get(store)` は `onMount` 内などの命令的コンテキストで store を同期読み取りする正しい方法
- `$store` リアクティブ構文はコンポーネントの reactive context 外では store 変更を追跡しない
- SM-2 の ease factor 計算: `EF' = EF + 0.1 - (3 - q) * (0.08 + (3 - q) * 0.02)`（最小 1.3）

### 詰まったこと・解決方法

- `$: { sessionCards = shuffle(...) }` リアクティブ文は store 更新のたびに再実行され、学習中にカードリストが再シャッフルされるバグが発生
- → `initSession()` 関数で `get(appStore)` を使い、コンポーネント初期化時に一度だけセッションを固定することで解決

### 次回やってみたいこと

- SvelteKit ルーティングを使った複数ページ構成
- WebWorker でバックグラウンド同期
