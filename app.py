import pandas as pd
import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

from src.data_processing import run_data_processing
from src.facebook_crawling import run_facebook_crawling
from src.sentiment_analysis import run_sentiment_analysis
from src.sentiment_charts import (
    render_post_overview_chart,
    render_sentiment_pie_chart,
    render_wordcloud,
)


def configure_streamlit():
    try:
        if get_script_run_ctx() is None:
            st.set_option("deprecation.showPyplotGlobalUse", False)
    except Exception:
        pass

    st.set_page_config(
        page_title="Facebook Sentiment Analysis",
        layout="centered",
        initial_sidebar_state="collapsed",
    )


def handle_link_input():
    links_input = st.text_area("📌 Dán link bài viết Facebook (mỗi dòng 1 link):")
    uploaded_file = st.file_uploader(
        "📁 Hoặc tải lên file chứa link (.txt hoặc .csv)", type=["txt", "csv"]
    )

    post_links = [link.strip() for link in links_input.splitlines() if link.strip()]

    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".txt"):
                content = uploaded_file.read().decode("utf-8")
                file_links = [
                    line.strip() for line in content.splitlines() if line.strip()
                ]
            else:
                df_file = pd.read_csv(uploaded_file)
                file_links = df_file.iloc[:, 0].dropna().astype(str).tolist()
            post_links.extend(file_links)
        except Exception:
            st.error("❌ Không thể đọc file. Vui lòng kiểm tra định dạng và nội dung.")

    return post_links


def run_analysis(post_links):
    if not post_links:
        st.warning("⚠️ Bạn cần nhập ít nhất một liên kết từ textarea hoặc từ file.")
        return

    try:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🔍 Đang crawl dữ liệu từ Facebook...")

        def update_progress(current, total):
            percent = int((current / total) * 25)
            progress_bar.progress(percent)

        df_posts, df_comments = run_facebook_crawling(
            post_links, on_progress=update_progress
        )

        progress_bar.progress(50)
        status_text.text("🧼 Đang làm sạch dữ liệu...")
        df_posts_cleaned, df_comments_cleaned = run_data_processing(
            df_posts, df_comments
        )

        progress_bar.progress(75)
        status_text.text("🤖 Đang phân tích cảm xúc...")
        df_comments_with_sentiment = run_sentiment_analysis(df_comments_cleaned)

        progress_bar.progress(100)
        status_text.text("✅ Phân tích cảm xúc hoàn tất!")

        st.session_state.df_posts_cleaned = df_posts_cleaned
        st.session_state.df_comments_with_sentiment = df_comments_with_sentiment

    except Exception as e:
        st.error("❌ Có lỗi xảy ra:")
        st.error(str(e))


def render_sentiment_filter(df):
    st.markdown("### 🎯 Lọc theo cảm xúc:")
    col1, col2, col3, col4 = st.columns(4)

    st.session_state.setdefault("selected_sentiment", "Tất cả")
    available_sentiments = df["sentiment"].unique().tolist()

    with col1:
        if st.button("⭐ Tất cả", key="all_btn"):
            st.session_state.selected_sentiment = "Tất cả"
            st.rerun()

    sentiments = {
        "Tích cực": "😊 Tích cực",
        "Tiêu cực": "😞 Tiêu cực",
        "Trung tính": "😐 Trung tính",
    }

    for i, (key, label) in enumerate(sentiments.items()):
        if key in available_sentiments:
            with [col2, col3, col4][i]:
                if st.button(label, key=f"{key}_btn"):
                    st.session_state.selected_sentiment = key
                    st.rerun()

    other_sentiments = [s for s in available_sentiments if s not in sentiments]
    if other_sentiments:
        selected_other = st.selectbox(
            "Hoặc chọn cảm xúc khác:",
            ["Không chọn"] + other_sentiments,
            key="other_sentiment_select",
        )
        if selected_other != "Không chọn":
            st.session_state.selected_sentiment = selected_other
            st.rerun()


def render_results_table(filtered_df):
    display_columns = ["comment", "sentiment"]
    available_columns = [col for col in display_columns if col in filtered_df.columns]

    if not available_columns or filtered_df.empty:
        return False

    filtered_df = filtered_df[filtered_df["comment"].astype(str).str.strip() != ""]

    if filtered_df.empty:
        st.warning("⚠️ Không có bình luận để hiển thị.")
        return True

    st.dataframe(filtered_df[available_columns], use_container_width=True)

    csv = filtered_df.to_csv(index=False)
    filename = f"sentiment_results_{st.session_state.selected_sentiment.lower().replace(' ', '_')}.csv"

    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.download_button(
            f"📥 Tải kết quả CSV ({st.session_state.selected_sentiment})",
            data=csv,
            file_name=filename,
            mime="text/csv",
        )

    return True


def check_empty_comments(df_comments_with_sentiment):
    df_comments_with_sentiment = df_comments_with_sentiment[
        df_comments_with_sentiment["comment"].astype(str).str.strip() != ""
    ]

    if df_comments_with_sentiment.empty:
        return True

    return False


def render_sentiment_stats(
    df_posts_cleaned, df_comments_with_sentiment, comment_checked
):
    st.markdown("### 📊 Thống kê tổng quan:")
    sentiment_counts = df_comments_with_sentiment["sentiment"].value_counts()

    render_post_overview_chart(df_posts_cleaned)

    render_sentiment_pie_chart(sentiment_counts, comment_checked)

    render_wordcloud(df_comments_with_sentiment)


def display_results(df_posts_cleaned, df_comments_with_sentiment):
    if df_comments_with_sentiment is None or df_comments_with_sentiment.empty:
        st.error("❌ Không có dữ liệu để hiển thị.")
        return

    st.markdown("### 🔎 Kết quả:")
    if "sentiment" not in df_comments_with_sentiment.columns:
        st.error("❌ Không tìm thấy cột 'sentiment' trong dữ liệu.")
        return

    render_sentiment_filter(df_comments_with_sentiment)
    selected = st.session_state.selected_sentiment
    st.info(f"Đang hiển thị: **{selected}**")

    filtered_df = (
        df_comments_with_sentiment
        if selected == "Tất cả"
        else df_comments_with_sentiment[
            df_comments_with_sentiment["sentiment"] == selected
        ]
    )

    comment_checked = check_empty_comments(df_comments_with_sentiment)

    if not comment_checked:
        st.markdown(
            f"**Hiển thị {len(filtered_df)} / {len(df_comments_with_sentiment)} bình luận**"
        )

    if not filtered_df.empty:
        displayed = render_results_table(filtered_df)
        if displayed:
            render_sentiment_stats(
                df_posts_cleaned, df_comments_with_sentiment, comment_checked
            )
        else:
            st.error("❌ Không tìm thấy các cột dữ liệu cần thiết.")
    else:
        st.warning(f"❌ Không có bình luận nào có cảm xúc '{selected}'")


def main():
    configure_streamlit()
    st.title("Facebook Sentiment Analysis")
    st.markdown(
        "Nhập các liên kết bài viết Facebook để thực hiện phân tích cảm xúc bình luận."
    )

    post_links = handle_link_input()

    _, col2, _ = st.columns([1.3, 1, 1])
    with col2:
        clicked = st.button("🚀 Phân tích")

    if clicked:
        run_analysis(post_links)

    if "df_comments_with_sentiment" in st.session_state:
        display_results(
            st.session_state.df_posts_cleaned,
            st.session_state.df_comments_with_sentiment,
        )


if __name__ == "__main__":
    main()
