# Day033 — DataView

## 概要

Python + Streamlit + Plotly で作るインタラクティブ CSV 分析ダッシュボード。
CSV ファイルをアップロード or サンプルデータを選ぶだけで、グラフ・統計・相関ヒートマップをブラウザ上でインタラクティブに探索できます。

## 技術スタック

- Language: Python 3.12
- Framework/Library: Streamlit 1.35+, Plotly 5+, Pandas 2.2+
- その他: 同梱サンプルデータ（売上データ・都道府県別人口データ）

## 起動方法

```bash
# セットアップ
pip install -r requirements.txt

# 実行
streamlit run app.py
# → ブラウザで http://localhost:8501 が開く
```

## 機能一覧

### 実装済み

- [x] サンプルデータ 2 種（売上 CSV / 都道府県別人口 CSV）をワンクリック読み込み
- [x] 任意 CSV ファイルのアップロード（文字コード選択対応: UTF-8 / Shift_JIS / CP932）
- [x] カテゴリ列によるサイドバーフィルター（最大 4 列、30 値以下の列に自動適用）
- [x] 基本統計量（count / mean / std / min / max / 四分位数）
- [x] カテゴリ列の値分布バーチャート（上位 10 値）
- [x] グラフ 6 種
  - 棒グラフ（集計方法: sum / mean / count、色分け対応）
  - 折れ線グラフ（グループ別マーカー付き）
  - 散布図（色分け・バブルサイズ対応）
  - ヒストグラム（ビン数スライダー）
  - 箱ひげ図（グループ別）
  - 円グラフ（件数 or 数値集計）
- [x] 数値列の相関係数ヒートマップ（RdBu カラースケール）
- [x] 生データプレビュー（全文検索・列ソート）
- [x] フィルター適用後データの CSV ダウンロード（UTF-8 BOM 付き）
- [x] エラーハンドリング（読み込み失敗時のメッセージ表示）

### 今後の改善候補（任意）

- [ ] 時系列データの自動検出と日次/週次/月次集計
- [ ] NULL 値の可視化と補完オプション
- [ ] グラフ画像のダウンロードボタン

## 開発ログ

### 学んだこと

- Streamlit の `st.tabs` と `st.columns` でレイアウトをシンプルに組める
- Plotly Express はカラム名を直接渡すだけで凡例・軸ラベルが自動生成される
- `pd.DataFrame.select_dtypes` で数値列・カテゴリ列を動的に分けると汎用性が高い

### 詰まったこと・解決方法

- Plotly 6.x でのカラーバー非表示: `coloraxis_showscale=False` で対応
- CSV ダウンロード時の文字化け: `utf-8-sig` (BOM 付き UTF-8) でExcel との互換性を確保

### 次回やってみたいこと

- Rust で同様の CLI ツール（高速処理に興味あり）
- WebAssembly + Python (Pyodide) でサーバーレス版
