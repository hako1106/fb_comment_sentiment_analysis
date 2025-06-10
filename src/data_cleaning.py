import pandas as pd
import emoji


def load_and_clean_posts(
        post_path: str,
        output_path: str = 'data/processed/facebook_posts_processed.csv'
) -> pd.DataFrame:
    """Đọc và xử lý file facebook_posts.csv"""
    df_post = pd.read_csv(post_path)

    df_post.loc[df_post['content'].isna(), 'content'] = "Cập nhật ảnh bìa"

    df_post['total_engagement'] = (
        df_post['reactions_count'] +
        df_post['shares_count'] +
        df_post['comments_count']
    )

    df_post.to_csv(output_path, index=False)
    return df_post


def load_and_clean_comments(
        comment_path: str,
        output_path: str = 'data/processed/facebook_comments_processed.csv'
) -> pd.DataFrame:
    """Đọc, loại bỏ trùng lặp và emoji trong facebook_comments.csv"""
    df_comments = pd.read_csv(comment_path)

    df_comments = df_comments.drop_duplicates(subset=['url', 'comment_text']).copy()

    df_comments['comment_text_remove_emojis'] = df_comments['comment_text'].apply(
        lambda text: emoji.replace_emoji(text, replace='')
    )

    df_comments.to_csv(output_path, index=False)
    return df_comments


def run_data_cleaning(
    post_path: str = 'data/crawl/facebook_posts.csv',
    comment_path: str = 'data/crawl/facebook_comments.csv'
):
    """Chạy quá trình xử lý dữ liệu"""
    print("\nCleaning data crawled...")
    df_post = load_and_clean_posts(post_path)
    df_comments = load_and_clean_comments(comment_path)

    return df_post, df_comments


if __name__ == "__main__":
    df_post, df_comments = run_data_cleaning()
