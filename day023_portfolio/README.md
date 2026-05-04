# Day 023 — Portfolio Site Generator

架空の人物「Yuki Tanaka」のポートフォリオサイトを生成する Python 製静的サイトジェネレーター。

## 特徴

- **外部依存ゼロ** — 標準ライブラリのみで動作
- **コンポーネント設計** — `Component` 基底クラスから派生した再利用可能な部品
- **データ分離** — `models.py` (dataclass) / `data.py` (コンテンツ) / `components.py` (描画) を完全分離
- **ダークモード UI** — アニメーション・レスポンシブ対応

## 構造

```
day023_portfolio/
├── main.py        # エントリーポイント・ローカルサーバー
├── generator.py   # HTML ページアセンブラー
├── components.py  # 再利用可能な HTML コンポーネント群
├── styles.py      # CSS ビルダー
├── models.py      # データモデル (dataclass)
├── data.py        # 架空キャラクターのデータ
└── output/
    └── index.html # 生成済み HTML
```

## 使い方

```bash
# HTML を生成するだけ
python main.py

# 生成してブラウザで確認
python main.py --serve

# ポートを指定
python main.py --serve --port 3000
```

## コンポーネント一覧

| クラス | 役割 |
|--------|------|
| `Component` | 全コンポーネントの抽象基底クラス |
| `Tag` | 汎用 HTML タグラッパー |
| `Badge` | バッジ（スキル・注目ラベル等） |
| `ProgressBar` | アニメーション付きスキルバー |
| `SectionHeader` | セクションタイトル + サブタイトル |
| `NavBar` | 固定ナビゲーションバー |
| `HeroSection` | ファーストビュー |
| `AboutSection` | 自己紹介セクション |
| `SkillGroup` | カテゴリ別スキルグループ |
| `SkillsSection` | スキル全体セクション |
| `ProjectCard` | プロジェクトカード |
| `ProjectsSection` | プロジェクト一覧グリッド |
| `TimelineItem` | タイムライン 1 エントリー |
| `TimelineSection` | キャリア・学歴タイムライン |
| `ContactSection` | コンタクト CTA |
| `Footer` | フッター |

## カスタマイズ

`data.py` の `PERSON` を編集するだけで別人のポートフォリオを生成できます。
