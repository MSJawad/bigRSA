"""Prime generation: small-prime trial division followed by Miller-Rabin."""

import secrets


def _sieve(limit: int) -> tuple[int, ...]:
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i * i :: i] = [False] * len(range(i * i, limit + 1, i))
    return tuple(i for i, prime in enumerate(is_prime) if prime)


SMALL_PRIMES = _sieve(1000)

# Miller-Rabin with the first 13 primes as bases is deterministic (never
# wrong) for every n below this bound (Sorenson and Webster, 2015).
_DETERMINISTIC_BASES = SMALL_PRIMES[:13]
_DETERMINISTIC_LIMIT = 3_317_044_064_679_887_385_961_981

# Rounds used above that bound. Each round with a random base lets a composite
# through with probability at most 1/4, so 40 rounds bound the error by 2**-80.
DEFAULT_ROUNDS = 40


def is_strong_probable_prime(n: int, base: int) -> bool:
    """Run one Miller-Rabin round: is odd n > 3 a strong probable prime to base?"""
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    x = pow(base, d, n)
    if x == 1 or x == n - 1:
        return True
    for _ in range(s - 1):
        x = pow(x, 2, n)
        if x == n - 1:
            return True
    return False


def is_probable_prime(n: int, rounds: int = DEFAULT_ROUNDS) -> bool:
    """Return True if n is prime, with error probability at most 4**-rounds.

    The answer is exact for n below about 3.3 * 10**24.
    """
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    if n < SMALL_PRIMES[-1] ** 2:
        return True
    if n < _DETERMINISTIC_LIMIT:
        bases = _DETERMINISTIC_BASES
    else:
        bases = (2 + secrets.randbelow(n - 3) for _ in range(rounds))
    return all(is_strong_probable_prime(n, a) for a in bases)


def generate_prime(bits: int) -> int:
    """Return a random prime of exactly `bits` bits whose top two bits are set.

    Setting the top two bits guarantees that the product of two such primes
    has exactly the sum of their bit lengths.
    """
    if bits < 3:
        raise ValueError("a prime needs at least 3 bits here")
    top_bits = (1 << (bits - 1)) | (1 << (bits - 2))
    while True:
        candidate = secrets.randbits(bits) | top_bits | 1
        if is_probable_prime(candidate):
            return candidate
