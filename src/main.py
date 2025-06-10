from data_cleaning import run_data_cleaning
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

    run_facebook_crawling(post_links)

    run_data_cleaning()

    df = run_sentiment_analysis()

    print(
        "\nSentiment analysis completed. Here are the first few rows of the processed data:"
    )
    print(df[["comment_text_remove_emojis", "sentiment"]].head())


if __name__ == "__main__":
    main()
