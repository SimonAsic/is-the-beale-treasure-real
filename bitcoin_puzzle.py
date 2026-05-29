"""
Sanity-check the cryptographic pipeline against known answers.

The "Bitcoin Puzzle" transactions (created Jan 2015) placed coins at addresses
whose private keys are 1, 2..3, 4..7, 8..15, ... The first five keys are public
knowledge (1, 3, 7, 8, 21). We derive their addresses from scratch and confirm
they match the canonical puzzle addresses -- proving our secp256k1 -> SHA256 ->
RIPEMD160 -> Base58Check pipeline is correct.

This is the honest counterweight to the romance: the UNSOLVED puzzles (#71+)
require searching a >= 2^70 keyspace. That is infeasible on any classical or
near-term hardware. There is no shortcut; this file just shows the pipeline is
real by reproducing answers that are already public.

Requires: pip install ecdsa base58
Run:      python bitcoin_puzzle.py
"""
import hashlib
import base58
import ecdsa

PUZZLES = [
    (1, 1,  "1BgGZ9tcN4rm9KBzDn7KprQz87SZ26SAMH"),
    (2, 3,  "1CUNEBjYrCn2y1SdiUMohaKUi4wpP326Lb"),
    (3, 7,  "19ZewH8Kk1PDbSNdJ97FP4EiCjTRaZMZQA"),
    (4, 8,  "1EhqbyUMvvs7BfL8goY6qcPbD6YKfPqb7e"),
    (5, 21, "1E6NuFjCi27W5zoXg8TRdcSRq84zJeBW3k"),
]


def privkey_to_address(k: int) -> str:
    sk = ecdsa.SigningKey.from_secret_exponent(k, curve=ecdsa.SECP256k1)
    p = sk.get_verifying_key().pubkey.point
    x = p.x().to_bytes(32, "big")
    pub = (b"\x02" if p.y() % 2 == 0 else b"\x03") + x  # compressed SEC
    h160 = hashlib.new("ripemd160", hashlib.sha256(pub).digest()).digest()
    payload = b"\x00" + h160
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return base58.b58encode(payload + checksum).decode()


print(f"{'#':>2} {'privkey':>7}  {'derived address':<36} match")
print("-" * 56)
ok = True
for n, k, expected in PUZZLES:
    got = privkey_to_address(k)
    match = got == expected
    ok &= match
    print(f"{n:>2} {k:>7}  {got:<36} {'OK' if match else 'MISMATCH'}")
print("\nPipeline verified." if ok else "\nPipeline FAULT.")
