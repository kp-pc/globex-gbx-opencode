import json
import ecdsa
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import utils


class Wallet:
    def __init__(self, private_key: bytes = None):
        if private_key:
            self.sk = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.sk = SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.verifying_key
        self.public_key = self.vk.to_string("compressed")
        self.address = utils.address_from_public_key(self.public_key)

    def sign(self, message: bytes) -> bytes:
        return self.sk.sign(message)

    def sign_transaction(self, tx: dict) -> dict:
        signed_tx = {k: v for k, v in tx.items() if k != "signature"}
        signed_tx["public_key"] = self.public_key.hex()
        message = json.dumps(signed_tx, sort_keys=True).encode()
        signed_tx["signature"] = self.sign(message).hex()
        return signed_tx

    def to_dict(self) -> dict:
        return {
            "private_key": self.sk.to_string().hex(),
            "public_key": self.public_key.hex(),
            "address": self.address
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(private_key=bytes.fromhex(d["private_key"]))

    @staticmethod
    def verify_transaction(tx: dict) -> bool:
        if not tx.get("signature") or not tx.get("public_key"):
            return False
        expected_addr = utils.address_from_public_key(bytes.fromhex(tx["public_key"]))
        if expected_addr != tx.get("sender"):
            return False
        sig_bytes = bytes.fromhex(tx["signature"])
        pub_bytes = bytes.fromhex(tx["public_key"])
        verify_tx = {k: v for k, v in tx.items() if k != "signature"}
        message = json.dumps(verify_tx, sort_keys=True).encode()
        vk = VerifyingKey.from_string(pub_bytes, curve=SECP256k1)
        try:
            return vk.verify(sig_bytes, message)
        except ecdsa.BadSignatureError:
            return False


def create_transaction(sender: str, recipient: str, amount: int,
                       fee: int = 0, nonce: int = 0) -> dict:
    return {
        "sender": sender,
        "recipient": recipient,
        "amount": amount,
        "fee": fee,
        "timestamp": __import__("time").time(),
        "nonce": nonce,
        "public_key": "",
        "signature": ""
    }
