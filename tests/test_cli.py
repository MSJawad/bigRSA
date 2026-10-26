import io
import subprocess
import sys

import pytest

from bigrsa.cli import main


@pytest.fixture
def keypair(tmp_path, capsys):
    prefix = tmp_path / "alice"
    assert main(["keygen", "--out", str(prefix), "--bits", "512"]) == 0
    capsys.readouterr()
    return tmp_path / "alice.public.json", tmp_path / "alice.private.json"


def run(capsys, *argv):
    code = main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


def test_keygen_reports_key_details(tmp_path, capsys):
    code, out, _ = run(capsys, "keygen", "--out", str(tmp_path / "bob"))
    assert code == 0
    assert "1200-bit key from two 600-bit primes, e = 65537" in out
    assert "up to 148 bytes" in out
    assert (tmp_path / "bob.public.json").exists()
    assert (tmp_path / "bob.private.json").exists()


def test_keygen_odd_size_reports_both_prime_sizes(tmp_path, capsys):
    code, out, _ = run(capsys, "keygen", "--out", str(tmp_path / "k"), "--bits", "129")
    assert code == 0
    assert "129-bit key from 65- and 64-bit primes" in out


def test_encrypt_decrypt_round_trip(keypair, capsys):
    public, private = keypair
    code, ciphertext, _ = run(capsys, "encrypt", "--key", str(public), "naïve café 🔐")
    assert code == 0
    code, plaintext, _ = run(capsys, "decrypt", "--key", str(private), ciphertext.strip())
    assert code == 0
    assert plaintext == "naïve café 🔐\n"


def test_stdin_round_trip(keypair, capsys, monkeypatch):
    public, private = keypair
    monkeypatch.setattr(sys, "stdin", io.StringIO("from stdin\n"))
    _, ciphertext, _ = run(capsys, "encrypt", "-k", str(public), "-")
    monkeypatch.setattr(sys, "stdin", io.StringIO(ciphertext))
    _, plaintext, _ = run(capsys, "decrypt", "-k", str(private), "-")
    assert plaintext == "from stdin\n\n"


def test_keygen_refuses_to_overwrite(keypair, capsys):
    prefix = str(keypair[0]).removesuffix(".public.json")
    code, _, err = run(capsys, "keygen", "--out", prefix, "--bits", "64")
    assert code == 1
    assert "already exists" in err
    assert run(capsys, "keygen", "--out", prefix, "--bits", "64", "--force")[0] == 0


def test_too_long_message_fails_cleanly(keypair, capsys):
    code, out, err = run(capsys, "encrypt", "-k", str(keypair[0]), "A" * 200)
    assert code == 1
    assert out == ""
    assert "at most 62 bytes" in err


def test_bad_ciphertext_fails_cleanly(keypair, capsys):
    code, _, err = run(capsys, "decrypt", "-k", str(keypair[1]), "not-a-number")
    assert code == 1
    assert "decimal integer" in err


def test_decrypt_with_public_key_fails_cleanly(keypair, capsys):
    code, _, err = run(capsys, "decrypt", "-k", str(keypair[0]), "12345")
    assert code == 1
    assert "needs the private key" in err


def test_bad_exponent_fails_cleanly(tmp_path, capsys):
    code, _, err = run(capsys, "keygen", "--out", str(tmp_path / "k"), "-e", "4")
    assert code == 1
    assert "odd" in err
    assert not (tmp_path / "k.public.json").exists()


def test_python_dash_m_entry_point(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "bigrsa", "keygen", "--out", str(tmp_path / "k"), "--bits", "128"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "128-bit key" in result.stdout
