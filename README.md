# bigRSA

[![CI](https://github.com/MSJawad/bigRSA/actions/workflows/ci.yml/badge.svg)](https://github.com/MSJawad/bigRSA/actions/workflows/ci.yml)

RSA from scratch in pure Python, with no dependencies. bigrsa generates its own large primes using
small-prime trial division and the Miller-Rabin test, builds RSA keys from them (a 1200-bit
modulus from two 600-bit primes by default), and encrypts and decrypts text from the command line.

> [!WARNING]
> **This is textbook RSA. It is for learning only: do not use it for real data.**
> It has no padding (such as OAEP), so encryption is deterministic and malleable, and it makes no
> attempt to resist timing or other side-channel attacks. For real cryptography, use a vetted
> library such as [`cryptography`](https://cryptography.io/).

## Quick start

You need Python 3.10 or newer. No install is needed to run from a clone:

```console
$ git clone https://github.com/MSJawad/bigRSA.git && cd bigRSA

$ python3 -m bigrsa keygen --out alice
Generated a 1200-bit key from two 600-bit primes, e = 65537
Public key:  alice.public.json
Private key: alice.private.json (keep this one secret)
Messages can be up to 148 bytes of UTF-8

$ python3 -m bigrsa encrypt --key alice.public.json "Hello, RSA! Ünïcödé works too 🔐" > message.txt

$ python3 -m bigrsa decrypt --key alice.private.json - < message.txt
Hello, RSA! Ünïcödé works too 🔐
```

The ciphertext in `message.txt` is a single decimal number below the modulus, about 361 digits
long (`690582947504475037282951360347132681722410037882286613149095...`).

A message that does not fit in the modulus is rejected instead of being silently corrupted:

```console
$ python3 -m bigrsa encrypt --key alice.public.json "$(printf 'A%.0s' {1..200})"
bigrsa: error: message is 200 bytes of UTF-8, but a 1200-bit key can encrypt at most 148 bytes
```

Pass `--bits 2048` (up to 8192) to `keygen` for room for longer messages, and `-e` to choose
another public exponent. `encrypt` and `decrypt` read standard input when the message or
ciphertext is `-`. Run `python3 -m bigrsa <command> --help` for every option.

`pip install .` also installs a `bigrsa` command that does the same thing as `python3 -m bigrsa`.

## How it works

| Module | What it does |
| --- | --- |
| [`bigrsa/primes.py`](bigrsa/primes.py) | `generate_prime(bits)` draws random odd numbers with the top two bits set and keeps the first that passes `is_probable_prime`. That function first divides by the 168 primes below 1000, which rules out most candidates cheaply, then runs Miller-Rabin. Below about 3.3 * 10^24 it uses the first 13 primes as bases, which makes the answer exact. Above that it uses 40 random bases, so a composite gets through with probability at most 2^-80. |
| [`bigrsa/keys.py`](bigrsa/keys.py) | `generate_key(bits, e)` picks primes p and q until gcd(e, (p-1)(q-1)) = 1, then sets n = pq and d = e^-1 mod (p-1)(q-1). Keys are saved as JSON. The private key file is made readable by its owner only. |
| [`bigrsa/codec.py`](bigrsa/codec.py) | A message is encoded as UTF-8, with a marker byte in front so that leading zero bytes survive, and read as one big-endian integer m < n. Encryption is c = m^e mod n, and decryption is m = c^d mod n. Decryption with the wrong key is detected and reported. |
| [`bigrsa/cli.py`](bigrsa/cli.py) | The `keygen`, `encrypt` and `decrypt` commands. |

The same functions work as a library:

```python
import bigrsa

key = bigrsa.generate_key(1200)
ciphertext = bigrsa.encrypt("hello", key.public_key)
assert bigrsa.decrypt(ciphertext, key) == "hello"
```

RSA is one of the first public-key cryptosystems, published by Ron Rivest, Adi Shamir and Leonard
Adleman in 1977. Its security rests on the difficulty of factoring n back into p and q: nobody
knows an efficient classical algorithm for that.

## Development

```console
$ python3 -m venv .venv && source .venv/bin/activate
$ python -m pip install -e ".[dev]"
$ python -m pytest
$ ruff check . && ruff format --check .
```

The tests cover the following:

- Round trips for ASCII, Unicode and maximum-length messages, plus the rejection of messages that are too long.
- Miller-Rabin against every number below 20,000, Mersenne primes, Carmichael numbers such as 561 and 41041, and the smallest strong pseudoprimes to the first k prime bases, for ten values of k up to 13.
- The key invariants, such as e * d = 1 mod (p-1)(q-1) and the exact modulus size.
- The CLI.

CI runs the tests on Python 3.10 to 3.13, plus `ruff check` and `ruff format --check`.

## Author

Mohammad Solaiman Jawad. Written in 2018 and restructured into a tested package in 2026.
Criticism and advice are welcome: solaimanjawad@gmail.com.

## License

[MIT](LICENSE)
