import re
from typing import Tuple

import emoji
import pandas as pd


def load_and_clean_posts(df_posts: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich the Facebook posts DataFrame."""

    df_posts["content"] = df_posts["content"].fillna("Cập nhật ảnh bìa")

    df_posts["total_engagement"] = (
        df_posts["reactions_count"].fillna(0)
        + df_posts["shares_count"].fillna(0)
        + df_posts["comments_count"].fillna(0)
    )

    return df_posts


def remove_emojis_from_text(text: str) -> str:
    """Remove emojis from a text if it contains letters or digits."""

    if pd.isna(text):
        return text
    text_str = str(text)
    if re.search(r"[A-Za-zÀ-ỹ0-9]", text_str):
        return emoji.replace_emoji(text_str, replace="")
    return text_str


def load_and_clean_comments(df_comments: pd.DataFrame) -> pd.DataFrame:
    """Clean and deduplicate Facebook comments."""

    df_comments = df_comments.drop_duplicates(subset=["url", "comment_text"])

    df_comments["comment"] = df_comments["comment_text"].apply(remove_emojis_from_text)
    df_comments = df_comments.drop(columns=["comment_text"])

    return df_comments


def run_data_processing(
    df_posts: pd.DataFrame,
    df_comments: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Run data cleaning for both posts and comments."""

    print("\nCleaning data crawled...")

    df_posts_processed = load_and_clean_posts(df_posts)
    df_comments_processed = load_and_clean_comments(df_comments)

    return df_posts_processed, df_comments_processed


if __name__ == "__main__":
    df_posts = pd.read_csv("data/crawl/facebook_posts.csv")
    df_comments = pd.read_csv("data/crawl/facebook_comments.csv")

    df_posts_processed, df_comments_processed = run_data_processing(
        df_posts, df_comments
    )

    print("Data cleaning completed.")
    print(f"Posts: \n{df_posts_processed.head()}")
    print(f"\nComments: \n{df_comments_processed.head()}")
