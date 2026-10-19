# xscrapper

Collect X (Twitter) posts about **Figma Config India** (Bengaluru, Oct 15 2026), then use Claude to find
the ones saying the event was underwhelming or not a hit.

> Why not snscrape? Its Twitter module has been broken since mid-2023, when X put search behind a login.
> This project uses [twscrape](https://github.com/vladkens/twscrape), which searches as your own logged-in
> account. Scraping is against X's terms. Keep volumes modest and consider a spare account, because X can
> rate-limit or lock accounts that scrape.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:

- `X_USERNAME`: your X handle, without the `@`.
- `X_COOKIES`: log in to x.com in your browser, open DevTools → Application → Cookies → `https://x.com`,
  and copy the `auth_token` and `ct0` values as `auth_token=...; ct0=...`. Cookies are more reliable than a
  password login, and twscrape never sees your password.
- `ANTHROPIC_API_KEY`: from <https://console.anthropic.com>.

`.env` and `accounts.db` (where twscrape keeps the session) are git-ignored. Don't commit them.

## 1. Collect posts

```bash
python collect.py
```

This searches a set of default queries (`"config india"`, `#ConfigIndia`, `figma config bengaluru`, …) for
posts since 2026-10-08, excluding retweets, and writes the de-duplicated results to `data/tweets.csv`.
Re-running adds new posts to the file.

```bash
python collect.py --since 2026-10-14 --until 2026-10-25 --limit 2000
python collect.py -q '"config india" underwhelming' -q '"config india" disappointing'
```

## 2. Find the critical ones

```bash
python classify.py
```

Claude reads the posts in batches of 25 and labels each one:

| column | meaning |
|---|---|
| `about_config_india` | actually about this event, not spam or a different "config" |
| `sentiment` | positive / neutral / negative / mixed |
| `critical_of_event` | says or implies the event was underwhelming, disappointing, overhyped, badly run… (sarcasm counts) |
| `complaint` | short tag for the main gripe, e.g. `nothing new announced`, `crowd management` |
| `reason` | one-line justification |

Outputs:

- `data/classified.csv`: every post with its labels. Re-runs only label new posts.
- `data/critical.csv`: posts critical of the event, sorted by engagement (likes + retweets).

Open `critical.csv` in Excel or Sheets, or with `pandas.read_csv`, to group by `complaint` and see the
recurring themes.
