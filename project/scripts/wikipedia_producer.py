"""Forward Wikipedia edit events to Kafka.

Reads the public Wikimedia "recentchange" Server-Sent Events stream, keeps
the edits of English Wikipedia articles and publishes them as JSON to the
Kafka topic ``wikipedia-edits``. The Spark job ``40_streaming.py`` consumes
this topic.

Usage (from the project directory, with the containers running)::

    python scripts/wikipedia_producer.py                 # until Ctrl+C
    python scripts/wikipedia_producer.py --minutes 25    # stop after 25 min

Kafka is reachable from the host on localhost:29092 (see compose.yaml).
"""
import argparse
import json
import time

from confluent_kafka import Producer
from requests_sse import EventSource

STREAM_URL = "https://stream.wikimedia.org/v2/stream/recentchange"
TOPIC = "wikipedia-edits"
# Wikimedia asks automated clients to identify themselves.
HEADERS = {"User-Agent": "ece-bigdata-lab-student-project/1.0 (Kafka demo)"}


def keep(change):
    """Keep edits and page creations of English Wikipedia articles."""
    return (
        change.get("wiki") == "enwiki"
        and change.get("type") in ("edit", "new")
        and change.get("namespace") == 0  # articles only, no talk pages
    )


def slim(change):
    """Keep only the fields used downstream."""
    length = change.get("length") or {}
    return {
        "id": change.get("id"),
        "type": change.get("type"),
        "title": change.get("title"),
        "user": change.get("user"),
        "bot": change.get("bot"),
        "minor": change.get("minor"),
        "comment": change.get("comment"),
        "timestamp": change.get("timestamp"),  # epoch seconds, event time
        "length_old": length.get("old"),
        "length_new": length.get("new"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bootstrap", default="localhost:29092")
    parser.add_argument("--topic", default=TOPIC)
    parser.add_argument("--minutes", type=float, default=None,
                        help="stop after this many minutes (default: never)")
    args = parser.parse_args()

    producer = Producer({"bootstrap.servers": args.bootstrap})
    deadline = time.time() + args.minutes * 60 if args.minutes else None
    seen = sent = 0

    with EventSource(STREAM_URL, headers=HEADERS) as stream:
        for event in stream:
            if event.type != "message" or not event.data:
                continue
            try:
                change = json.loads(event.data)
            except json.JSONDecodeError:
                continue  # keep-alive or truncated message
            seen += 1
            if keep(change):
                producer.produce(
                    args.topic,
                    key=(change.get("title") or "").encode("utf-8"),
                    value=json.dumps(slim(change)).encode("utf-8"),
                )
                producer.poll(0)
                sent += 1
            if seen % 1000 == 0:
                print(f"read {seen} events, sent {sent} to {args.topic}",
                      flush=True)
            if deadline and time.time() > deadline:
                break

    producer.flush()
    print(f"done: read {seen} events, sent {sent} to {args.topic}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("stopped")
