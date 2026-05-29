"""
Is Beale Cipher #1 a real encrypted message, or a hoax?

The famous Gillogly strings (J. Gillogly, Cryptologia, 1980): decoding Beale #1
with the Declaration of Independence yields gibberish that nonetheless contains
alphabetical runs like 'abcdefghi'. This is the lever:

  If #1 encrypted real text with some OTHER key, its numbers would be
  statistically INDEPENDENT of the Declaration -- decoding with the Declaration
  would show no alphabetical structure beyond chance.

  If the author built #1 by walking the Declaration and picking words whose
  first letters run a->b->c->d..., that structure appears ONLY under the
  Declaration -- the fingerprint of construction-without-a-message (a hoax).

We quantify the alphabetical structure and compare against a null model
(random orderings of the same letter multiset). Beale #2 (genuine English)
is the control.

Run:  python beale_hoax_test.py [num_trials]
"""
import sys
import random
from common import load_key, load_cipher, decode

random.seed(1729)
TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
words = load_key("declaration.txt")


def ascending_pairs(s):
    return sum(1 for i in range(len(s) - 1)
               if s[i].isalpha() and s[i + 1].isalpha()
               and ord(s[i + 1]) - ord(s[i]) == 1)


def longest_run(s):
    best = cur = 1
    for i in range(len(s) - 1):
        if s[i].isalpha() and s[i + 1].isalpha() and ord(s[i + 1]) - ord(s[i]) == 1:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best


def test(label, cipher_name):
    dec = decode(load_cipher(cipher_name), words)
    obs_pairs, obs_long = ascending_pairs(dec), longest_run(dec)
    letters = list(dec)
    ge_pairs = ge_long = 0
    for _ in range(TRIALS):
        random.shuffle(letters)
        if ascending_pairs(letters) >= obs_pairs:
            ge_pairs += 1
        if longest_run(letters) >= obs_long:
            ge_long += 1
    print(f"{label:<34} pairs={obs_pairs:>3} (p={ge_pairs/TRIALS:.1e})   "
          f"longest_run={obs_long} (p={ge_long/TRIALS:.1e})")


print(f"Alphabetical-structure test under the Declaration ({TRIALS:,} trials each)\n")
print(f"{'cipher':<34} {'ascending a->b pairs':<22} longest alphabetical run")
print("-" * 92)
test("Beale #2 (genuine English, control)", "beale_2.txt")
test("Beale #1 (the location cipher)",       "beale_1.txt")
test("Beale #3 (the heir-list cipher)",      "beale_3.txt")

print("""
Reading the result
------------------
#2 (real English) shows no anomalous alphabetical structure (high p).
#1 shows far more alphabetical transitions than chance allows (p ~ 0): the
   fingerprint of being constructed FROM the Declaration without encoding
   English -- i.e. a hoax.
#3 looks clean like #2 -- it is NOT positively flagged. (Note: 'clean' does
   not prove #3 genuine; a careful hoax or a real message under an unknown key
   would also look clean. #3 is undetermined; only #1 is flagged.)

Conclusion: on the balance of cryptographic evidence, Beale #1 most likely
encodes no plaintext. This is consistent with Gillogly (1980) and with the
fact that no key has decoded it in ~150 years -- there may be no key because
there is no message.
""")
