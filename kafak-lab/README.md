# Kafka lab setup

Install Python 3, then open a terminal in the `kafak-lab` folder. Create a virtual environment to keep the lab's packages separate from your system packages.

## Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install confluent-kafka
```

If `py` is unavailable but `python` works, use `python -m venv .venv` for the first command. These commands use the environment directly, so activation and PowerShell execution policy changes are unnecessary.

## macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install confluent-kafka
```

On Ubuntu/Debian, if creating the environment reports that `venv` is missing, run `sudo apt install python3-venv`, then retry.

`confluent-kafka` is the only dependency, so `python -m pip install -r requirements.txt` works too. On Windows, use `.\.venv\Scripts\python.exe` instead of `python`.

## Start Kafka

A Kafka broker must be running and reachable at `localhost:9092`. Installing `confluent-kafka` installs the Python client only.

```bash
docker pull apache/kafka-native:4.1.1
docker run -p 9092:9092 apache/kafka-native:4.1.1
```

Leave this terminal open while running the scripts.

## Run the scripts

Create the `BookLecture` topic:

```bash
python admin.py
```

Then run the producer and consumer in separate terminals:

```bash
python producer.py
```

```bash
python consumer.py
```

On macOS/Linux, activate the environment with `source .venv/bin/activate` in each terminal. On Windows, replace `python` with `.\.venv\Scripts\python.exe` in each command.

If using WSL on Windows, follow the Linux instructions and create the virtual environment inside WSL.

The producer waits one second between two lines, so sending the whole book takes about an hour. To send it all at once, set `PRODUCER_DELAY` to `0`:

```bash
PRODUCER_DELAY=0 python producer.py          # macOS / Linux
$env:PRODUCER_DELAY=0; python producer.py    # Windows PowerShell
```

## What each script does

| Script | Lab step | Role |
|---|---|---|
| `admin.py` | 2 | Creates the `BookLecture` topic (1 partition) and lists the existing topics. |
| `book.txt` | 3 | *The King's Friend* by Robert Sulivan, downloaded from [Project Gutenberg](https://www.gutenberg.org/ebooks/79740). |
| `producer.py` | 4 | Reads `book.txt` line by line and sends each line as one message to `BookLecture`. |
| `consumer.py` | 5 and 6 | Reads `BookLecture`, cleans every message and writes the result to `output/`. |
| `text_cleaning.py` | 6 | Cleaning and parsing functions used by the consumer. |

## Text cleaning (step 6)

Inspired by the word count lab, each incoming message goes through these steps:

1. Skip the Project Gutenberg header and license: only the lines between `*** START OF THE PROJECT GUTENBERG EBOOK` and `*** END OF THE PROJECT GUTENBERG EBOOK` are kept. The consumer stops as soon as it receives the END marker.
2. Convert the text to lower case.
3. Remove punctuation, including the typographic quotes and dashes used by Gutenberg (`’ “ ” —`), and digits.
4. Split the line into words, dropping blank spaces, single letters and common English stop words.
5. Skip lines that end up empty.

The consumer produces two files in `output/`:

- `cleaned_book.txt`: one cleaned line per incoming message that still contains words.
- `word_counts.txt`: every word with its number of occurrences (tab-separated), sorted by descending frequency, then alphabetically.

It also prints the 10 most frequent words. Because the book is a play, character names come out on top (`marq` for the Marquis de Rosny, `hen` for Henry IV, `kath` for Katherine de Villequier).

The consumer does not commit its offsets, so every run re-reads the topic from the beginning and rebuilds the output files. You can try `python text_cleaning.py` to see the cleaning applied to a sample sentence without Kafka.
