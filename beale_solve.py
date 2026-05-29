"""
Reproduce the one Beale cipher that IS solved: Paper #2.

Beale #2 was cracked in 1885 using the U.S. Declaration of Independence as the
key text. The catch that trips up most first attempts: you must split hyphenated
words ('self-evident' -> 'self', 'evident') before numbering, or word #115 is
'among' instead of the required 'instituted'.

Run:  python beale_solve.py
"""
import textwrap
from common import load_key, load_cipher, decode, chi_squared_english

words = load_key("declaration.txt")
print(f"Declaration of Independence: {len(words)} words after hyphen-split tokenization")
print(f"  word #115 = {words[114]!r}  (must be 'instituted' for the solve to work)\n")

cipher = load_cipher("beale_2.txt")
plain = decode(cipher, words)

print("Beale #2, decoded with the Declaration:")
print(textwrap.fill(plain, width=70))
print(f"\nchi-squared vs English: {chi_squared_english(plain):.1f}  "
      f"(real English ~50-100; gibberish ~600+)\n")

print("Historical plaintext (Beale's own errata corrected):")
print(textwrap.fill(
    "I have deposited in the county of Bedford about four miles from Bufords "
    "in an excavation or vault six feet below the surface of the ground the "
    "following articles belonging jointly to the parties whose names are given "
    "in number three herewith ...", width=70))
