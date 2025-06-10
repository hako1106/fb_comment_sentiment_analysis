from data_cleaning import data_cleaning
from facebook_crawling import facebook_crawling
from sentiment_analysis import sentiment_analysis


def main():
    post_links = []
    print("Enter Facebook post links (type 'done' when finished):")
    while True:
        link = input("Link: ").strip()
        if link.lower() == "done":
            break
        if link:
            post_links.append(link)

    facebook_crawling(post_links)

    data_cleaning()

    df = sentiment_analysis()

    print(
        "\nSentiment analysis completed. Here are the first few rows of the processed data:"
    )
    print(df[["comment_text_remove_emojis", "sentiment"]].head())


if __name__ == "__main__":
    main()
