import json
import os
import sys
from pathlib import Path

import feedparser
import requests


BASE_DIR = Path(__file__).resolve().parent
FEEDS_FILE = BASE_DIR / "feeds.json"
POSTED_FILE = BASE_DIR / "posted_articles.json"
ENV_FILE = BASE_DIR / ".env"


def load_dotenv():
    if not ENV_FILE.exists():
        return

    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_feeds():
    if not FEEDS_FILE.exists():
        raise FileNotFoundError("feeds.json が見つかりません。")

    with FEEDS_FILE.open("r", encoding="utf-8") as file:
        feeds = json.load(file)

    if not isinstance(feeds, list):
        raise ValueError("feeds.json は配列形式にしてください。")

    return feeds


def load_posted_urls():
    if not POSTED_FILE.exists():
        return set()

    with POSTED_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data.get("posted_articles", []))


def save_posted_urls(posted_urls):
    data = {"posted_articles": sorted(posted_urls)}
    with POSTED_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def get_article_key(entry):
    return entry.get("link") or entry.get("id")


def get_latest_article(feed):
    parsed = feedparser.parse(feed["url"])

    if not parsed.entries:
        print(f"[INFO] 記事が見つかりませんでした: {feed['name']}")
        return None

    entry = parsed.entries[0]
    title = entry.get("title", "No title").strip()
    url = entry.get("link", "").strip()
    key = get_article_key(entry)

    if not key or not url:
        print(f"[WARN] タイトルまたはURLが不足しています: {feed['name']}")
        return None

    return {"title": title, "url": url, "key": key}


def post_to_discord(webhook_url, article):
    message = f":icon:SINGULARITY FEED:icon:\n\n{article['title']}\n{article['url']}"
    response = requests.post(
        webhook_url,
        json={"content": message},
        timeout=20,
    )
    response.raise_for_status()


def main():
    load_dotenv()

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL が設定されていません。")
        print("ローカルでは .env、GitHub Actionsでは GitHub Secrets に設定してください。")
        return 1

    feeds = load_feeds()
    posted_urls = load_posted_urls()
    posted_count_before = len(posted_urls)

    for feed in feeds:
        if feed.get("disabled", False):
            print(f"[SKIP] 無効化中: {feed.get('name', '名前なし')}")
            continue

        try:
            article = get_latest_article(feed)
            if not article:
                continue

            if article["key"] in posted_urls:
                print(f"[OK] 投稿済み: {article['title']}")
                continue

            post_to_discord(webhook_url, article)
            posted_urls.add(article["key"])
            print(f"[POSTED] {feed['name']}: {article['title']}")

        except Exception as error:
            print(f"[ERROR] {feed.get('name', '名前なし')}: {error}")

    if len(posted_urls) != posted_count_before:
        save_posted_urls(posted_urls)
        print("[OK] posted_articles.json を更新しました。")
    else:
        print("[OK] 新しい投稿はありませんでした。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
