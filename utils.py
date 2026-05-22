import hashlib
import struct

ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def sha256d(data: bytes) -> bytes:
    return sha256(sha256(data))


def ripemd160(data: bytes) -> bytes:
    return hashlib.new("ripemd160", data).digest()


def hash160(data: bytes) -> bytes:
    return ripemd160(sha256(data))


def base58_encode(data: bytes) -> str:
    n = int.from_bytes(data, "big")
    chars = []
    while n > 0:
        n, r = divmod(n, 58)
        chars.append(ALPHABET[r])
    for b in data:
        if b == 0:
            chars.append(ALPHABET[0])
        else:
            break
    return "".join(reversed(chars))


def base58_decode(s: str) -> bytes:
    n = 0
    for c in s:
        n = n * 58 + ALPHABET.index(c)
    prefix = b"\x00" * (len(s) - len(s.lstrip("1")))
    result = prefix + n.to_bytes((n.bit_length() + 7) // 8, "big")
    return result


def base58_check_encode(data: bytes, version: int = 0) -> str:
    payload = bytes([version]) + data
    checksum = sha256d(payload)[:4]
    return base58_encode(payload + checksum)


def base58_check_decode(s: str) -> bytes:
    decoded = base58_decode(s)
    payload, checksum = decoded[:-4], decoded[-4:]
    if sha256d(payload)[:4] != checksum:
        raise ValueError("Invalid checksum")
    return payload[1:]


def address_from_public_key(pubkey: bytes) -> str:
    return base58_check_encode(hash160(pubkey), version=0)


def address_to_hash160(address: str) -> bytes:
    return base58_check_decode(address)


def merkle_root(hashes: list[bytes]) -> bytes:
    if not hashes:
        return b"\x00" * 32
    layer = list(hashes)
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [sha256d(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
    return layer[0]
