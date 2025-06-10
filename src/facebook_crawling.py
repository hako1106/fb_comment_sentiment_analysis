from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re
import random

def setup_browser_context(browser):
    """Set up browser context with optimized settings for Facebook"""
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    return context

def wait_for_page_load(page, timeout=10):
    """Wait for the page to fully load"""
    try:
        page.wait_for_load_state('networkidle', timeout=timeout*1000)
        #time.sleep(random.uniform(1, 2))
    except:
        time.sleep(2)

def extract_engagement_metrics(page):
    """Extracts engagement metrics (reactions, comments, shares) from a social media post."""
    metrics = {
        'reactions_count': 0,
        'comments_count': 0,
        'shares_count': 0,
    }

    reaction_selectors = [
        'span[aria-hidden="true"] span span'        
    ]
    
    comment_selectors = [
        'span:has-text("comments")',
        'span:has-text("bình luận")'
    ]

    share_selectors = [
        'span:has-text("shares")',
        'span:has-text("chia sẻ")',
        'span:has-text("lượt chia sẻ")'
    ]

    for selector in reaction_selectors:
        try:
            page.wait_for_selector(selector, timeout=15000)
            element = page.locator(selector).first
            text = element.inner_text(timeout=1000).strip()
            if not text:
                continue

            if re.fullmatch(r'(\d[\d,]*)', text):
                numbers = re.findall(r'(\d[\d,]*)', text)
                if numbers:
                    val = int(numbers[0].replace(',', ''))
                    metrics['reactions_count'] = max(metrics['reactions_count'], val)
                    break 
            elif 'K' in text.upper() or 'M' in text.upper():
                numbers = re.findall(r'(\d+(?:[.,]\d+)?)', text)
                if numbers:
                    num_str = numbers[0].replace(',', '.')
                    if 'K' in text.upper():
                        val = float(num_str) * 1000
                    else:  # 'M'
                        val = float(num_str) * 1000000
                    metrics['reactions_count'] = max(metrics['reactions_count'], int(val))
                    break 
        except Exception:
            pass 

    for selector in comment_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                text = element.inner_text(timeout=1000).strip()
                numbers = re.findall(r'(\d[\d,]*)', text)
                if numbers:
                    metrics['comments_count'] = max(metrics['comments_count'], int(numbers[0].replace(',', '')))
                    break
        except Exception:
            pass

    for selector in share_selectors:
        try:
            element = page.locator(selector).first
            if element.is_visible():
                text = element.inner_text(timeout=1000).strip()
                numbers = re.findall(r'(\d[\d,]*)', text)
                if numbers:
                    metrics['shares_count'] = max(metrics['shares_count'], int(numbers[0].replace(',', '')))
                    break
        except Exception:
            pass
            
    return metrics

def extract_post_content(page):
    """Extracts the main text content of a social media post."""
    try:
        element = page.locator('[data-ad-preview="message"]').first
        if element.is_visible():
            content = element.inner_text(timeout=3000)
            if content and len(content) > 0:
                return content.strip()
    except:
        pass
    return ""

def extract_post_metadata(page):
    """Extract post metadata (time, author, etc.)"""
    metadata = {
        'author': ''
    }
    
    try:
        author_selectors = [
            'div[data-ad-rendering-role="profile_name"] h3 a[role="link"]'
        ]
        
        for selector in author_selectors:
            try:
                author_elem = page.locator(selector).first
                if author_elem.count() > 0:
                    metadata['author'] = author_elem.inner_text()
                    break
            except:
                continue
                
    except Exception as e:
        print(f"Error extracting metadata: {e}")
    
    return metadata

def extract_comments(page):
    """Extract comments from the post area (not the entire page)"""
    comments = []

    try:
        # Click the "Most relevant" button
        try:
            most_relevant = page.locator('span:has-text("Most relevant")').first
            if most_relevant.count() > 0:
                most_relevant.click()
                time.sleep(1)
        except:
            print("Could not find or click 'Most relevant'.")

        # Click "All comments" if available
        try:
            all_comments_btn = page.locator('span:has-text("Show all comments, including potential spam.")').first
            if all_comments_btn.count() > 0:
                all_comments_btn.click()
                time.sleep(2)
        except:
            print("Could not find or click 'All comments'.")

        # Scroll down to load all comments
        try:
            scrollable_container = page.locator(
                'div.xb57i2i.x1q594ok.x5lxg6s.x78zum5.xdt5ytf.x6ikm8r.x1ja2u2z.x1pq812k.x1rohswg'
                '.xfk6m8.x1yqm8si.xjx87ck.xx8ngbg.xwo3gff.x1n2onr6.x1oyok0e.x1odjw0f.x1iyjqo2.xy5w88m'
            ).first            
            previous_height = scrollable_container.evaluate("(el) => el.scrollHeight")
            
            for _ in range(1000):
                scrollable_container.evaluate("(el) => el.scrollBy(0, 1500)")
                time.sleep(random.uniform(1, 2))

                current_height = scrollable_container.evaluate("(el) => el.scrollHeight")
                if current_height == previous_height:
                    scrollable_container.evaluate("(el) => el.scrollBy(0, 2500)")
                    time.sleep(random.uniform(1, 2))

                    current_height = scrollable_container.evaluate("(el) => el.scrollHeight")
                    if current_height == previous_height:
                        break

                previous_height = current_height
        except Exception as e:
            print(f"Scroll error: {e}")

        # Extract comments
        comment_elements = page.locator(
            'div.html-div.xdj266r.x14z9mp.xat24cr.x1lziwak.xexx8yu.x18d9i69.x1g0dm76.xpdmqnj.x1n2onr6 '
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
                comments.append({
                    "comments_text": comment_text,
                })

            except Exception:
                continue

    except Exception as e:
        print(f"Error extracting comments: {e}")

    return comments


def crawl_facebook_post(page, url):
    """Crawl a complete Facebook post"""    
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
            "author": metadata['author'],
            "content": content,
            "reactions_count": metrics['reactions_count'],
            "comments_count": metrics['comments_count'],
            "shares_count": metrics['shares_count'],
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
    

def check_post_links(post_links=None):
    """Check if post links are valid"""
    if not post_links:
        print("No links were entered!")
        return False
    for link in post_links:
        if not re.match(r'https?://www\.facebook\.com/[^/]+/posts/[^/?]+', link):
            print(f"Invalid link format: {link}")
            return False
    return True


def run_facebook_crawling(post_links=None):
    """Main function to crawl Facebook posts"""
    print("\nCrawling data from Facebook posts...")

    if not check_post_links(post_links):
        return
    else:
        posts_summary = []
        all_comments = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
            )

            context = setup_browser_context(browser)
            page = context.new_page()
            page.on("dialog", lambda dialog: dialog.accept())

            try:
                for i, url in enumerate(post_links, 1):
                    data = crawl_facebook_post(page, url)

                    posts_summary.append({
                        "url": data["url"],
                        "author": data["author"],
                        "content": data["content"],
                        "reactions_count": data["reactions_count"],
                        "comments_count": data["comments_count"],
                        "shares_count": data["shares_count"],
                        "total_comments_crawled": len(data["comments"]),
                    })


                    for comment in data["comments"]:
                        all_comments.append({
                            "url": data["url"],
                            "comment_text": comment["comments_text"],
                        })

                    if i < len(post_links):
                        time.sleep(random.uniform(2, 3))
            finally:
                browser.close()

    summary_df = pd.DataFrame(posts_summary)
    comments_df = pd.DataFrame(all_comments)

    summary_file = f"data/crawl/facebook_posts.csv"
    comments_file = f"data/crawl/facebook_comments.csv"

    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    comments_df.to_csv(comments_file, index=False, encoding='utf-8-sig')

    print(f"\nCrawling completed!")
    print(f"Statistics:")
    print(f"   - Total posts: {len(posts_summary)}")
    print(f"   - Total comments: {len(all_comments)}")
    print(f"   - Total reactions: {sum(post.get('reactions_count', 0) for post in posts_summary)}")
    print(f"   - Total shares: {sum(post.get('shares_count', 0) for post in posts_summary)}")

    
if __name__ == "__main__":
    post_links = []
    print("Enter Facebook post links (type 'done' when finished):")
    while True:
        link = input("Link: ").strip()
        if link.lower() == "done":
            break
        if link:
            post_links.append(link)

    run_facebook_crawling(post_links)