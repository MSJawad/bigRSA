import math

import pytest

from bigrsa.primes import SMALL_PRIMES, generate_prime, is_probable_prime, is_strong_probable_prime


def is_prime_naive(n):
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


def test_small_primes_table():
    assert SMALL_PRIMES == tuple(n for n in range(1000) if is_prime_naive(n))


def test_matches_trial_division_below_20000():
    for n in range(-5, 20000):
        assert is_probable_prime(n) == is_prime_naive(n), n


@pytest.mark.parametrize(
    "exponent",
    [61, 89, 107, 127, 521, 607, 1279],
)
def test_mersenne_primes(exponent):
    assert is_probable_prime(2**exponent - 1)


@pytest.mark.parametrize(
    "n",
    [
        2**67 - 1,  # 193707721 * 761838257287
        2**32 + 1,  # 641 * 6700417
        (2**127 - 1) * (2**89 - 1),
        (2**521 - 1) * (2**607 - 1),
        (2**521 - 1) ** 2,
    ],
)
def test_large_composites(n):
    assert not is_probable_prime(n)


CARMICHAEL_NUMBERS = [561, 1105, 1729, 2465, 2821, 6601, 8911, 41041, 825265, 321197185]


@pytest.mark.parametrize("n", CARMICHAEL_NUMBERS)
def test_carmichael_numbers_fool_fermat_but_not_miller_rabin(n):
    # A Carmichael number passes the Fermat test a**(n-1) = 1 (mod n) for
    # every base coprime to it, which is why the Fermat test alone is not enough.
    assert all(pow(a, n - 1, n) == 1 for a in range(2, 100) if math.gcd(a, n) == 1)
    assert not is_probable_prime(n)


# Each n is the smallest strong pseudoprime to all of the first k prime bases:
# that many Miller-Rabin rounds with fixed bases call it prime, wrongly.
STRONG_PSEUDOPRIMES = [
    (2047, 1),  # 23 * 89
    (1373653, 2),  # 829 * 1657
    (25326001, 3),  # 2251 * 11251
    (3215031751, 4),  # 151 * 751 * 28351
    (2152302898747, 5),  # 6763 * 10627 * 29947
    (3474749660383, 6),  # 1303 * 16927 * 157543
    (341550071728321, 8),  # 10670053 * 32010157
    (3825123056546413051, 11),  # 149491 * 747451 * 34233211
    (318665857834031151167461, 12),  # 399165290221 * 798330580441
    (3317044064679887385961981, 13),  # 1287836182261 * 2575672364521
]


@pytest.mark.parametrize(("n", "k"), STRONG_PSEUDOPRIMES)
def test_strong_pseudoprimes(n, k):
    assert all(is_strong_probable_prime(n, a) for a in SMALL_PRIMES[:k])
    assert not is_probable_prime(n)


def test_single_round_rejects_composite_with_witness():
    assert is_strong_probable_prime(2047, 2)
    assert not is_strong_probable_prime(2047, 3)


@pytest.mark.parametrize("bits", [3, 4, 8, 16, 64, 600])
def test_generate_prime_size(bits):
    for _ in range(5):
        p = generate_prime(bits)
        assert p.bit_length() == bits
        assert p >> (bits - 2) == 0b11
        assert is_probable_prime(p)


def test_generate_prime_product_has_exact_size():
    for _ in range(20):
        assert (generate_prime(32) * generate_prime(32)).bit_length() == 64


def test_generate_prime_rejects_tiny_sizes():
    with pytest.raises(ValueError):
        generate_prime(2)
