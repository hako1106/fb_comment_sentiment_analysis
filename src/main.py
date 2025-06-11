from data_processing import run_data_processing
from facebook_crawling import run_facebook_crawling
from sentiment_analysis import run_sentiment_analysis


def main():
    post_links = []
    print("Enter Facebook post links (type 'done' when finished):")
    while True:
        link = input("Link: ").strip()
        if link.lower() == "done":
            break
        if link:
            post_links.append(link)

    df_posts, df_comments = run_facebook_crawling(post_links)

    df_posts_processed, df_comments_processed = run_data_processing(
        df_posts, df_comments
    )

    df_comments_processed_with_sentiment = run_sentiment_analysis(df_comments_processed)

    print(
        "\nData processing completed. Here are the first few rows of the processed posts:"
    )
    print(df_posts_processed[["url", "content", "total_engagement"]].head())

    print(
        "\nSentiment analysis completed. Here are the first few rows of the processed data:"
    )
    print(df_comments_processed_with_sentiment[["comment", "sentiment"]].head())


if __name__ == "__main__":
    main()
