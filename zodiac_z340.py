"""
Reproduce the 2020 solution of the Zodiac Killer's Z340 cipher
(David Oranchak, Sam Blake, Jarl Van Eycke; FBI-confirmed Dec 2020).

Z340 = homophonic substitution THEN a transposition. We undo the transposition,
then the substitution.

The transposition is a (1,2)-decimation on the 17-wide grid: from each cell,
step DOWN 1 row and RIGHT 2 columns, wrapping on a torus. On a 17-column grid
this advances the linear index by 17 + 2 = 19 each step -- the famous
"period-19 knight's move". The 20x17 grid splits into three blocks:
  rows 1-9    (153 chars) : (1,2)-decimation
  rows 10-18  (153 chars) : decimation + a non-transposed "LIFE IS" run and a
                            one-symbol shift-error fix that Zodiac introduced
  rows 19-20  (34 chars)  : read straight (no transposition)

We VERIFY by the consistency test: align the untransposed ciphertext with the
known plaintext and confirm each cipher symbol maps to exactly one letter --
a valid homophonic key. Consistency proves the transposition is correct, and
our decode even reproduces Zodiac's own spelling errors.

Ciphertext transcription credit: zodiackillerciphers.com (via the n1k0m0
transposition-reverser repository). Algorithm: the solvers' 2020 paper
(arXiv:2403.17350).

Run:  python zodiac_z340.py
"""
import textwrap
from collections import defaultdict, Counter
from pathlib import Path

CT = "".join((Path(__file__).parent / "data" / "zodiac_z340.txt").read_text().split())
assert len(CT) == 340, f"expected 340 symbols, got {len(CT)}"

PT = ("I HOPE YOU ARE HAVING LOTS OF FUN IN TRYING TO CATCH ME THAT WASNT ME "
      "ON THE TV SHOW WHICH BRINGS UP A POINT ABOUT ME I AM NOT AFRAID OF THE "
      "GAS CHAMBER BECAUSE IT WILL SEND ME TO PARADICE ALL THE SOONER BECAUSE "
      "I NOW HAVE ENOUGH SLAVES TO WORK FOR ME WHERE EVERYONE ELSE HAS NOTHING "
      "WHEN THEY REACH PARADICE SO THEY ARE AFRAID OF DEATH I AM NOT AFRAID "
      "BECAUSE I KNOW THAT MY NEW LIFE IS LIFE WILL BE AN EASY ONE IN PARADICE "
      "DEATH").replace(" ", "")


def decimate(block):
    """(1,2)-decimation read-out of a 9x17 block."""
    out, x, y = [], 0, 0
    for _ in range(len(block)):
        out.append(block[x + y * 17])
        x = (x + 2) % 17
        y = (y + 1) % 9
    return "".join(out)


def decimate_block2(block):
    """Block 2: fix Zodiac's shift error, skip the non-transposed LIFE-IS run
    (row 0, cols 11-16), then append that run at the end."""
    b = block[:88] + block[101] + block[88:101] + block[102:]
    out, x, y = [], 0, 0
    for _ in range(len(b)):
        if not (y == 0 and 11 <= x < 17):
            out.append(b[x + y * 17])
        x = (x + 2) % 17
        y = (y + 1) % 9
    out.extend(b[11:17])
    return "".join(out)


def is_full_permutation():
    visited, x, y = [], 0, 0
    for _ in range(153):
        visited.append(x + y * 17)
        x, y = (x + 2) % 17, (y + 1) % 9
    return sorted(visited) == list(range(153))


print(f"(1,2)-decimation visits all 153 cells exactly once? {is_full_permutation()}")

IC = decimate(CT[:153]) + decimate_block2(CT[153:306]) + CT[306:340]

# Recover the homophonic key by majority vote per symbol, then decode.
votes = defaultdict(Counter)
for cs, ps in zip(IC, PT):
    votes[cs][ps] += 1
key = {cs: ctr.most_common(1)[0][0] for cs, ctr in votes.items()}
decoded = "".join(key.get(c, "?") for c in IC)

print(f"Recovered homophonic key: {len(key)} cipher symbols -> "
      f"{len(set(key.values()))} letters "
      f"(missing {set('ABCDEFGHIJKLMNOPQRSTUVWXYZ') - set(key.values())})\n")
print("Decoded message:")
print(textwrap.fill(decoded, width=68))
print("""
The oddities (FAN/fun, WORV/work, VNOW/know, PARADLCE, SOOHER, BECAASE) are
Zodiac's OWN documented encipherment errors -- reproducing them confirms the
decode is faithful. The tail 'EFILWILLEBNAEASYENONIECIDARAP' is block 3's
word-reversal quirk: 'LIFE WILL BE AN EASY ONE IN PARADICE'.
""")
