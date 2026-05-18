import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import io

DATA_DIR = Path(__file__).parent / "data"
SAMPLE_DATASETS = {
    "売上データ（電子機器 2024）": DATA_DIR / "sales.csv",
    "都道府県別人口データ": DATA_DIR / "population.csv",
}

st.set_page_config(
    page_title="DataView — CSV 分析ダッシュボード",
    page_icon="📊",
    layout="wide",
)

st.title("📊 DataView — CSV 分析ダッシュボード")
st.markdown("CSV ファイルをアップロード、またはサンプルデータを選んでインタラクティブに探索できます。")

with st.sidebar:
    st.header("データソース")
    source = st.radio("データ選択", ["サンプルデータ", "CSV アップロード"])

    df: pd.DataFrame | None = None

    if source == "サンプルデータ":
        selected = st.selectbox("データセット", list(SAMPLE_DATASETS.keys()))
        path = SAMPLE_DATASETS[selected]
        df = pd.read_csv(path)
        st.success(f"{len(df)} 行 × {len(df.columns)} 列")
    else:
        uploaded = st.file_uploader("CSV ファイルを選択", type="csv")
        if uploaded:
            encoding = st.selectbox("文字コード", ["utf-8", "shift_jis", "cp932"])
            try:
                df = pd.read_csv(uploaded, encoding=encoding)
                st.success(f"{len(df)} 行 × {len(df.columns)} 列")
            except Exception as e:
                st.error(f"読み込みエラー: {e}")

    if df is not None:
        st.divider()
        st.header("フィルター")
        cat_cols = [c for c in df.columns if df[c].dtype == object]
        filters: dict[str, list] = {}
        for col in cat_cols[:4]:
            unique_vals = sorted(df[col].dropna().unique().tolist())
            if len(unique_vals) <= 30:
                selected_vals = st.multiselect(col, unique_vals, default=unique_vals)
                filters[col] = selected_vals

        for col, vals in filters.items():
            if vals:
                df = df[df[col].isin(vals)]

        st.caption(f"フィルター後: {len(df)} 行")


if df is None:
    st.info("左のサイドバーからデータを選択またはアップロードしてください。")
    st.stop()

num_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

tab_overview, tab_charts, tab_heatmap, tab_raw = st.tabs(
    ["概要・統計", "グラフ", "相関ヒートマップ", "生データ"]
)

with tab_overview:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("行数", f"{len(df):,}")
    col2.metric("列数", len(df.columns))
    col3.metric("数値列", len(num_cols))
    col4.metric("カテゴリ列", len(cat_cols))

    st.subheader("基本統計量")
    if num_cols:
        st.dataframe(df[num_cols].describe().T.style.format("{:.2f}"), use_container_width=True)

    if cat_cols:
        st.subheader("カテゴリ列の値分布")
        cols_per_row = 3
        for i in range(0, len(cat_cols), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cat_cols[i : i + cols_per_row]):
                vc = df[col].value_counts().head(10)
                with cols[j]:
                    fig = px.bar(
                        x=vc.values,
                        y=vc.index,
                        orientation="h",
                        title=col,
                        labels={"x": "件数", "y": col},
                        height=300,
                        color=vc.values,
                        color_continuous_scale="Blues",
                    )
                    fig.update_layout(showlegend=False, coloraxis_showscale=False, margin=dict(t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)

with tab_charts:
    chart_type = st.selectbox(
        "グラフタイプ",
        ["棒グラフ", "折れ線グラフ", "散布図", "ヒストグラム", "箱ひげ図", "円グラフ"],
    )

    if chart_type == "棒グラフ":
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("X 軸 (カテゴリ)", cat_cols + num_cols)
        y_col = c2.selectbox("Y 軸 (数値)", num_cols) if num_cols else None
        color_col = c3.selectbox("色分け", ["なし"] + cat_cols)
        agg_func = st.radio("集計方法", ["sum", "mean", "count"], horizontal=True)

        if y_col:
            if agg_func == "count":
                plot_df = df.groupby(x_col).size().reset_index(name="count")
                y_plot = "count"
            else:
                plot_df = df.groupby(x_col)[y_col].agg(agg_func).reset_index()
                y_plot = y_col

            kwargs: dict = dict(x=x_col, y=y_plot, title=f"{x_col} × {y_plot} ({agg_func})")
            if color_col != "なし" and color_col in plot_df.columns:
                kwargs["color"] = color_col
            fig = px.bar(plot_df, **kwargs, height=500)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "折れ線グラフ":
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("X 軸", df.columns.tolist())
        y_col = c2.selectbox("Y 軸 (数値)", num_cols) if num_cols else None
        color_col = c3.selectbox("色分け (グループ)", ["なし"] + cat_cols)

        if y_col:
            kwargs = dict(x=x_col, y=y_col, title=f"{x_col} → {y_col}")
            if color_col != "なし":
                kwargs["color"] = color_col
            fig = px.line(df, **kwargs, height=500, markers=True)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "散布図":
        c1, c2, c3, c4 = st.columns(4)
        x_col = c1.selectbox("X 軸", num_cols) if num_cols else None
        y_col = c2.selectbox("Y 軸", num_cols[1:] if len(num_cols) > 1 else num_cols) if num_cols else None
        color_col = c3.selectbox("色分け", ["なし"] + cat_cols)
        size_col = c4.selectbox("サイズ", ["なし"] + num_cols)

        if x_col and y_col:
            kwargs = dict(x=x_col, y=y_col, title=f"{x_col} vs {y_col}", opacity=0.7)
            if color_col != "なし":
                kwargs["color"] = color_col
            if size_col != "なし":
                kwargs["size"] = size_col
                kwargs["size_max"] = 30
            fig = px.scatter(df, **kwargs, height=500)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "ヒストグラム":
        c1, c2, c3 = st.columns(3)
        x_col = c1.selectbox("列", num_cols) if num_cols else None
        color_col = c2.selectbox("色分け", ["なし"] + cat_cols)
        nbins = c3.slider("ビン数", 5, 100, 30)

        if x_col:
            kwargs = dict(x=x_col, nbins=nbins, title=f"{x_col} の分布", opacity=0.8)
            if color_col != "なし":
                kwargs["color"] = color_col
                kwargs["barmode"] = "overlay"
            fig = px.histogram(df, **kwargs, height=500)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "箱ひげ図":
        c1, c2 = st.columns(2)
        y_col = c1.selectbox("数値列", num_cols) if num_cols else None
        x_col = c2.selectbox("グループ列", ["なし"] + cat_cols)

        if y_col:
            kwargs = dict(y=y_col, title=f"{y_col} の分布", points="outliers")
            if x_col != "なし":
                kwargs["x"] = x_col
                kwargs["color"] = x_col
            fig = px.box(df, **kwargs, height=500)
            st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "円グラフ":
        c1, c2 = st.columns(2)
        name_col = c1.selectbox("ラベル列", cat_cols) if cat_cols else None
        val_col = c2.selectbox("値列 (空白=件数)", ["件数"] + num_cols)

        if name_col:
            if val_col == "件数":
                pie_df = df[name_col].value_counts().reset_index()
                pie_df.columns = [name_col, "count"]
                fig = px.pie(pie_df, names=name_col, values="count", title=f"{name_col} の割合", height=500)
            else:
                pie_df = df.groupby(name_col)[val_col].sum().reset_index()
                fig = px.pie(pie_df, names=name_col, values=val_col, title=f"{name_col} 別 {val_col}", height=500)
            st.plotly_chart(fig, use_container_width=True)

with tab_heatmap:
    if len(num_cols) < 2:
        st.warning("相関ヒートマップには数値列が 2 列以上必要です。")
    else:
        corr = df[num_cols].corr()
        fig = go.Figure(
            data=go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                colorscale="RdBu",
                zmid=0,
                text=[[f"{v:.2f}" for v in row] for row in corr.values],
                texttemplate="%{text}",
                textfont={"size": 12},
                hoverongaps=False,
            )
        )
        fig.update_layout(
            title="数値列の相関係数ヒートマップ",
            height=max(400, len(num_cols) * 60),
            xaxis_showgrid=False,
            yaxis_showgrid=False,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("値が +1 に近いほど正の相関、-1 に近いほど負の相関を示します。")

with tab_raw:
    st.subheader("データプレビュー")

    c1, c2 = st.columns([3, 1])
    search_term = c1.text_input("検索 (部分一致)", placeholder="キーワードを入力...")
    sort_col = c2.selectbox("ソート列", ["なし"] + df.columns.tolist())

    display_df = df.copy()
    if search_term:
        mask = display_df.astype(str).apply(lambda col: col.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    if sort_col != "なし":
        asc = st.checkbox("昇順", value=True)
        display_df = display_df.sort_values(sort_col, ascending=asc)

    st.caption(f"{len(display_df):,} 行表示中")
    st.dataframe(display_df, use_container_width=True, height=450)

    csv_bytes = display_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="CSV としてダウンロード",
        data=csv_bytes,
        file_name="dataview_export.csv",
        mime="text/csv",
    )
