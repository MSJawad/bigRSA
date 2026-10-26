"""RSA key generation and JSON key files."""

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

from .primes import generate_prime

DEFAULT_BITS = 1200
DEFAULT_EXPONENT = 65537
MIN_BITS = 64
# Python refuses to convert integers longer than 4300 decimal digits to and
# from text by default, which caps what the key files and ciphertexts can hold.
MAX_BITS = 8192

PUBLIC_TYPE = "bigrsa-public-key"
PRIVATE_TYPE = "bigrsa-private-key"


class InvalidKeyError(ValueError):
    """A key is invalid, or a key file cannot be read."""


@dataclass(frozen=True)
class PublicKey:
    n: int
    e: int

    @property
    def bits(self) -> int:
        return self.n.bit_length()


@dataclass(frozen=True)
class PrivateKey:
    n: int
    e: int
    d: int
    p: int
    q: int

    @property
    def bits(self) -> int:
        return self.n.bit_length()

    @property
    def public_key(self) -> PublicKey:
        return PublicKey(self.n, self.e)


def private_key_from_primes(p: int, q: int, e: int = DEFAULT_EXPONENT) -> PrivateKey:
    """Build a key from two distinct primes, with d = e**-1 mod (p-1)(q-1)."""
    if p == q:
        raise InvalidKeyError("p and q must be distinct primes")
    phi = (p - 1) * (q - 1)
    if not 1 < e < phi or math.gcd(e, phi) != 1:
        raise InvalidKeyError(f"e={e} is not coprime with (p-1)(q-1) or not below it")
    return PrivateKey(n=p * q, e=e, d=pow(e, -1, phi), p=p, q=q)


def generate_key(bits: int = DEFAULT_BITS, e: int = DEFAULT_EXPONENT) -> PrivateKey:
    """Generate a key whose modulus n has exactly `bits` bits."""
    if not MIN_BITS <= bits <= MAX_BITS:
        raise InvalidKeyError(f"key size must be between {MIN_BITS} and {MAX_BITS} bits")
    # An even e shares the factor 2 with every (p-1)(q-1), so no primes could work.
    if e < 3 or e % 2 == 0:
        raise InvalidKeyError("e must be an odd integer of at least 3")
    if e.bit_length() > bits - 2:
        raise InvalidKeyError(f"e must be below 2**{bits - 2} for a {bits}-bit modulus")
    while True:
        p = generate_prime(bits - bits // 2)
        q = generate_prime(bits // 2)
        if p != q and math.gcd(e, (p - 1) * (q - 1)) == 1:
            return private_key_from_primes(p, q, e)


def save_public_key(key: PublicKey, path: Path) -> None:
    data = {"type": PUBLIC_TYPE, "bits": key.bits, "e": key.e, "n": key.n}
    path.write_text(json.dumps(data, indent=2) + "\n")


def save_private_key(key: PrivateKey, path: Path) -> None:
    data = {
        "type": PRIVATE_TYPE,
        "bits": key.bits,
        "e": key.e,
        "n": key.n,
        "d": key.d,
        "p": key.p,
        "q": key.q,
    }
    # Create the file readable by its owner only, before writing the secret.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(json.dumps(data, indent=2) + "\n")


def _read_key_file(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as err:
        raise InvalidKeyError(f"cannot read key file {path}: {err}") from err
    if not isinstance(data, dict) or data.get("type") not in (PUBLIC_TYPE, PRIVATE_TYPE):
        raise InvalidKeyError(f"{path} is not a bigrsa key file")
    return data


def _get_int(data: dict, field: str, path: Path) -> int:
    value = data.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise InvalidKeyError(f"{path}: field {field!r} must be a positive integer")
    return value


def load_public_key(path: Path) -> PublicKey:
    """Load the public key from a public or a private key file."""
    data = _read_key_file(path)
    return PublicKey(n=_get_int(data, "n", path), e=_get_int(data, "e", path))


def load_private_key(path: Path) -> PrivateKey:
    data = _read_key_file(path)
    if data["type"] != PRIVATE_TYPE:
        raise InvalidKeyError(f"{path} holds a public key; decryption needs the private key")
    fields = {f: _get_int(data, f, path) for f in ("n", "e", "d", "p", "q")}
    key = PrivateKey(**fields)
    if key.p * key.q != key.n:
        raise InvalidKeyError(f"{path}: p * q does not equal n")
    return key
