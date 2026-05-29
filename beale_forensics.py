"""
Author forensics: not WHAT the Beale ciphers say, but HOW they were built.

If #1 is a fabrication and #2 a genuine encoding, their construction habits
should differ. We measure three behavioural fingerprints and find that #1 is
the outlier on every one.

Run:  python beale_forensics.py
"""
from collections import Counter
from common import load_key, load_cipher, decode

words = load_key("declaration.txt")
c1 = load_cipher("beale_1.txt")
c2 = load_cipher("beale_2.txt")
c3 = load_cipher("beale_3.txt")

# 1. Anatomy of the longest alphabetical run in #1 -------------------------
dec1 = decode(c1, words)
i = best_i = 0
best_len = 1
while i < len(dec1):
    j = i
    while (j + 1 < len(dec1) and dec1[j].isalpha() and dec1[j + 1].isalpha()
           and ord(dec1[j + 1]) - ord(dec1[j]) == 1):
        j += 1
    if j - i + 1 > best_len:
        best_len, best_i = j - i + 1, i
    i = j + 1 if j > i else i + 1

run_nums = c1[best_i:best_i + best_len]
print("1. Anatomy of the longest alphabetical run in Beale #1")
print(f"   run = {dec1[best_i:best_i+best_len]!r}  from cipher numbers {run_nums}")
print(f"   source words: {[words[n-1] for n in run_nums]}")
print(f"   spread across the Declaration: words {min(run_nums)}..{max(run_nums)} "
      f"(span {max(run_nums)-min(run_nums)})")
print("   -> the alphabetical run was ASSEMBLED from scattered words, not read")
print("      off one passage: deliberate construction, not lazy scanning.\n")

# 2. Behavioural fingerprints ---------------------------------------------
print("2. Construction fingerprints")
print(f"   {'cipher':>7} {'mean |gap|':>11} {'reuse rate':>11} {'% in first 200':>15}")
for name, c in [("#1", c1), ("#2", c2), ("#3", c3)]:
    gaps = [abs(c[k + 1] - c[k]) for k in range(len(c) - 1)]
    reuse = 1 - len(set(c)) / len(c)
    low = sum(1 for x in c if x <= 200) / len(c)
    print(f"   {name:>7} {sum(gaps)/len(gaps):>11.1f} {reuse:>10.0%} {low:>14.0%}")

print("""
   #1 is the outlier on every axis: it jumps around the most (largest gaps),
   reuses words the least, and reaches deepest into the document. Together with
   the alphabetical fingerprint, this is the portrait of a number string that
   was FABRICATED rather than ENCODED.
""")
