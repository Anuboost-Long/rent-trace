import base64
import hashlib
import os
import secrets
import tempfile
from pathlib import Path

MIN_KEY_BYTES = 32
MIN_WORDS = 4
MIN_WORDS_LENGTH = 20
KEY_BYTES = 48

SCRYPT_COST = 2**17
SCRYPT_BLOCK_SIZE = 8
SCRYPT_PARALLELISM = 1
SCRYPT_MAX_MEMORY = 256 * 1024 * 1024


def generate_random_key():
    return secrets.token_urlsafe(KEY_BYTES)


def derive_key_from_words(words, label):
    stretched = hashlib.scrypt(
        words.encode(),
        salt=f"renttrace-jwt-signing-key:{label}".encode(),
        n=SCRYPT_COST,
        r=SCRYPT_BLOCK_SIZE,
        p=SCRYPT_PARALLELISM,
        maxmem=SCRYPT_MAX_MEMORY,
        dklen=KEY_BYTES,
    )
    return base64.urlsafe_b64encode(stretched).decode().rstrip("=")


def words_problem(words):
    if len(words.split()) < MIN_WORDS:
        return f"Use at least {MIN_WORDS} words."
    if len(words) < MIN_WORDS_LENGTH:
        return f"Use at least {MIN_WORDS_LENGTH} characters in total."
    return None


def write_env_value(env_file, name, value):
    path = Path(env_file)
    lines = path.read_text().splitlines() if path.exists() else []
    entry = f"{name}={value}"
    updated = [entry if line.startswith(f"{name}=") else line for line in lines]
    if entry not in updated:
        updated.append(entry)

    mode = path.stat().st_mode if path.exists() else 0o600
    with tempfile.NamedTemporaryFile("w", dir=path.parent, delete=False) as temporary:
        temporary.write("\n".join(updated) + "\n")
    os.chmod(temporary.name, mode)
    os.replace(temporary.name, path)
