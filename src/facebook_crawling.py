import random
import re
import time
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright


def setup_browser_context(browser: Browser) -> BrowserContext:
    """Create a browser context with custom viewport and user-agent."""

    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    return context


def wait_for_page_load(page: Page, timeout: int = 10) -> None:
    """Wait until the page finishes loading."""

    try:
        page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        # time.sleep(random.uniform(1, 2))
    except Exception:
        time.sleep(2)
        raise


def extract_engagement_metrics(page: Page) -> Dict[str, int]:
    """Extract reaction, comment, and share counts from the post."""

    metrics = {
        "reactions_count": 0,
        "comments_count": 0,
        "shares_count": 0,
    }

    reaction_selectors = ['span[aria-hidden="true"] span span']

    comment_selectors = ['span:has-text("comments")', 'span:has-text("bình luận")']

    share_selectors = [
        'span:has-text("shares")',
        'span:has-text("chia sẻ")',
        'span:has-text("lượt chia sẻ")',
    ]

    for selector in reaction_selectors:
        try:
            page.wait_for_selector(selector, timeout=15000)
            element = page.locator(selector).first
            text = element.inner_text(timeout=1000).strip()
            if not text:
                continue

            if re.fullmatch(r"(\d[\d,]*)", text):
                numbers = re.findall(r"(\d[\d,]*)", text)
                if numbers:
                    val = int(numbers[0].replace(",", ""))
                    metrics["reactions_count"] = max(metrics["reactions_count"], val)
                    break
            elif "K" in text.upper() or "M" in text.upper():
                numbers = re.findall(r"(\d+(?:[.,]\d+)?)", text)
                if numbers:
                    num_str = numbers[0].replace(",", ".")
                    if "K" in text.upper():
                        val = float(num_str) * 1000
                    else:  # 'M'
                        val = float(num_str) * 1000000
                    metrics["reactions_count"] = max(
                        metrics["reactions_count"], int(val)
                    )
                    break
        except Exception:
            raise

    for selector in comment_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                text = element.inner_text(timeout=1000).strip()
                numbers = re.findall(r"(\d[\d,]*)", text)
                if numbers:
                    metrics["comments_count"] = max(
                        metrics["comments_count"], int(numbers[0].replace(",", ""))
                    )
                    break
        except Exception:
            raise

    for selector in share_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                text = element.inner_text(timeout=1000).strip()
                numbers = re.findall(r"(\d[\d,]*)", text)
                if numbers:
                    metrics["shares_count"] = max(
                        metrics["shares_count"], int(numbers[0].replace(",", ""))
                    )
                    break
        except Exception:
            raise

    return metrics


def extract_post_content(page: Page) -> str:
    """Extract main text content of the Facebook post."""

    try:
        element = page.locator('[data-ad-preview="message"]').first
        if element.is_visible():
            content = element.inner_text(timeout=3000)
            if content and len(content) > 0:
                return content.strip()
    except Exception:
        raise
    return ""


def extract_post_metadata(page: Page) -> Dict[str, str]:
    """Extract post metadata like author name."""

    metadata = {"author": ""}

    try:
        author_selectors = [
            'div[data-ad-rendering-role="profile_name"] h3 a[role="link"]'
        ]

        for selector in author_selectors:
            try:
                author_elem = page.locator(selector).first
                if author_elem.count() > 0:
                    metadata["author"] = author_elem.inner_text()
                    break
            except Exception:
                continue

    except Exception as e:
        print(f"Error extracting metadata: {e}")

    return metadata


def extract_comments(page: Page) -> List[Dict[str, str]]:
    """Extract visible comments from the post area."""

    comments = []

    try:
        # Click the "Most relevant" button
        try:
            most_relevant = page.locator('span:has-text("Most relevant")').first
            if most_relevant.count() > 0:
                most_relevant.click()
                time.sleep(1)
        except Exception:
            print("Could not find or click 'Most relevant'.")
            raise

        # Click "All comments" if available
        try:
            all_comments_btn = page.locator(
                'span:has-text("Show all comments, including potential spam.")'
            ).first
            if all_comments_btn.count() > 0:
                all_comments_btn.click()
                time.sleep(2)
        except Exception:
            print("Could not find or click 'All comments'.")
            raise

        # Scroll down to load all comments
        try:
            scrollable_container = page.locator(
                "div.xb57i2i.x1q594ok.x5lxg6s.x78zum5.xdt5ytf.x6ikm8r.x1ja2u2z.x1pq812k.x1rohswg"
                ".xfk6m8.x1yqm8si.xjx87ck.xx8ngbg.xwo3gff.x1n2onr6.x1oyok0e.x1odjw0f.x1iyjqo2.xy5w88m"
            ).first
            previous_height = scrollable_container.evaluate("(el) => el.scrollHeight")

            for _ in range(1000):
                scrollable_container.evaluate("(el) => el.scrollBy(0, 1500)")
                time.sleep(random.uniform(1, 2))

                current_height = scrollable_container.evaluate(
                    "(el) => el.scrollHeight"
                )
                if current_height == previous_height:
                    scrollable_container.evaluate("(el) => el.scrollBy(0, 2500)")
                    time.sleep(random.uniform(1, 2))

                    current_height = scrollable_container.evaluate(
                        "(el) => el.scrollHeight"
                    )
                    if current_height == previous_height:
                        break

                previous_height = current_height
        except Exception as e:
            print(f"Scroll error: {e}")
            raise

        # Extract comments
        comment_elements = page.locator(
            "div.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.x18d9i69.x1g0dm76.xpdmqnj.x1n2onr6 "
            'div[dir="auto"][style="text-align: start;"]'
        ).all()

        for el in comment_elements:
            try:
                # Extract main text
                comment_text = el.inner_text().strip()

                # Add emojis (if any)
                emojis = el.locator("img[alt]").all()
                for emoji in emojis:
                    alt = emoji.get_attribute("alt")
                    if alt:
                        comment_text += f" {alt}"

                # Append to list
                comments.append(
                    {
                        "comments_text": comment_text,
                    }
                )

            except Exception:
                continue

    except Exception as e:
        print(f"Error extracting comments: {e}")

    return comments


def crawl_facebook_post(page: Page, url: str) -> Dict[str, Any]:
    """Crawl all post data including content, metadata, and comments."""

    try:
        page.goto(url, timeout=30000)
        wait_for_page_load(page)

        # Extract data
        content = extract_post_content(page)
        metadata = extract_post_metadata(page)
        metrics = extract_engagement_metrics(page)
        comments = extract_comments(page)

        result = {
            "url": url,
            "author": metadata["author"],
            "content": content,
            "reactions_count": metrics["reactions_count"],
            "comments_count": metrics["comments_count"],
            "shares_count": metrics["shares_count"],
            "comments": comments,
        }

        return result

    except Exception as e:
        print(f"Error crawling {url}: {e}")

        return {
            "url": url,
            "author": "",
            "content": "",
            "reactions_count": 0,
            "comments_count": 0,
            "shares_count": 0,
            "comments": [],
            "error": str(e),
        }


def check_post_links(post_links: Optional[List[str]] = None) -> bool:
    """Validate the format of Facebook post URLs."""

    if not post_links:
        print("No links were entered!")
        return False
    for link in post_links:
        if not re.match(r"https?://www\.facebook\.com/[^/]+/posts/[^/?]+", link):
            print(f"Invalid link format: {link}")
            return False
    return True


def run_facebook_crawling(
    post_links: Optional[List[str]] = None,
) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """Crawl multiple Facebook posts and return their data as DataFrames."""

    print("\nCrawling data from Facebook posts...")

    if not check_post_links(post_links):
        return None, None

    posts_summary = []
    all_comments = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-blink-features=AutomationControlled"],
            )
            try:
                context = setup_browser_context(browser)
                page = context.new_page()
                page.on("dialog", lambda dialog: dialog.accept())

                for i, url in enumerate(post_links, 1):
                    data = crawl_facebook_post(page, url)

                    posts_summary.append(
                        {
                            "url": data["url"],
                            "author": data["author"],
                            "content": data["content"],
                            "reactions_count": data["reactions_count"],
                            "comments_count": data["comments_count"],
                            "shares_count": data["shares_count"],
                            "total_comments_crawled": len(data["comments"]),
                        }
                    )

                    all_comments.extend(
                        [
                            {"url": data["url"], "comment_text": c["comments_text"]}
                            for c in data["comments"]
                        ]
                    )

                    if i < len(post_links):
                        time.sleep(random.uniform(1, 2))
            finally:
                browser.close()

        df_posts = pd.DataFrame(posts_summary)
        df_comments = pd.DataFrame(all_comments)

        return df_posts, df_comments

    except Exception as e:
        print(f"Error during crawling: {e}")
        raise e


if __name__ == "__main__":
    post_links = []
    print("Enter Facebook post links (type 'done' when finished):")
    while True:
        link = input("Link: ").strip()
        if link.lower() == "done":
            break
        if link:
            post_links.append(link)

    df_posts, df_comments = run_facebook_crawling(post_links)

    print("\nCrawling completed!")
    print("Statistics:")
    print(f"   - Total posts: {len(df_posts)}")
    print(f"   - Total comments: {len(df_comments)}")
    total_reactions = df_posts["reactions_count"].fillna(0).sum()
    total_shares = df_posts["shares_count"].fillna(0).sum()
    print(f"   - Total reactions: {int(total_reactions)}")
    print(f"   - Total shares: {int(total_shares)}")
