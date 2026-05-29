"""
The real thing: hunt Bitcoin private keys by solving the elliptic-curve
discrete log (ECDLP) on secp256k1 with Baby-Step Giant-Step (BSGS).

This is the *actual* technique used to solve the lower "Bitcoin Puzzle"
transactions. Given a PUBLIC KEY whose private key lies in a known range
[lo, hi), BSGS finds it in about sqrt(hi - lo) group operations.

We demonstrate it finding keys for real (round-trip verified), then show the
wall: BSGS costs ~2^(k/2) ops and memory for a k-bit range, and -- crucially --
the UNSOLVED puzzles (#71+) don't even expose the public key, only the address
hash. With no public key you can't run ECDLP at all; you must brute-force
key -> address over the full 2^k space. That is the honest reason the big
prizes stay locked, and why no laptop (or warehouse of them) will find them.

Run:  python btc_key_hunt.py
"""
import time
import math
import os

# --- secp256k1 ---------------------------------------------------------------
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
G = (GX, GY)


def inv(x):
    return pow(x, P - 2, P)


def add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        s = (3 * x1 * x1) * inv(2 * y1) % P
    else:
        s = (y2 - y1) * inv((x2 - x1) % P) % P
    x3 = (s * s - x1 - x2) % P
    y3 = (s * (x1 - x3) - y1) % P
    return (x3, y3)


def mul(k, point=G):
    r = None
    addend = point
    while k:
        if k & 1:
            r = add(r, addend)
        addend = add(addend, addend)
        k >>= 1
    return r


def neg(point):
    if point is None:
        return None
    x, y = point
    return (x, (-y) % P)


# --- Baby-Step Giant-Step ----------------------------------------------------
def bsgs(target, lo, hi):
    """Find d in [lo, hi) with mul(d) == target, via BSGS. Returns (d, hops)."""
    w = hi - lo
    m = int(math.isqrt(w)) + 1
    # Search d' in [0, w) where d = lo + d';  target' = target - lo*G
    target_shift = add(target, neg(mul(lo)))

    # Baby steps: table[ j*G ] = j  for j in [0, m)
    table = {}
    cur = None  # 0*G
    for j in range(m):
        table[cur] = j
        cur = add(cur, G)

    # Giant steps: gamma = target' - i*(m*G); look for a baby match
    factor = neg(mul(m))           # -m*G
    gamma = target_shift
    for i in range(m + 1):
        if gamma in table:
            return lo + i * m + table[gamma], (m + i)
        gamma = add(gamma, factor)
    return None, (m + m)


# --- Demo: find keys for real, then show the wall ----------------------------
def hunt(bits):
    lo, hi = (1 << (bits - 1)), (1 << bits)        # puzzle-#bits style range
    secret = lo + int.from_bytes(os.urandom(32), "big") % (hi - lo)
    pub = mul(secret)                              # the only thing a hunter sees
    t0 = time.perf_counter()
    found, hops = bsgs(pub, lo, hi)
    dt = time.perf_counter() - t0
    ok = found == secret
    print(f"  {bits:>2}-bit range  secret=0x{secret:013x}  "
          f"FOUND=0x{found:013x}  {'OK' if ok else 'FAIL'}  "
          f"({hops:,} hops, {dt:.2f}s)")
    return dt


print("HUNTING BITCOIN KEYS (BSGS over secp256k1)\n")
print("Each line: we generate a secret in puzzle-#k's range, publish ONLY its")
print("public key, then recover the secret from the public key alone.\n")
for bits in (20, 28, 36, 40):
    hunt(bits)

print("""
THE WALL
--------
BSGS needs ~2^(k/2) operations AND ~2^(k/2) memory for a k-bit range:
   k=40  -> 2^20 ~ 1e6      (seconds on a laptop, as above)
   k=50  -> 2^25 ~ 3e7      (minutes; memory getting heavy)
   k=66  -> 2^33 ~ 9e9      (GPU cluster territory; this one WAS solved)
   k=71  -> 2^35 ~ 3e10     (feasible compute, but...)
   k=135 -> 2^67 ~ 1e20     (infeasible, full stop)

...and the decisive catch: the UNSOLVED puzzles publish only the ADDRESS
(a hash160), NOT the public key. Without the public key you cannot run BSGS or
kangaroo at all -- you must brute force key -> pubkey -> hash160 -> compare over
the ENTIRE 2^k space (no square-root shortcut). For k=71 that is 2^71 ~ 2e21
hashes. That is the honest, unbreakable wall.

So: this tool really does find keys -- but only ones small enough that there
was never any money behind them. The keys with coins behind them are exactly
the ones it cannot reach. That is not a limitation of the code; it is the
reason Bitcoin works.
""")
