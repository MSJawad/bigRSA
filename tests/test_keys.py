import json
import math
import os

import pytest

from bigrsa.keys import (
    DEFAULT_EXPONENT,
    InvalidKeyError,
    PrivateKey,
    generate_key,
    load_private_key,
    load_public_key,
    private_key_from_primes,
    save_private_key,
    save_public_key,
)
from bigrsa.primes import is_probable_prime


def assert_valid_key(key: PrivateKey, bits: int, e: int):
    phi = (key.p - 1) * (key.q - 1)
    assert key.n == key.p * key.q
    assert key.n.bit_length() == bits
    assert key.p != key.q
    assert is_probable_prime(key.p) and is_probable_prime(key.q)
    assert key.e == e
    assert math.gcd(e, phi) == 1
    assert key.e * key.d % phi == 1
    assert 0 < key.d < phi


def test_textbook_example():
    # The worked example from the Wikipedia article on RSA.
    key = private_key_from_primes(61, 53, 17)
    assert (key.n, key.d) == (3233, 2753)
    assert pow(65, key.e, key.n) == 2790
    assert pow(2790, key.d, key.n) == 65


def test_default_key_is_1200_bits_from_two_600_bit_primes():
    key = generate_key()
    assert_valid_key(key, 1200, DEFAULT_EXPONENT)
    assert key.p.bit_length() == key.q.bit_length() == 600


@pytest.mark.parametrize(("bits", "e"), [(64, 65537), (65, 3), (256, 17), (513, 65537)])
def test_generated_key_invariants(bits, e):
    for _ in range(5):
        assert_valid_key(generate_key(bits, e), bits, e)


@pytest.mark.parametrize("bits", [0, 63, 8193])
def test_rejects_key_size_out_of_range(bits):
    with pytest.raises(InvalidKeyError, match="key size"):
        generate_key(bits)


@pytest.mark.parametrize("e", [-3, 1, 2, 4, 65536])
def test_rejects_bad_exponent(e):
    with pytest.raises(InvalidKeyError, match="odd"):
        generate_key(64, e)


def test_rejects_exponent_too_large_for_modulus():
    with pytest.raises(InvalidKeyError, match="below"):
        generate_key(64, 2**63 + 1)


def test_rejects_exponent_sharing_a_factor_with_phi():
    # (7 - 1) * (11 - 1) = 60 shares the factor 3 with e = 3.
    with pytest.raises(InvalidKeyError, match="coprime"):
        private_key_from_primes(7, 11, 3)


def test_rejects_equal_primes():
    with pytest.raises(InvalidKeyError, match="distinct"):
        private_key_from_primes(61, 61, 17)


@pytest.fixture(scope="module")
def key():
    return generate_key(256)


def test_key_files_round_trip(tmp_path, key):
    save_public_key(key.public_key, tmp_path / "k.public.json")
    save_private_key(key, tmp_path / "k.private.json")
    assert load_public_key(tmp_path / "k.public.json") == key.public_key
    assert load_private_key(tmp_path / "k.private.json") == key
    # Encrypting only needs the public half, so a private key file also works.
    assert load_public_key(tmp_path / "k.private.json") == key.public_key


@pytest.mark.skipif(os.name != "posix", reason="POSIX file modes")
def test_private_key_file_is_owner_only(tmp_path, key):
    save_private_key(key, tmp_path / "k.private.json")
    assert (tmp_path / "k.private.json").stat().st_mode & 0o777 == 0o600


def test_decryption_needs_private_key_file(tmp_path, key):
    save_public_key(key.public_key, tmp_path / "k.public.json")
    with pytest.raises(InvalidKeyError, match="public key"):
        load_private_key(tmp_path / "k.public.json")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("not json", "cannot read"),
        ("[1, 2]", "not a bigrsa key file"),
        ('{"type": "something-else"}', "not a bigrsa key file"),
        ('{"type": "bigrsa-public-key", "n": 3233}', "'e'"),
        ('{"type": "bigrsa-public-key", "n": "3233", "e": 17}', "'n'"),
        ('{"type": "bigrsa-public-key", "n": true, "e": 17}', "'n'"),
        ('{"type": "bigrsa-public-key", "n": 3233, "e": -17}', "'e'"),
    ],
)
def test_rejects_malformed_key_files(tmp_path, content, message):
    path = tmp_path / "bad.json"
    path.write_text(content)
    with pytest.raises(InvalidKeyError, match=message):
        load_public_key(path)


def test_rejects_missing_key_file(tmp_path):
    with pytest.raises(InvalidKeyError, match="cannot read"):
        load_public_key(tmp_path / "missing.json")


def test_rejects_inconsistent_private_key(tmp_path, key):
    path = tmp_path / "k.private.json"
    save_private_key(key, path)
    data = json.loads(path.read_text())
    data["n"] += 2
    path.write_text(json.dumps(data))
    with pytest.raises(InvalidKeyError, match="p \\* q"):
        load_private_key(path)
