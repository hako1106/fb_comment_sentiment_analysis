import re

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from underthesea import word_tokenize
from wordcloud import WordCloud


def render_post_overview_chart(df_posts):
    if df_posts is None or df_posts.empty:
        st.warning("⚠️ Không có dữ liệu bài viết để hiển thị biểu đồ.")
        return

    metrics = ["reactions_count", "shares_count", "total_comments_crawled"]
    metric_name_map = {
        "reactions_count": "Lượt cảm xúc",
        "shares_count": "Lượt chia sẻ",
        "total_comments_crawled": "Lượt bình luận",
    }

    df_chart = df_posts[["content"] + metrics].copy()
    df_chart = df_chart.melt(id_vars="content", var_name="Loại", value_name="Số lượng")
    df_chart["Loại"] = df_chart["Loại"].replace(metric_name_map)
    df_chart["Bài viết #"] = df_chart.groupby("content", sort=False).ngroup() + 1
    df_chart["Nội dung"] = df_chart["content"].apply(
        lambda x: x[:100] + "..." if len(x) > 100 else x
    )

    fig = px.bar(
        df_chart,
        x="Bài viết #",
        y="Số lượng",
        color="Loại",
        barmode="stack",
        hover_data={"Nội dung": True, "Bài viết #": False},
    )

    fig.update_layout(
        xaxis_title="Bài viết",
        yaxis_title="Số lượng",
        legend_title="Loại tương tác",
        xaxis=dict(tickmode="linear"),
        height=500,
    )

    st.markdown("#### Tổng quan tương tác bài viết")
    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_pie_chart(sentiment_counts, comment_checked):
    if sentiment_counts.empty or comment_checked:
        st.warning("⚠️ Không có dữ liệu cảm xúc để hiển thị.")
        return

    df = sentiment_counts.reset_index()
    df.columns = ["Cảm xúc", "Số lượng"]

    color_map = {
        "Tích cực": "#28a745",
        "Tiêu cực": "#dc3545",
        "Trung tính": "#6c757d",
    }

    fig = px.pie(
        df,
        names="Cảm xúc",
        values="Số lượng",
        color="Cảm xúc",
        color_discrete_map=color_map,
        hole=0,
    )

    fig.update_traces(
        textinfo="percent+label",
        textfont_size=14,
    )
    fig.update_layout(
        showlegend=True,
        height=450,
    )

    st.markdown("#### Phân bố cảm xúc")
    st.plotly_chart(fig, use_container_width=True)


def load_vietnamese_stopwords(path="vietnamese_stopwords.txt"):
    with open(path, encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def preprocess_text_vi(text, stopwords_vi):
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = word_tokenize(text, format="text").split()

    filtered = [word for word in tokens if word not in stopwords_vi]

    return " ".join(filtered)


def render_wordcloud(df_comments_with_sentiment):
    if df_comments_with_sentiment is None or df_comments_with_sentiment.empty:
        st.warning("⚠️ Không có dữ liệu để tạo WordCloud.")
        return

    sentiments_available = df_comments_with_sentiment["sentiment"].unique().tolist()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("#### WordCloud cho cảm xúc:")
    with col2:
        sentiment_label = st.selectbox(
            "Chọn cảm xúc cho WordCloud",
            ["Tất cả"] + sentiments_available,
            index=0,
            label_visibility="collapsed",
        )

    if sentiment_label != "Tất cả":
        df_filtered = df_comments_with_sentiment[
            df_comments_with_sentiment["sentiment"] == sentiment_label
        ]
    else:
        df_filtered = df_comments_with_sentiment

    if df_filtered.empty:
        st.warning(
            f"⚠️ Không có bình luận nào với cảm xúc '{sentiment_label}' để tạo WordCloud."
        )
        return

    comments = df_filtered["comment"].astype(str)
    stopwords_vi = load_vietnamese_stopwords()
    processed_comments = comments.apply(lambda x: preprocess_text_vi(x, stopwords_vi))
    text = " ".join(processed_comments).replace("_", " ")

    if not text.strip():
        st.warning("⚠️ Không có dữ liệu để tạo WordCloud")
        return

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        font_path="arial.ttf",
        colormap="viridis",
        max_words=200,
    ).generate(text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
