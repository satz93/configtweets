"""Print a Markdown summary of the latest results (used for the GitHub Actions run page).

    python summarize.py >> "$GITHUB_STEP_SUMMARY"
"""

import csv
from collections import Counter
from pathlib import Path

TWEETS = Path("data/tweets.csv")
CLASSIFIED = Path("data/classified.csv")
CRITICAL = Path("data/critical.csv")

TOP = 30


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cell(text: str, limit: int = 220) -> str:
    text = " ".join(text.split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def table(rows: list[dict], with_complaint: bool) -> list[str]:
    head = "| Author | Likes | " + ("Complaint | " if with_complaint else "") + "Post |"
    lines = [head, "|---|---:|" + ("---|" if with_complaint else "") + "---|"]
    for r in rows:
        complaint = f"{cell(r['complaint'], 40)} | " if with_complaint else ""
        lines.append(f"| @{r['username']} | {r['likes']} | {complaint}[{cell(r['text'])}]({r['url']}) |")
    return lines


def main() -> None:
    tweets = read_csv(TWEETS)
    classified = read_csv(CLASSIFIED)
    critical = read_csv(CRITICAL)

    out = ["# Config India on X", ""]
    if not tweets:
        out.append("No posts were collected. Check the collect step's log.")
        print("\n".join(out))
        return

    if not classified:
        out += [
            f"Collected **{len(tweets)}** posts. They weren't labelled because the `ANTHROPIC_API_KEY` "
            "secret isn't set. Download `config-india-results` below for the CSV.",
            "",
            "## Most-liked posts",
            "",
        ]
        top = sorted(tweets, key=lambda r: int(r["likes"] or 0), reverse=True)[:TOP]
        out += table(top, with_complaint=False)
        print("\n".join(out))
        return

    relevant = [r for r in classified if r["about_config_india"] == "True"]
    out += [
        f"**{len(tweets)}** posts collected · **{len(relevant)}** about Config India · "
        f"**{len(critical)}** critical of the event",
        "",
        "Download `config-india-results` at the bottom of this page for the full CSVs.",
        "",
    ]

    themes = Counter(r["complaint"].strip().lower() for r in critical if r["complaint"].strip())
    if themes:
        out += ["## Complaints", "", "| Complaint | Posts |", "|---|---:|"]
        out += [f"| {cell(name, 60)} | {count} |" for name, count in themes.most_common(15)]
        out.append("")

    if critical:
        out += [f"## Critical posts (top {min(TOP, len(critical))} by engagement)", ""]
        out += table(critical[:TOP], with_complaint=True)

    print("\n".join(out))


if __name__ == "__main__":
    main()
