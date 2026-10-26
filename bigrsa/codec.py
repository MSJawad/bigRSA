"""Text <-> integer encoding and textbook RSA encryption.

A message is encoded as UTF-8 and read as one big-endian integer, prefixed
with a 0x01 marker byte so that leading zero bytes survive the round trip.
The integer must be smaller than the modulus n, so a message may hold at most
max_message_bytes(n) bytes of UTF-8. Longer messages are rejected rather than
silently corrupted.
"""

from .keys import PrivateKey, PublicKey

_MARKER = b"\x01"


class MessageTooLongError(ValueError):
    """The message does not fit in one block of the key's modulus."""


class DecryptionError(ValueError):
    """The ciphertext is malformed, or was not made with this key."""


def max_message_bytes(n: int) -> int:
    """The longest UTF-8 message, in bytes, that a modulus n can carry.

    The marker plus the message must fit in n.bit_length() - 1 bits, which
    keeps the encoded integer below n for any n of that bit length.
    """
    return max((n.bit_length() - 1) // 8 - len(_MARKER), 0)


def encode(message: str, n: int) -> int:
    data = message.encode("utf-8")
    limit = max_message_bytes(n)
    if len(data) > limit:
        raise MessageTooLongError(
            f"message is {len(data)} bytes of UTF-8, but a {n.bit_length()}-bit key "
            f"can encrypt at most {limit} bytes"
        )
    return int.from_bytes(_MARKER + data, "big")


def decode(m: int) -> str:
    raw = m.to_bytes((m.bit_length() + 7) // 8, "big")
    if not raw.startswith(_MARKER):
        raise DecryptionError("decryption failed: wrong key or corrupted ciphertext")
    try:
        return raw[len(_MARKER) :].decode("utf-8")
    except UnicodeDecodeError as err:
        raise DecryptionError("decryption failed: wrong key or corrupted ciphertext") from err


def encrypt(message: str, key: PublicKey) -> int:
    return pow(encode(message, key.n), key.e, key.n)


def decrypt(ciphertext: int, key: PrivateKey) -> str:
    if not 0 <= ciphertext < key.n:
        raise DecryptionError("ciphertext is out of range for this key")
    return decode(pow(ciphertext, key.d, key.n))
