import pytest

from bigrsa.codec import (
    DecryptionError,
    MessageTooLongError,
    decode,
    decrypt,
    encode,
    encrypt,
    max_message_bytes,
)
from bigrsa.keys import generate_key


@pytest.fixture(scope="module")
def key():
    return generate_key(1200)


@pytest.mark.parametrize(
    "message",
    [
        "Hello, RSA!",
        "The quick brown fox jumps over the lazy dog. 0123456789 ~!@#$%^&*()_+",
        "",
        " ",
        "line one\nline two\ttabbed\r\n",
    ],
)
def test_ascii_round_trip(key, message):
    assert decrypt(encrypt(message, key.public_key), key) == message


@pytest.mark.parametrize(
    "message",
    [
        # The original scripts turned this into "na\x17[\xb5\x01 caf\x17\x03".
        "naïve café",
        "Ünïcödé ✓ 🔐🚀",
        "مرحبا بالعالم",
        "你好，世界",
        "é combining accent",
        "\x00\x00leading and trailing NUL\x00",
        "\x01starts with the marker byte",
    ],
)
def test_unicode_and_control_character_round_trip(key, message):
    assert decrypt(encrypt(message, key.public_key), key) == message


def test_max_message_bytes_for_default_key(key):
    # 1200 bits hold 149 whole bytes below the top bit; one of them is the marker.
    assert max_message_bytes(key.n) == 148


def test_maximum_length_ascii_round_trip(key):
    message = "A" * max_message_bytes(key.n)
    assert decrypt(encrypt(message, key.public_key), key) == message


def test_maximum_length_multibyte_round_trip(key):
    # "é" is 2 bytes of UTF-8 and "🔐" is 4, so this fills all 148 bytes.
    message = "é" * 70 + "🔐" * 2
    assert len(message.encode("utf-8")) == max_message_bytes(key.n)
    assert decrypt(encrypt(message, key.public_key), key) == message


def test_maximum_value_stays_below_modulus(key):
    assert encode("\xff" * (max_message_bytes(key.n) // 2), key.n) < key.n
    assert int.from_bytes(b"\x01" + b"\xff" * max_message_bytes(key.n), "big") < key.n


def test_one_byte_too_long_is_rejected(key):
    with pytest.raises(MessageTooLongError, match="149 bytes"):
        encrypt("A" * (max_message_bytes(key.n) + 1), key.public_key)


def test_long_message_is_rejected_not_corrupted(key):
    # The original scripts silently decrypted 200 "A"s to garbage.
    with pytest.raises(MessageTooLongError, match="at most 148 bytes"):
        encrypt("A" * 200, key.public_key)


def test_long_message_fits_larger_key():
    key = generate_key(2048)
    message = "A" * 200
    assert decrypt(encrypt(message, key.public_key), key) == message


def test_length_limit_counts_utf8_bytes_not_characters(key):
    # 75 characters, but 150 bytes of UTF-8.
    with pytest.raises(MessageTooLongError, match="150 bytes"):
        encrypt("é" * 75, key.public_key)


def test_textbook_rsa_is_deterministic(key):
    # No padding: the same message always gives the same ciphertext.
    assert encrypt("same", key.public_key) == encrypt("same", key.public_key)


def test_ciphertext_out_of_range(key):
    with pytest.raises(DecryptionError, match="out of range"):
        decrypt(key.n, key)
    with pytest.raises(DecryptionError, match="out of range"):
        decrypt(-1, key)


def test_wrong_key_is_detected(key):
    other = generate_key(1200)
    ciphertext = encrypt("secret message", key.public_key)
    with pytest.raises(DecryptionError):
        decrypt(ciphertext % other.n, other)


def test_decode_rejects_missing_marker():
    with pytest.raises(DecryptionError):
        decode(int.from_bytes(b"\x02abc", "big"))
    with pytest.raises(DecryptionError):
        decode(0)


def test_decode_rejects_invalid_utf8():
    with pytest.raises(DecryptionError):
        decode(int.from_bytes(b"\x01\xff\xfe", "big"))
