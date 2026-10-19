"""Collect X (Twitter) posts about Config India into data/tweets.csv.

Uses twscrape with your own logged-in X account (cookies from .env).

    python collect.py                       # default queries, posts since 2026-10-08
    python collect.py --limit 500 --since 2026-10-14 --until 2026-10-25
    python collect.py -q '"config india" underwhelming'
"""

import argparse
import asyncio
import csv
import os
from pathlib import Path

from dotenv import load_dotenv
from twscrape import API

DEFAULT_QUERIES = [
    '"config india"',
    "#ConfigIndia",
    "#ConfigIndia2026",
    "figma config bengaluru",
    "figma config bangalore",
    "@figma config india",
]

FIELDS = [
    "id", "url", "date", "username", "display_name", "followers",
    "text", "likes", "retweets", "replies", "quotes", "views", "lang", "query",
]

OUT = Path("data/tweets.csv")


async def ensure_account(api: API) -> None:
    username = os.environ.get("X_USERNAME")
    cookies = os.environ.get("X_COOKIES")
    if not username or not cookies:
        raise SystemExit("Set X_USERNAME and X_COOKIES in .env (see .env.example).")

    existing = {acc.username for acc in await api.pool.get_all()}
    if username not in existing:
        # With cookies, twscrape skips the password login flow; the other fields are unused.
        await api.pool.add_account(username, "unused", "unused@example.com", "unused", cookies=cookies)
    await api.pool.login_all()

    # twscrape waits forever when no account is usable, so fail loudly instead.
    acc = await api.pool.get_account(username)
    if not acc or not acc.active:
        reason = acc.error_msg if acc else "account missing"
        raise SystemExit(
            f"X account @{username} is not logged in ({reason}). Refresh X_COOKIES in .env, "
            f"then run: twscrape del_accounts {username}"
        )


def load_existing() -> dict[str, dict]:
    if not OUT.exists():
        return {}
    with OUT.open(newline="", encoding="utf-8") as f:
        return {row["id"]: row for row in csv.DictReader(f)}


def to_row(tweet, query: str) -> dict:
    return {
        "id": tweet.id_str,
        "url": tweet.url,
        "date": tweet.date.isoformat(),
        "username": tweet.user.username,
        "display_name": tweet.user.displayname,
        "followers": tweet.user.followersCount,
        "text": tweet.rawContent,
        "likes": tweet.likeCount,
        "retweets": tweet.retweetCount,
        "replies": tweet.replyCount,
        "quotes": tweet.quoteCount,
        "views": tweet.viewCount,
        "lang": tweet.lang,
        "query": query,
    }


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-q", "--query", action="append", help="search query (repeatable); replaces the defaults")
    parser.add_argument("--since", default="2026-10-08", help="YYYY-MM-DD, inclusive")
    parser.add_argument("--until", help="YYYY-MM-DD, exclusive")
    parser.add_argument("--limit", type=int, default=1000, help="max posts per query")
    parser.add_argument("--include-retweets", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    api = API()  # stores account sessions in accounts.db
    await ensure_account(api)

    rows = load_existing()
    before = len(rows)

    for query in args.query or DEFAULT_QUERIES:
        q = f"{query} since:{args.since}"
        if args.until:
            q += f" until:{args.until}"
        if not args.include_retweets:
            q += " -filter:retweets"

        found = 0
        async for tweet in api.search(q, limit=args.limit, kv={"product": "Latest"}):
            rows.setdefault(tweet.id_str, to_row(tweet, query))
            found += 1
        print(f"{found:5d} posts  {q}")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(sorted(rows.values(), key=lambda r: r["date"]))

    print(f"\n{len(rows)} unique posts in {OUT} ({len(rows) - before} new)")


if __name__ == "__main__":
    asyncio.run(main())
