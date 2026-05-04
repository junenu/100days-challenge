"""Fictional character data for the portfolio."""

from models import Person, Skill, Project, TimelineEntry, SocialLink

PERSON = Person(
    name="Yuki Tanaka",
    title="Full-Stack Developer & Creative Coder",
    tagline="I build things that live on the internet — and occasionally, things that think.",
    bio=(
        "5 年以上の経験を持つフルスタックエンジニア。"
        "Web アプリケーション開発から機械学習まで幅広く手がけ、"
        "「動くものを美しく」をモットーにプロダクト開発に取り組んでいます。"
        "オープンソースへの貢献と技術コミュニティの発展を大切にしています。"
    ),
    location="Tokyo, Japan",
    email="yuki@example.dev",
    avatar_initials="YT",
    social_links=[
        SocialLink("GitHub", "https://github.com", "GH"),
        SocialLink("Twitter", "https://twitter.com", "TW"),
        SocialLink("LinkedIn", "https://linkedin.com", "LI"),
        SocialLink("Zenn", "https://zenn.dev", "ZN"),
    ],
    skills=[
        Skill("Python", 95, "Backend"),
        Skill("TypeScript", 88, "Frontend"),
        Skill("Go", 80, "Backend"),
        Skill("React", 85, "Frontend"),
        Skill("PostgreSQL", 78, "Database"),
        Skill("Docker", 82, "DevOps"),
        Skill("PyTorch", 70, "ML/AI"),
        Skill("Rust", 55, "Systems"),
    ],
    projects=[
        Project(
            title="NeuralNotes",
            description="自然言語処理を使ったスマートメモアプリ。入力内容を自動分類・タグ付けし、関連ノートをレコメンドする。",
            tech=["Python", "FastAPI", "React", "PyTorch"],
            image_emoji="🧠",
            featured=True,
        ),
        Project(
            title="Chronoflow",
            description="チーム向けタイムトラッキング & プロジェクト管理ツール。Slack / GitHub と連携してコンテキストを自動記録。",
            tech=["Go", "TypeScript", "PostgreSQL", "Redis"],
            image_emoji="⏱️",
            featured=True,
        ),
        Project(
            title="Pixelate CLI",
            description="ターミナルで動作する画像処理 CLI ツール。リサイズ・フィルタ・ASCII アート変換をパイプラインで処理。",
            tech=["Rust", "WASM"],
            image_emoji="🖼️",
            featured=False,
        ),
        Project(
            title="LiveQuery",
            description="WebSocket ベースのリアルタイム SQL クエリビジュアライザー。クエリの実行計画をアニメーションで可視化。",
            tech=["TypeScript", "D3.js", "WebSocket"],
            image_emoji="📊",
            featured=False,
        ),
        Project(
            title="Kanji Forge",
            description="漢字学習 Web アプリ。スペースド・リピティションアルゴリズムで効率的な学習カーブを実現。",
            tech=["Next.js", "Python", "SQLite"],
            image_emoji="🈳",
            featured=False,
        ),
        Project(
            title="SkyMapper",
            description="衛星データを使った農業支援ツール。NDVI 指数から作物の健康状態をヒートマップ表示。",
            tech=["Python", "NumPy", "Leaflet.js"],
            image_emoji="🛰️",
            featured=False,
        ),
    ],
    timeline=[
        TimelineEntry(
            year="2024",
            title="Senior Engineer",
            organization="Luminary Tech K.K.",
            description="決済プラットフォームのバックエンドリード。月間 1 億件のトランザクションを処理するマイクロサービス基盤を設計・構築。",
            kind="work",
        ),
        TimelineEntry(
            year="2022",
            title="Software Engineer",
            organization="DataBridge Inc.",
            description="ML パイプライン基盤の開発。Python と Go を組み合わせたデータ処理ワークフローを構築し処理速度を 40% 改善。",
            kind="work",
        ),
        TimelineEntry(
            year="2021",
            title="修士（情報工学）",
            organization="東京工業大学",
            description="自然言語処理・グラフニューラルネットワークの研究。国際会議 2 本採択。",
            kind="education",
        ),
        TimelineEntry(
            year="2019",
            title="Software Engineer Intern",
            organization="Google Tokyo",
            description="検索品質チームでクエリ拡張アルゴリズムの研究開発に従事。",
            kind="work",
        ),
        TimelineEntry(
            year="2019",
            title="学士（情報工学）",
            organization="東京大学",
            description="情報理工学系研究科。卒業論文：強化学習を用いたゲームエージェントの研究。",
            kind="education",
        ),
    ],
)
