"""Command line interface: python -m bigrsa keygen|encrypt|decrypt."""

import argparse
import sys
from pathlib import Path

from . import codec, keys


class CLIError(Exception):
    pass


def _read_arg(value: str) -> str:
    """Return value, or all of standard input when value is '-'."""
    return sys.stdin.read() if value == "-" else value


def _keygen(args: argparse.Namespace) -> None:
    public_path = Path(f"{args.out}.public.json")
    private_path = Path(f"{args.out}.private.json")
    if not args.force:
        for path in (public_path, private_path):
            if path.exists():
                raise CLIError(f"{path} already exists (pass --force to overwrite it)")
    key = keys.generate_key(args.bits, args.e)
    keys.save_public_key(key.public_key, public_path)
    keys.save_private_key(key, private_path)
    p_bits, q_bits = key.p.bit_length(), key.q.bit_length()
    primes = f"two {p_bits}-bit primes" if p_bits == q_bits else f"{p_bits}- and {q_bits}-bit primes"
    print(f"Generated a {key.bits}-bit key from {primes}, e = {key.e}")
    print(f"Public key:  {public_path}")
    print(f"Private key: {private_path} (keep this one secret)")
    print(f"Messages can be up to {codec.max_message_bytes(key.n)} bytes of UTF-8")


def _encrypt(args: argparse.Namespace) -> None:
    key = keys.load_public_key(args.key)
    print(codec.encrypt(_read_arg(args.message), key))


def _decrypt(args: argparse.Namespace) -> None:
    key = keys.load_private_key(args.key)
    text = _read_arg(args.ciphertext).strip()
    try:
        ciphertext = int(text)
    except ValueError:
        raise CLIError("ciphertext must be a decimal integer") from None
    print(codec.decrypt(ciphertext, key))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bigrsa",
        description="Textbook RSA for learning. Not for real data: there is no padding.",
    )
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    keygen = commands.add_parser("keygen", help="generate a key pair")
    keygen.add_argument(
        "-o",
        "--out",
        default="bigrsa",
        metavar="PREFIX",
        help="write PREFIX.public.json and PREFIX.private.json (default: %(default)s)",
    )
    keygen.add_argument(
        "--bits",
        type=int,
        default=keys.DEFAULT_BITS,
        help="modulus size in bits (default: %(default)s)",
    )
    keygen.add_argument(
        "-e",
        type=int,
        default=keys.DEFAULT_EXPONENT,
        help="public exponent (default: %(default)s)",
    )
    keygen.add_argument("--force", action="store_true", help="overwrite existing key files")
    keygen.set_defaults(func=_keygen)

    encrypt = commands.add_parser("encrypt", help="encrypt a message with a public key")
    encrypt.add_argument("-k", "--key", type=Path, required=True, help="public or private key file")
    encrypt.add_argument("message", help="text to encrypt, or - to read standard input")
    encrypt.set_defaults(func=_encrypt)

    decrypt = commands.add_parser("decrypt", help="decrypt a ciphertext with a private key")
    decrypt.add_argument("-k", "--key", type=Path, required=True, help="private key file")
    decrypt.add_argument("ciphertext", help="decimal ciphertext, or - to read standard input")
    decrypt.set_defaults(func=_decrypt)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.func(args)
    except (CLIError, ValueError, OSError) as err:
        print(f"bigrsa: error: {err}", file=sys.stderr)
        return 1
    return 0
