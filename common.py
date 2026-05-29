"""
Shared helpers for the book-cipher analyses.

A Beale-style book cipher maps each plaintext letter to a NUMBER: the position
of a word in a key text whose FIRST LETTER is that plaintext letter. To decode,
you look up the Nth word of the key text and take its first letter.
"""
from pathlib import Path
import re

DATA = Path(__file__).parent / "data"


def load_key(name: str) -> list[str]:
    """Tokenize a key text the Beale way: split hyphenated words ('self-evident'
    -> 'self', 'evident'), strip surrounding punctuation, drop empties.

    The hyphen split is the historically correct rule: without it, word #115 of
    the Declaration of Independence is not 'instituted' and Beale Cipher #2 will
    not decode. See README.
    """
    text = (DATA / name).read_text()
    text = text.replace("-", " ").replace("—", " ").replace("–", " ").replace("&", " and ")
    words = []
    for tok in text.split():
        clean = tok.strip(",.;:!?\"'()[]{}")
        if clean:
            words.append(clean)
    return words


def load_cipher(name: str) -> list[int]:
    """Load a whitespace-separated list of cipher numbers."""
    return [int(x) for x in (DATA / name).read_text().split()]


def decode(numbers: list[int], words: list[str]) -> str:
    """Decode a book cipher: Nth word's first letter. Out-of-range -> '?'."""
    out = []
    for n in numbers:
        if 1 <= n <= len(words):
            ch = words[n - 1][0].lower()
            out.append(ch if ch.isalpha() else "?")
        else:
            out.append("?")
    return "".join(out)


# English unigram frequencies (Norvig), percentages.
ENGLISH_FREQ = {
    "e": 12.7, "t": 9.1, "a": 8.2, "o": 7.5, "i": 7.0, "n": 6.7, "s": 6.3,
    "h": 6.1, "r": 6.0, "d": 4.3, "l": 4.0, "c": 2.8, "u": 2.8, "m": 2.4,
    "w": 2.4, "f": 2.2, "g": 2.0, "y": 2.0, "p": 1.9, "b": 1.5, "v": 1.0,
    "k": 0.8, "j": 0.15, "x": 0.15, "q": 0.1, "z": 0.07,
}


def chi_squared_english(text: str) -> float:
    """Distance from English letter frequencies. Lower = more English-like.
    Real English ~ 50-100; random gibberish ~ 600+."""
    s = re.sub(r"[^a-z]", "", text.lower())
    if not s:
        return 999.0
    n = len(s)
    chi = 0.0
    for c, pct in ENGLISH_FREQ.items():
        expected = pct / 100.0 * n
        observed = s.count(c)
        if expected > 0:
            chi += (observed - expected) ** 2 / expected
    return chi
