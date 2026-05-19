# 100 Days Challenge

100 日間、毎日 1 つのプロダクトを完成させる挑戦。
言語・ジャンル不問。動くものを毎日届ける。

詳細ルール → [RULES.md](./RULES.md)

---

## 進捗

| Day | プロダクト名 | 技術スタック | 一言メモ       |
| --- | ------------ | ------------ | -------------- |
| 001 | [habit-tracker](./day001_habit-tracker) | Go | 習慣管理 CLI。ストリーク・30日カレンダー付き |
| 002 | [pomodoro-timer](./day002_pomodoro-timer) | JavaScript (Node.js) | ターミナル版ポモドーロタイマー。ANSI カラー・プログレスバー付き |
| 003 | [quiz-game](./day003_quiz-game) | JavaScript (Node.js) | JS 基礎を学べる CLI クイズゲーム。詳細コード解説付き |
| 004 | [expense-tracker](./day004_expense-tracker) | Python | CLI 家計簿。CSV 永続化・カテゴリ別 ASCII バーグラフ付き |
| 005 | [notes-api](./day005_notes-api) | Go | メモ管理 REST API。CRUD + 全文検索・JSON ファイル永続化 |
| 006 | [netdiag](./day006_netdiag) | Go (cobra/tablewriter) | ネットワーク診断 CLI。ping/traceroute/DNS/ポートスキャン |
| 007 | [weather-board](./day007_weather-board) | React + Vite + Recharts | モックデータの天気ダッシュボード。5 地域切替・グラフ付き |
| 008 | [pet-cli](./day008_pet-cli) | Go (cobra) | ターミナル育成ペット。時間経過でステータス減衰・顔文字で感情表現 |
| 009 | [markdown-preview](./day009_markdown-preview) | Node.js (ESM) | Markdown をターミナルでカラー整形表示する CLI ビューワー |
| 010 | [json-diff](./day010_json-diff) | Python | 2 つの JSON を比較して差分を色付き表示する CLI ツール |
| 011 | [config-diff](./day011_config-diff) | Python | Cisco/Juniper 設定ファイルをセクション単位で比較する CLI + Web UI |
| 012 | [othello](./day012_othello) | Python + pygame | pygame 製オセロ。AI 対戦（Minimax depth=4 + α-β 枝刈り） |
| 013 | [breakout](./day013_breakout) | Python + pygame | pygame 製ブロック崩し。3 レベル・HP 制ブロック・パドル角度コントロール |
| 014 | [py-share-server](./day014_py-share-server) | Python | 標準ライブラリだけで動くローカルファイル共有用の簡易 Web サーバー |
| 015 | [log-analyzer](./day015_log-analyzer) | Python | アクセスログを集計する CLI。ステータス別・URL別・IP別ランキング表示 |
| 016 | [netdiag-web](./day016_netdiag-web) | React + Vite | ネットワーク診断 Web サービス。ping/DNS/ポートスキャンをブラウザから実行 |
| 017 | [roguelike](./day017_roguelike) | Python + curses | ターミナルダンジョン探索。FOV・4 種モンスター・レベルアップ・5 フロア |
| 018 | [rpg](./day018_rpg) | Python + pygame | トップダウンアクション RPG。剣・魔法・ボス戦・レベルアップシステム |
| 019 | [mnist-sketch](./day019_mnist-sketch) | Python + FastAPI + scikit-learn | Canvas 手書き数字を ML モデル（MLP・97% 精度）がリアルタイム認識 |
| 020 | [tetris](./day020_tetris) | TypeScript + Vite + Canvas API | ブラウザ動作のテトリス。ゴーストピース・ウォールキック・レベルアップ対応 |
| 021 | [typing-game](./day021_typing-game) | Python + pygame | 日英対応タイピングゲーム。正確率・CPM 計測・IME 対応 |
| 022 | [darts](./day022_darts) | Python + pygame | 501 ルールダーツ対戦。リアルなボード描画・CPU 自動対戦（ダブルフィニッシュ判断） |
| 023 | [portfolio](./day023_portfolio) | Python | 静的サイトジェネレーター。Component 抽象基底クラスから派生した 16 種の再利用可能コンポーネントで架空人物のポートフォリオを生成 |
| 024 | [2048](./day024_2048) | TypeScript + Vite + Canvas API | ブラウザ動作の 2048 パズル。矢印キー / スワイプ操作・ポップインアニメーション・ベストスコア永続化 |
| 025 | [synth](./day025_synth) | TypeScript + Vite + Web Audio API | ブラウザ動作のポリフォニック・シンセサイザー。4 波形・ADSR・ディレイ・リバーブ・オシロスコープ付き |
| 026 | [life](./day026_life) | Node.js (ESM) | ターミナル Conway's Game of Life。7 種プリセット・速度調整・カラー新生セル表示 |
| 027 | [pixel-art](./day027_pixel-art) | TypeScript + Vite + Canvas API | ブラウザ動作のピクセルアートエディタ。Flood Fill・Undo/Redo・PNG エクスポート・外部依存ゼロ |
| 028 | [img-resize](./day028_img-resize) | TypeScript + Vite + Canvas API | ブラウザ動作の画像リサイザー。PNG/JPEG/WebP 対応・アスペクト比ロック・10 種プリセット・品質スライダー |
| 029 | [mandelbrot](./day029_mandelbrot) | TypeScript + Vite + Canvas API | マンデルブロ集合エクスプローラー。ズーム/パン・スムースカラーリング・5 種カラーマップ |
| 030 | [reaction-diffusion](./day030_reaction-diffusion) | TypeScript + Vite + Canvas API | Gray-Scott 反応拡散シミュレーター。6 種プリセット・4 種カラーテーマ・クリックで化学物質注入 |
| 031 | [booklog](./day031_booklog) | Python + PostgreSQL + Docker Compose | psycopg2 接続の読書ログ CLI。追加・一覧・評価・統計・自動マイグレーション |
| 032 | [netwatch](./day032_netwatch) | Python + PostgreSQL + Docker Compose | ping/traceroute 結果を DB 記録するネットワーク監視 CLI。可用性レポート・定期監視ループ・Rich 表示 |
| 033 | [dataview](./day033_dataview) | Python + Streamlit + Plotly | CSV 分析ダッシュボード。6 種グラフ・相関ヒートマップ・サイドバーフィルター・CSV ダウンロード |
| 034 | [tab-timer](./day034_tab-timer) | JavaScript + Chrome Extensions API (MV3) | タブ閲覧時間計測 Chrome 拡張。ドメイン別ランキング・バーグラフ・ファビコン・リアルタイム更新 |
| 035 | [flashcard](./day035_flashcard) | Svelte 5 + TypeScript + Vite | SM-2 間隔反復アルゴリズム搭載フラッシュカード暗記アプリ。3D フリップ・デッキ管理・localStorage 永続化 |

完了: 35 / 100

---

## 統計

| 言語 | 回数 |
| ---- | ---- |
| Go | 4 |
| JavaScript (Node.js) | 4 |
| JavaScript (Chrome Extension) | 1 |
| Python | 16 |
| React (JSX) | 2 |
| TypeScript + Vite | 7 |
| Svelte + TypeScript + Vite | 1 |

---

## ライセンス

各プロダクトのライセンスはそれぞれのディレクトリを参照してください。
