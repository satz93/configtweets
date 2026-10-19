"""Label each collected post with Claude and pull out the ones critical of Config India.

Reads data/tweets.csv (from collect.py) and writes:
  data/classified.csv  every post with its labels (re-runs skip posts already labelled)
  data/critical.csv    only posts that say the event was underwhelming / not a hit

    python classify.py
    python classify.py --batch-size 20
"""

import argparse
import csv
import json
from pathlib import Path
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel

MODEL = "claude-opus-5-5"

IN = Path("data/tweets.csv")
CLASSIFIED = Path("data/classified.csv")
CRITICAL = Path("data/critical.csv")

LABEL_FIELDS = ["about_config_india", "sentiment", "critical_of_event", "complaint", "reason"]

SYSTEM = """You label X (Twitter) posts about Config India, Figma's design conference held in \
Bengaluru on October 15, 2026.

For each post decide:
- about_config_india: is it actually about this event (not another "config", not unrelated spam)?
- sentiment toward the event: positive, neutral, negative, or mixed.
- critical_of_event: does the author say or clearly imply the event was underwhelming, \
disappointing, not a hit, overhyped, badly organised, or not worth attending? Sarcasm and \
indirect jabs count. Criticism of Figma the product alone, unrelated to the event, does not.
- complaint: a short tag for the main complaint (e.g. "nothing new announced", "crowd management", \
"too salesy", "venue/logistics", "talks too basic"), or an empty string if none.
- reason: one sentence explaining the label.

Return one label per post, using the post's id."""


class Label(BaseModel):
    id: str
    about_config_india: bool
    sentiment: Literal["positive", "neutral", "negative", "mixed"]
    critical_of_event: bool
    complaint: str
    reason: str


class Labels(BaseModel):
    labels: list[Label]


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def classify_batch(client: anthropic.Anthropic, batch: list[dict]) -> dict[str, Label]:
    posts = [{"id": t["id"], "author": t["username"], "date": t["date"], "text": t["text"]} for t in batch]
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": json.dumps(posts, ensure_ascii=False)}],
        output_format=Labels,
        output_config={"effort": "low"},
        # If a post trips a safety classifier, let the API retry on a fallback model.
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    if response.stop_reason == "refusal":
        print(f"  refused batch starting at {batch[0]['id']}; skipping (will retry next run)")
        return {}
    return {label.id: label for label in response.parsed_output.labels}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch-size", type=int, default=25, help="posts per Claude request")
    args = parser.parse_args()

    load_dotenv()
    tweets = read_csv(IN)
    if not tweets:
        raise SystemExit(f"No posts in {IN}. Run collect.py first.")

    done = {row["id"]: row for row in read_csv(CLASSIFIED)}
    todo = [t for t in tweets if t["id"] not in done]
    print(f"{len(tweets)} posts, {len(done)} already labelled, {len(todo)} to go")

    client = anthropic.Anthropic()
    fields = list(tweets[0].keys()) + LABEL_FIELDS

    for start in range(0, len(todo), args.batch_size):
        batch = todo[start:start + args.batch_size]
        labels = classify_batch(client, batch)
        for tweet in batch:
            label = labels.get(tweet["id"])
            if label:
                done[tweet["id"]] = {**tweet, **label.model_dump(exclude={"id"})}
        # Save after every batch so an interrupted run can resume.
        write_csv(CLASSIFIED, list(done.values()), fields)
        print(f"  labelled {min(start + args.batch_size, len(todo))}/{len(todo)}")

    rows = list(done.values())
    critical = [
        r for r in rows
        if str(r["about_config_india"]) == "True" and str(r["critical_of_event"]) == "True"
    ]
    critical.sort(key=lambda r: int(r["likes"] or 0) + int(r["retweets"] or 0), reverse=True)
    write_csv(CRITICAL, critical, fields)

    relevant = [r for r in rows if str(r["about_config_india"]) == "True"]
    print(f"\n{len(relevant)} posts about Config India, {len(critical)} critical of the event -> {CRITICAL}")
    for r in critical[:10]:
        print(f"- @{r['username']} ({r['likes']} likes) [{r['complaint']}] {r['url']}")


if __name__ == "__main__":
    main()
