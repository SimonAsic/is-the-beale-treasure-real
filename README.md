# Classic Cipher Cryptanalysis: Beale & Zodiac

Reproducible, from-scratch Python for three famous ciphers:

1. **Beale Cipher #2** — reproduce the one Beale cipher that *is* solved (1885, keyed on the Declaration of Independence).
2. **Beale Cipher #1** — a statistical test arguing it's a **hoax**, not a treasure map. (p < 5×10⁻⁶)
3. **Zodiac Z340** — reproduce the famous 2020 solution end-to-end, transposition and all.

No dependencies beyond the standard library for the Beale work (`ecdsa`/`base58` only for the optional Bitcoin sanity-check). Every claim below is something you can run and verify in seconds.

```bash
git clone <this-repo> && cd classic-cipher-cryptanalysis
python beale_solve.py        # reproduce the 1885 Beale #2 solve
python beale_hoax_test.py    # is Beale #1 real? (Monte Carlo)
python beale_forensics.py    # how was Beale #1 built?
python zodiac_z340.py        # reproduce the Zodiac Z340 decode
pip install ecdsa base58 && python bitcoin_puzzle.py   # optional pipeline check
```

---

## 1. Beale #2: reproducing the 1885 solve

The Beale Papers (1885) describe gold buried in Bedford County, Virginia, encrypted across three numeric ciphers. Only **#2** was ever solved — using the **U.S. Declaration of Independence** as the key: cipher number *N* → first letter of the *N*-th word.

The gotcha that defeats most first attempts: you must **split hyphenated words** (`self-evident` → `self`, `evident`) before numbering. Without it, word #115 is `among`; with it, word #115 is `instituted` — and the cipher falls open.

```
$ python beale_solve.py
chi-squared vs English: 81.9   (real English ~50-100; gibberish ~600+)
iharedeposctedinthecopntfolbedoort... = "I have deposited in the county of Bedford..."
```

## 2. Beale #1: real cipher, or hoax?

This is the interesting one. Beale #1 (the "location" cipher) has resisted every attacker for ~150 years. In 1980, James Gillogly (RAND) noticed something strange: decoding #1 with the Declaration produces gibberish that nonetheless contains **alphabetical runs** like `...defghi...`.

That observation is a lever. Consider two hypotheses:

- **Real:** #1 encrypts a genuine message with some *other* key book. Then its numbers are statistically **independent** of the Declaration, and decoding with the Declaration should show **no** alphabetical structure beyond chance.
- **Hoax:** the author built #1 by walking the Declaration and picking words whose first letters spell `a→b→c→d…`. That structure then appears **only** under the Declaration — and the result is gibberish, not English.

`beale_hoax_test.py` quantifies the alphabetical structure and compares it to a null model (100,000 random orderings of the same letters). **Beale #2 (genuine English) is the control.**

```
cipher                                ascending a->b pairs    longest alphabetical run
-------------------------------------------------------------------------------------
Beale #2 (genuine English, control)   pairs=40 (p=0.20)       run=3 (p=0.72)   ← clean
Beale #1 (the location cipher)        pairs=44 (p<1e-5)       run=6 (p~1e-5)   ← FLAGGED
Beale #3 (the heir-list cipher)       pairs=16 (p=0.94)       run=3 (p=0.56)   ← clean
```

Beale #1 has **44 alphabetical transitions** where chance allows ~15 — a value that never appeared once in 200,000 random orderings of its own letters. The only mechanism that imprints alphabetical order into the *Declaration decode specifically* is deliberate construction from the Declaration **without** encoding a real message.

**Verdict:** on the balance of cryptographic evidence, **Beale #1 most likely encodes no plaintext.** No key has decoded it in 150 years — plausibly because there is no message. (Consistent with Gillogly, 1980.)

> **Honest caveat:** This is a balance-of-evidence argument, not a proof of non-existence. And note **#3 is *not* flagged** — it looks statistically ordinary. "Clean" does not prove #3 is genuine (a careful hoax, or a real message under an unknown key, would also look clean). #3 is *undetermined*; only **#1** carries the positive hoax fingerprint.

## 3. Author forensics: how Beale #1 was built

`beale_forensics.py` asks *how* each cipher was constructed, not what it says. Beale #1 is the outlier on every behavioural axis:

| metric | #1 | #2 (genuine) | #3 |
|---|---|---|---|
| alphabetical fingerprint | **flagged** | no | no |
| mean gap between consecutive numbers | **273.8** | 172.6 | 89.9 |
| number-reuse rate | **43%** (lowest) | 76% | 57% |
| % of picks in first 200 words | **59%** (deepest) | 75% | 74% |

The famous `defghi` run is assembled from words at positions `[320, 37, 122, 113, 6, 140]` — scattered across the whole document, not read off one passage. The author *deliberately assembled* the alphabetical sequence; they didn't stumble into it.

## 4. Zodiac Z340: reproducing the 2020 solution

The Zodiac Killer's 340-character cipher went unbroken for **51 years** until David Oranchak, Sam Blake, and Jarl Van Eycke cracked it in December 2020 (FBI-confirmed). `zodiac_z340.py` reproduces the decode from scratch.

**Scheme:** homophonic substitution, then a transposition. The transposition is a **(1,2)-decimation**: from each grid cell, step *down 1 row, right 2 columns*, wrapping on a torus. On a 17-wide grid that advances the linear index by 17 + 2 = **19** every step — the legendary "period-19 knight's move."

What the script does and verifies:
1. Implements the (1,2)-decimation and proves it's a **valid full-cycle permutation** (all 153 cells visited exactly once) — the mathematical core of the break.
2. Untransposes the real ciphertext and recovers the homophonic key: **63 symbols → 21 letters** (no J/K/Q/X/Z — exactly the FBI-confirmed solution).
3. Decodes to the message: *"I HOPE YOU ARE HAVING LOTS OF FUN IN TRYING TO CATCH ME … I AM NOT AFRAID OF THE GAS CHAMBER BECAUSE IT WILL SEND ME TO PARADICE …"*
4. **Faithfulness check:** the decode reproduces Zodiac's *own* documented encipherment errors (`FAN`→fun, `WORV`→work, `VNOW`→know, `PARADLCE`, `SOOHER`) and block 3's word-reversal quirk. Reproducing his exact mistakes is strong evidence the pipeline is correct, not fudged.

> This reproduces a **known, published** solution. It is not a new break.

## 5. Bitcoin puzzle: a pipeline sanity-check (and a reality check)

`bitcoin_puzzle.py` derives the addresses of "Bitcoin Puzzle" transactions #1–#5 from their publicly-known private keys (1, 3, 7, 8, 21) and confirms they match the real addresses — proving the secp256k1 → SHA256 → RIPEMD160 → Base58Check pipeline is correct.

It's also the honest counterweight to cipher-treasure romance: the **unsolved** puzzles (#71+) require searching a ≥ 2⁷⁰ keyspace. There is no shortcut and no near-term hardware that makes it feasible. This file just shows the math is real by reproducing answers that are already public.

## 6. Hunting Bitcoin keys for real (and the wall that stops it)

`btc_key_hunt.py` implements **Baby-Step Giant-Step** discrete-log on secp256k1 — the actual technique used to solve the lower Bitcoin Puzzle transactions. Given a *public key* whose private key lies in a known k-bit range, it recovers the key in ~2^(k/2) operations. It really finds keys (round-trip verified):

```
20-bit range   FOUND  ✓   (850 hops, 0.08s)
28-bit range   FOUND  ✓   (19,538 hops, 1.66s)
36-bit range   FOUND  ✓   (269,446 hops, 23.2s)
40-bit range   FOUND  ✓   (1,245,271 hops, 108.7s)
```

Every +8 bits multiplies the time ~16× — the √(2^k) law made visible. Extrapolated: k=66 is GPU-cluster territory (that puzzle *was* solved), k=135 is ~2^67 ops (hopeless).

**And the decisive catch:** the *unsolved* puzzles (#71+) publish only the address (a hash160), **not** the public key. With no public key you can't run BSGS or kangaroo at all — you must brute-force `key → pubkey → hash160 → compare` over the entire 2^k space, with no square-root shortcut. That is the honest, unbreakable wall.

> The punchline: this tool genuinely finds keys — but only ones small enough that there was never any money behind them. The keys with coins behind them are exactly the ones it cannot reach. That's not a flaw in the code; it's the reason Bitcoin works.

---

## What this is, and isn't

- ✅ Reproducible reimplementations of published results, with verification you can run.
- ✅ An original (if modest) statistical framing of the Beale #1 hoax question, with the #3 control.
- ✅ A working ECDLP key-recovery tool that demonstrates exactly where (and why) Bitcoin key-hunting becomes infeasible.
- ❌ Not a new cipher break, not a treasure map, not a way to recover anyone's coins.

## Repository layout

```
.
├── common.py            # shared book-cipher helpers (load/decode/score)
├── beale_solve.py       # reproduce the 1885 Beale #2 solve
├── beale_hoax_test.py   # Monte Carlo hoax test on #1/#2/#3
├── beale_forensics.py   # construction fingerprints
├── zodiac_z340.py       # Zodiac Z340 reproduction
├── bitcoin_puzzle.py    # ECDSA pipeline sanity-check (needs ecdsa, base58)
├── btc_key_hunt.py      # BSGS elliptic-curve key recovery + the infeasibility wall
└── data/
    ├── beale_1.txt  beale_2.txt  beale_3.txt
    ├── declaration.txt  constitution.txt
    └── zodiac_z340.txt
```

## Credits & references

- **Beale Papers** transcription: [Wikisource](https://en.wikisource.org/wiki/The_Beale_Papers) · overview: [Wikipedia](https://en.wikipedia.org/wiki/Beale_ciphers)
- **Gillogly, J. J.** (1980), "The Beale Cypher: A Dissenting Opinion," *Cryptologia* 4(2). The original alphabetical-strings observation.
- **Zodiac Z340 solution**: Oranchak, Blake & Van Eycke (2020). Paper: [arXiv:2403.17350](https://arxiv.org/abs/2403.17350) · writeup: [Wolfram Blog](https://blog.wolfram.com/2021/03/24/the-solution-of-the-zodiac-killers-340-character-cipher/)
- **Z340 ciphertext transcription**: [zodiackillerciphers.com](https://zodiackillerciphers.com/) via the [n1k0m0 transposition-reverser](https://github.com/n1k0m0/Zodiac-340-Transposition-Reverser)
- **Founding documents**: U.S. National Archives ([Declaration](https://www.archives.gov/founding-docs/declaration-transcript), [Constitution](https://www.archives.gov/founding-docs/constitution-transcript))

## Support / tip jar

If this saved you a treasure hunt — or you just enjoyed the read — tips are welcome and keep the weekend cryptanalysis coming:

**BTC:** `3PuGDsdHaAoMNApqHP6oZa9RN1g6MEGEkS`

(A valid P2SH mainnet address — verify the checksum yourself with the pipeline in `bitcoin_puzzle.py` if you like. Every sat appreciated. 🏴‍☠️)

## License

MIT — see [LICENSE](LICENSE).

---

<sub>Built as a weekend cryptanalysis project. PRs welcome — especially anyone who wants to add Z408, run a larger key-text search against Beale #1, or formalize the hoax test as a proper hypothesis test.</sub>
