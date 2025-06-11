import streamlit as st

from src.data_processing import run_data_processing
from src.facebook_crawling import run_facebook_crawling
from src.sentiment_analysis import run_sentiment_analysis


# ==============================
# Cấu hình Streamlit và khắc phục lỗi context
# ==============================
def configure_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is None:
            st.set_option("deprecation.showPyplotGlobalUse", False)
    except Exception:
        pass
    st.set_page_config(
        page_title="Facebook Sentiment Analysis",
        layout="centered",
        initial_sidebar_state="collapsed",
    )


# ==============================
# Hàm chính
# ==============================
def main():
    configure_streamlit()
    st.title("🧠 Facebook Sentiment Analysis")
    st.markdown(
        "Nhập các liên kết bài viết Facebook để thực hiện phân tích cảm xúc bình luận."
    )

    links_input = st.text_area("📌 Dán link bài viết Facebook (mỗi dòng 1 link):")

    if st.button("🚀 Phân tích"):
        post_links = [link.strip() for link in links_input.splitlines() if link.strip()]
        if not post_links:
            st.warning("⚠️ Bạn cần nhập ít nhất một liên kết.")
            return

        try:
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Bước 1: Crawl dữ liệu
            status_text.text("🔍 Đang crawl dữ liệu từ Facebook...")
            df_posts, df_comments = run_facebook_crawling(post_links)
            progress_bar.progress(25)

            # Bước 2: Làm sạch dữ liệu
            status_text.text("🧼 Đang làm sạch dữ liệu...")
            df_posts_processed, df_comments_processed = run_data_processing(
                df_posts, df_comments
            )
            progress_bar.progress(50)

            # Bước 3: Phân tích cảm xúc
            status_text.text("🤖 Đang phân tích cảm xúc...")
            df_comments_processed_with_sentiment = run_sentiment_analysis(
                df_comments_processed
            )
            progress_bar.progress(75)

            # Hoàn tất
            progress_bar.progress(100)
            status_text.text("✅ Phân tích cảm xúc hoàn tất!")
            st.success("✅ Phân tích cảm xúc hoàn tất!")

            # Lưu kết quả vào session state
            st.session_state.df_results = df_comments_processed_with_sentiment

        except Exception as e:
            st.error("❌ Có lỗi xảy ra:")
            st.error(str(e))

    # Hiển thị kết quả nếu có dữ liệu
    if "df_results" in st.session_state and st.session_state.df_results is not None:
        display_results(st.session_state.df_results)


# ==============================
# Hàm hiển thị kết quả với chức năng lọc
# ==============================
def display_results(df):
    if df is None or df.empty:
        st.error("❌ Không có dữ liệu để hiển thị.")
        return

    st.markdown("### 🔎 Kết quả:")

    # Kiểm tra xem có cột sentiment không
    if "sentiment" not in df.columns:
        st.error("❌ Không tìm thấy cột 'sentiment' trong dữ liệu.")
        return

    # Lấy danh sách các loại cảm xúc có trong dữ liệu
    available_sentiments = df["sentiment"].unique().tolist()

    # Tạo section lọc cảm xúc
    st.markdown("### 🎯 Lọc theo cảm xúc:")

    # Tạo các nút lọc theo hàng ngang
    col1, col2, col3, col4 = st.columns(4)

    # Khởi tạo session state cho filter nếu chưa có
    if "selected_sentiment" not in st.session_state:
        st.session_state.selected_sentiment = "Tất cả"

    # Nút "Tất cả"
    with col1:
        if st.button("📊 Tất cả", key="all_sentiments"):
            st.session_state.selected_sentiment = "Tất cả"

    # Nút cho từng loại cảm xúc (tối đa 3 nút còn lại)
    sentiment_buttons = {
        "positive": ("😊 Tích cực", "positive_btn"),
        "negative": ("😞 Tiêu cực", "negative_btn"),
        "neutral": ("😐 Trung tính", "neutral_btn"),
    }

    cols = [col2, col3, col4]
    for i, (sentiment_key, (button_text, button_key)) in enumerate(
        sentiment_buttons.items()
    ):
        if i < len(cols) and sentiment_key in available_sentiments:
            with cols[i]:
                if st.button(button_text, key=button_key):
                    st.session_state.selected_sentiment = sentiment_key

    # Thêm selectbox để lọc nếu có nhiều loại cảm xúc khác
    other_sentiments = [
        s for s in available_sentiments if s not in sentiment_buttons.keys()
    ]
    if other_sentiments:
        st.selectbox(
            "Hoặc chọn cảm xúc khác:",
            ["Không chọn"] + other_sentiments,
            key="other_sentiment_select",
        )
        if st.session_state.other_sentiment_select != "Không chọn":
            st.session_state.selected_sentiment = (
                st.session_state.other_sentiment_select
            )

    # Hiển thị cảm xúc đang được chọn
    st.info(f"🎯 Đang hiển thị: **{st.session_state.selected_sentiment}**")

    # Lọc dữ liệu theo cảm xúc được chọn
    if st.session_state.selected_sentiment == "Tất cả":
        filtered_df = df
    else:
        filtered_df = df[df["sentiment"] == st.session_state.selected_sentiment]

    # Hiển thị số lượng kết quả
    total_count = len(df)
    filtered_count = len(filtered_df)
    st.markdown(f"**Hiển thị {filtered_count} / {total_count} bình luận**")

    # Hiển thị bảng dữ liệu đã lọc
    display_columns = ["comment_text_remove_emojis", "sentiment"]
    available_columns = [col for col in display_columns if col in filtered_df.columns]

    if available_columns and not filtered_df.empty:
        st.dataframe(filtered_df[available_columns], use_container_width=True)

        # Nút tải CSV cho dữ liệu đã lọc
        csv = filtered_df.to_csv(index=False)
        filename = f"sentiment_results_{st.session_state.selected_sentiment.lower().replace(' ', '_')}.csv"
        st.download_button(
            f"📥 Tải kết quả CSV ({st.session_state.selected_sentiment})",
            data=csv,
            file_name=filename,
            mime="text/csv",
        )

        # Biểu đồ thống kê tổng quan (luôn hiển thị tất cả)
        st.markdown("### 📊 Thống kê tổng quan cảm xúc:")
        sentiment_counts = df["sentiment"].value_counts()

        # Tạo 2 cột để hiển thị biểu đồ và thống kê số
        chart_col, stats_col = st.columns([2, 1])

        with chart_col:
            st.bar_chart(sentiment_counts)

        with stats_col:
            st.markdown("**Số lượng:**")
            for sentiment, count in sentiment_counts.items():
                percentage = (count / total_count) * 100
                st.markdown(f"• {sentiment}: {count} ({percentage:.1f}%)")

    elif filtered_df.empty:
        st.warning(
            f"❌ Không có bình luận nào có cảm xúc '{st.session_state.selected_sentiment}'"
        )

    else:
        st.error("❌ Không tìm thấy các cột dữ liệu cần thiết.")


# ==============================
# Chạy ứng dụng
# ==============================
if __name__ == "__main__":
    main()
