# %%
import os
from collections import Counter

from confluent_kafka import Consumer

from text_cleaning import GutenbergFilter, clean_line, top_words

# %%
# Offsets are not committed so every run re-reads the whole topic and
# rebuilds the output files from scratch.
conf = {'bootstrap.servers': 'localhost:9092',
        'group.id': 'book-cleaner',
        'auto.offset.reset': 'smallest',
        'enable.auto.commit': False}

consumer = Consumer(conf)

# %%
topic='BookLecture'
consumer.subscribe([topic])

# %%
OUTPUT_DIR = 'output'
CLEANED_FILE = os.path.join(OUTPUT_DIR, 'cleaned_book.txt')
WORD_COUNT_FILE = os.path.join(OUTPUT_DIR, 'word_counts.txt')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# %%
# Configuration
MAX_EMPTY_POLLS = 10  # Ends after ~10 seconds of silence
MAX_ERRORS = 5        # Ends after 5 consecutive errors
empty_polls = 0
error_count = 0

gutenberg = GutenbergFilter()
word_counts = Counter()
received = 0
written = 0

with open(CLEANED_FILE, 'w', encoding='utf-8') as out:
    while True:
        msg = consumer.poll(1.0)

        # 1. Handle "No Message" (Timeout)
        if msg is None:
            empty_polls += 1
            if empty_polls >= MAX_EMPTY_POLLS:
                print("Closing: No new messages received.")
                break
            continue

        # 2. Handle Errors
        if msg.error():
            error_count += 1
            print(f"Consumer error: {msg.error()}")
            if error_count >= MAX_ERRORS:
                print("Closing: Too many consecutive errors.")
                break
            continue

        # 3. Handle Success
        # Reset counters when we actually get data
        empty_polls = 0
        error_count = 0
        received += 1

        line = msg.value().decode('utf-8')
        print(f"Rcvd message: {line.rstrip()}")

        # 4. Clean and parse the message
        if not gutenberg.accept(line):
            if gutenberg.finished:
                print("Closing: reached the end of the book.")
                break
            continue
        words = clean_line(line)
        if not words:
            continue

        cleaned = ' '.join(words)
        out.write(cleaned + '\n')
        out.flush()
        word_counts.update(words)
        written += 1
        print(f"Cleaned     : {cleaned}")

# Clean up
consumer.close()

# %%
with open(WORD_COUNT_FILE, 'w', encoding='utf-8') as f:
    for word, count in top_words(word_counts):
        f.write(f"{word}\t{count}\n")

print(f"\n{received} messages received, {written} cleaned lines written "
      f"to {CLEANED_FILE}")
print(f"{len(word_counts)} distinct words written to {WORD_COUNT_FILE}")
print("Top 10 words:")
for word, count in top_words(word_counts, 10):
    print(f"  {word:<15} {count}")
