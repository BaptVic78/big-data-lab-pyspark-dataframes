# %%
import re
import string
from collections import Counter

# %%
# Common English stop words (word count lab, step c)
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "can", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers",
    "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no",
    "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "we",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why",
    "will", "with", "would", "you", "your", "yours", "yourself",
    "yourselves", "thee", "thou", "thy", "thine", "ye", "o", "s", "t", "ll",
    "d", "re", "ve", "m", "shall", "may", "must", "let", "upon", "yet",
}

# Gutenberg books use typographic quotes and dashes on top of ASCII
# punctuation (word count lab, step f)
PUNCTUATION = string.punctuation + "‘’“”—–…«»"
_PUNCT_RE = re.compile(f"[{re.escape(PUNCTUATION)}]")
_DIGITS_RE = re.compile(r"\d+")

GUTENBERG_START = "*** START OF THE PROJECT GUTENBERG EBOOK"
GUTENBERG_END = "*** END OF THE PROJECT GUTENBERG EBOOK"


# %%
def clean_line(line):
    """Return the list of meaningful words contained in a line of text."""
    line = line.lower()
    line = _PUNCT_RE.sub(" ", line)
    line = _DIGITS_RE.sub(" ", line)
    return [w for w in line.split() if len(w) > 1 and w not in STOP_WORDS]


class GutenbergFilter:
    """Keep only the lines between the Gutenberg START and END markers.

    Messages arrive one at a time from Kafka, so the filter keeps track of
    where we are in the book between calls.
    """

    def __init__(self):
        self.in_body = False
        self.finished = False

    def accept(self, line):
        if line.startswith(GUTENBERG_START):
            self.in_body = True
            return False
        if line.startswith(GUTENBERG_END):
            self.in_body = False
            self.finished = True
            return False
        return self.in_body


def top_words(counter, n=None):
    """Sort by descending frequency, then alphabetically (steps d and e)."""
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return items[:n] if n else items


# %%
if __name__ == "__main__":
    sample = "“Sire, I am your FRIEND—the King’s friend!” cried he, in 1845."
    print(clean_line(sample))
    print(top_words(Counter(clean_line(sample))))
