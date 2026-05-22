import argparse
import json
import os
import sys

import config
from wallet import (
    Wallet, MultiSigWallet, WalletDB, TransactionBuilder,
    generate_mnemonic, validate_mnemonic, mnemonic_to_seed,
    HDNode, BIP44_PATH
)
from miner import Miner


WALLET_FILE = "wallet.json"
WALLET_DB_PATH = "wallet_data/wallet.db"


def cmd_start_node(args):
    from node import start_node
    print(f"Starting Globex node on {args.host}:{args.port}...")
    start_node(host=args.host, port=args.port)


def cmd_mine(args):
    node_url = args.node or f"http://127.0.0.1:{config.NODE_PORT}"
    miner = Miner(node_url, args.address, args.threads)
    print(f"Mining on {node_url} with {args.threads} thread(s)")
    print(f"Miner address: {args.address}")
    print("Press Ctrl+C to stop")
    try:
        miner.start()
    except KeyboardInterrupt:
        miner.stop()
        print("\nMining stopped.")


def cmd_create_wallet(args):
    if args.mnemonic:
        if not validate_mnemonic(args.mnemonic):
            print("Invalid mnemonic phrase")
            sys.exit(1)
        wallet = Wallet.generate_from_mnemonic(args.mnemonic, path=args.path)
    elif args.wif:
        wallet = Wallet.from_wif(args.wif)
    else:
        wallet, mnemonic = Wallet.generate_master()
        print(f"Mnemonic: {mnemonic}")
        print("Write this down and keep it safe!\n")
    data = wallet.to_dict()
    if args.mnemonic:
        data["mnemonic"] = args.mnemonic
        data["path"] = args.path or BIP44_PATH + "/0'/0/0"
    out_path = args.file or WALLET_FILE
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wallet created: {wallet.address}")
    print(f"Private key saved to: {out_path}")
    if not args.no_db:
        try:
            db = WalletDB(WALLET_DB_PATH)
            db.save_wallet(wallet, label=args.label or "", mnemonic=getattr(args, 'mnemonic', None), path=args.path or "")
            print(f"Wallet saved to database: {WALLET_DB_PATH}")
        except Exception as e:
            print(f"Warning: Could not save to wallet DB ({e})")
    print("KEEP YOUR PRIVATE KEY SAFE!")


def cmd_restore_wallet(args):
    if not args.mnemonic:
        mnemonic = input("Enter your 12/24 word mnemonic phrase: ").strip().lower()
    else:
        mnemonic = args.mnemonic
    if not validate_mnemonic(mnemonic):
        print("Invalid mnemonic phrase - check your words and try again")
        sys.exit(1)
    wallet = Wallet.generate_from_mnemonic(mnemonic, path=args.path, passphrase=args.passphrase or "")
    data = wallet.to_dict()
    data["mnemonic"] = mnemonic
    data["path"] = args.path or BIP44_PATH + "/0'/0/0"
    out_path = args.file or WALLET_FILE
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wallet restored: {wallet.address}")
    print(f"Private key saved to: {out_path}")


def cmd_wallet_info(args):
    wallet_path = args.key or WALLET_FILE
    if not os.path.exists(wallet_path):
        print(f"Wallet file not found: {wallet_path}")
        sys.exit(1)
    with open(wallet_path) as f:
        data = json.load(f)
    wallet = Wallet.from_dict(data)
    print(f"Address:     {wallet.address}")
    print(f"Public Key:  {wallet.public_key.hex()}")
    print(f"Private Key: {wallet.sk.to_string().hex()[:16]}...")
    print(f"WIF:         {wallet.get_wif()}")
    if "mnemonic" in data:
        print(f"Mnemonic:    {data['mnemonic'][:32]}...")
    if "path" in data:
        print(f"Derivation:  {data['path']}")


def cmd_encrypt_wallet(args):
    wallet_path = args.key or WALLET_FILE
    if not os.path.exists(wallet_path):
        print(f"Wallet file not found: {wallet_path}")
        sys.exit(1)
    with open(wallet_path) as f:
        data = json.load(f)
    wallet = Wallet.from_dict(data)
    passphrase = args.passphrase or input("Enter encryption passphrase: ")
    encrypted = wallet.encrypt(passphrase)
    enc_path = f"{wallet_path}.enc"
    with open(enc_path, "w") as f:
        json.dump(encrypted, f, indent=2)
    print(f"Wallet encrypted: {wallet.address}")
    print(f"Encrypted file: {enc_path}")


def cmd_decrypt_wallet(args):
    wallet_path = args.file or f"{WALLET_FILE}.enc"
    if not os.path.exists(wallet_path):
        print(f"Encrypted file not found: {wallet_path}")
        sys.exit(1)
    with open(wallet_path) as f:
        encrypted = json.load(f)
    if encrypted.get("type") != "encrypted":
        print("Invalid encrypted wallet format")
        sys.exit(1)
    passphrase = args.passphrase or input("Enter decryption passphrase: ")
    try:
        wallet = Wallet.decrypt(encrypted, passphrase)
    except Exception:
        print("Decryption failed - wrong passphrase or corrupted data")
        sys.exit(1)
    data = wallet.to_dict()
    out_path = args.output or WALLET_FILE
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wallet decrypted: {wallet.address}")
    print(f"Saved to: {out_path}")


def cmd_sign_message(args):
    wallet_path = args.key or WALLET_FILE
    if not os.path.exists(wallet_path):
        print(f"Wallet file not found: {wallet_path}")
        sys.exit(1)
    with open(wallet_path) as f:
        data = json.load(f)
    wallet = Wallet.from_dict(data)
    message = args.message or input("Enter message to sign: ")
    signature = wallet.sign_message(message)
    print(f"Address:   {wallet.address}")
    print(f"Message:   {message}")
    print(f"Signature: {signature}")


def cmd_verify_message(args):
    address = args.address
    message = args.message
    signature = args.signature
    if not all([address, message, signature]):
        print("Usage: verify-message --address <addr> --message <msg> --signature <sig>")
        sys.exit(1)
    result = Wallet.verify_message(address, message, signature)
    if result:
        print("Signature: VALID")
    else:
        print("Signature: INVALID (message may be tampered or wrong key)")
        sys.exit(1)


def cmd_send(args):
    node_url = args.node or f"http://127.0.0.1:{config.NODE_PORT}"
    import requests
    wallet_path = args.key or WALLET_FILE
    if not os.path.exists(wallet_path):
        print(f"Wallet file not found: {wallet_path}")
        sys.exit(1)
    with open(wallet_path) as f:
        wallet_data = json.load(f)
    wallet = Wallet.from_dict(wallet_data)
    bal_resp = requests.get(f"{node_url}/balance/{wallet.address}", timeout=10)
    balance = bal_resp.json().get("balance", 0)
    total_cost = args.amount + (args.fee or 0)
    if balance < total_cost:
        print(f"Insufficient balance. Have {balance / config.GBX:.2f} GBX, need {total_cost / config.GBX:.2f} GBX")
        sys.exit(1)
    tx = TransactionBuilder.create(wallet.address, args.to, args.amount, args.fee or 0, nonce=args.nonce or 0)
    signed_tx = wallet.sign_transaction(tx)
    if args.memo:
        signed_tx["memo"] = args.memo
    resp = requests.post(f"{node_url}/transactions/new", json=signed_tx, timeout=10)
    if resp.status_code == 200:
        result = resp.json()
        tx_hash = result.get("tx_hash", "")
        print(f"Transaction sent: {tx_hash}")
        try:
            db = WalletDB(WALLET_DB_PATH)
            db.record_transaction(tx_hash, wallet.address, "send", args.amount, args.fee or 0, counterparty=args.to, memo=args.memo or "")
        except Exception:
            pass
    else:
        print(f"Failed: {resp.json().get('detail', 'unknown error')}")
        sys.exit(1)


def cmd_balance(args):
    node_url = args.node or f"http://127.0.0.1:{config.NODE_PORT}"
    import requests
    resp = requests.get(f"{node_url}/balance/{args.address}", timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Address: {data['address']}")
        print(f"Balance: {data['balance'] / config.GBX:.8f} GBX")
        print(f"Raw: {data['balance']}")
    else:
        print(f"Failed: {resp.json().get('detail', 'unknown error')}")
        sys.exit(1)


def cmd_generate_mnemonic(args):
    strength = args.strength or 256
    mnemonic = generate_mnemonic(strength)
    print(f"Mnemonic ({len(mnemonic.split())} words):")
    print(mnemonic)
    print("\nWrite this down and keep it safe! Do not store digitally.")


def cmd_multisig_address(args):
    if not args.public_keys:
        print("Provide at least 2 public keys in hex format")
        sys.exit(1)
    public_keys = [pk.strip() for pk in args.public_keys.split(",")]
    if len(public_keys) < 2:
        print("Multi-sig requires at least 2 public keys")
        sys.exit(1)
    address, redeem_script = Wallet.create_multisig_address(public_keys, args.required)
    print(f"Multi-Sig Address ({args.required}/{len(public_keys)}):")
    print(f"Address:       {address}")
    print(f"Redeem Script: {redeem_script}")
    print(f"Public Keys: {len(public_keys)}")
    for i, pk in enumerate(public_keys):
        print(f"  [{i + 1}] {pk[:16]}...")


def cmd_list_wallets(args):
    db_path = args.db or WALLET_DB_PATH
    if not os.path.exists(db_path):
        print(f"No wallet database found at {db_path}")
        sys.exit(1)
    try:
        db = WalletDB(db_path)
        wallets = db.list_wallets()
        if not wallets:
            print("No wallets in database")
            return
        print(f"{'Address':<36} {'Label':<16} {'Balance':<14} {'HD':<4} {'Last Used'}")
        print("-" * 90)
        for w in wallets:
            addr = w["address"][:34] + ".."
            label = (w["label"] or "-")[:14]
            balance = w.get("balance", 0)
            bal_str = f"{balance / config.GBX:.4f}" if balance else "0.0000"
            is_hd = "Y" if w.get("is_hd") else "N"
            last = time.strftime("%Y-%m-%d %H:%M", time.localtime(w.get("last_used", 0))) if w.get("last_used") else "-"
            print(f"{addr:<36} {label:<16} {bal_str:<14} {is_hd:<4} {last}")
    except Exception as e:
        print(f"Error reading wallet database: {e}")
        sys.exit(1)


import time as time_module
time = time_module


def cmd_tx_history(args):
    db_path = args.db or WALLET_DB_PATH
    if not os.path.exists(db_path):
        print(f"No wallet database found at {db_path}")
        sys.exit(1)
    try:
        db = WalletDB(db_path)
        txs = db.get_transaction_history(address=args.address, limit=args.limit or 20)
        if not txs:
            print("No transactions found")
            return
        print(f"{'Tx Hash':<20} {'Type':<8} {'Amount':<14} {'Fee':<10} {'Time'}")
        print("-" * 80)
        for tx in txs:
            txh = tx["tx_hash"][:16] + ".."
            amt_str = f"{tx['amount'] / config.GBX:.4f}"
            fee_str = f"{tx['fee'] / config.GBX:.4f}"
            ts = time.strftime("%m-%d %H:%M", time.localtime(tx["timestamp"])) if tx["timestamp"] else "-"
            print(f"{txh:<20} {tx['type']:<8} {amt_str:<14} {fee_str:<10} {ts}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Globex GBX CLI - Cryptocurrency Node, Wallet & Tools"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("start-node", help="Start a Globex node")
    p_start.add_argument("--host", default="0.0.0.0")
    p_start.add_argument("--port", type=int, default=config.NODE_PORT)

    p_mine = sub.add_parser("mine", help="Start CPU mining")
    p_mine.add_argument("--address", required=True)
    p_mine.add_argument("--threads", type=int, default=1)
    p_mine.add_argument("--node")

    p_wallet = sub.add_parser("create-wallet", help="Create a new wallet")
    p_wallet.add_argument("--file", default=WALLET_FILE)
    p_wallet.add_argument("--mnemonic", help="Restore from mnemonic phrase")
    p_wallet.add_argument("--wif", help="Import from WIF private key")
    p_wallet.add_argument("--path", default=BIP44_PATH + "/0'/0/0", help="BIP44 derivation path")
    p_wallet.add_argument("--label", default="", help="Wallet label for database")
    p_wallet.add_argument("--no-db", action="store_true", help="Skip saving to wallet database")

    p_restore = sub.add_parser("restore-wallet", help="Restore wallet from mnemonic")
    p_restore.add_argument("--mnemonic", help="Mnemonic phrase (omit for prompt)")
    p_restore.add_argument("--file", default=WALLET_FILE)
    p_restore.add_argument("--path", default=BIP44_PATH + "/0'/0/0")
    p_restore.add_argument("--passphrase", default="")

    p_info = sub.add_parser("wallet-info", help="Show wallet details")
    p_info.add_argument("--key", help="Path to wallet file")

    p_enc = sub.add_parser("encrypt-wallet", help="Encrypt wallet file")
    p_enc.add_argument("--key", help="Path to wallet file")
    p_enc.add_argument("--passphrase", help="Encryption passphrase")

    p_dec = sub.add_parser("decrypt-wallet", help="Decrypt wallet file")
    p_dec.add_argument("--file", help="Path to encrypted wallet file")
    p_dec.add_argument("--output", help="Output path for decrypted wallet")
    p_dec.add_argument("--passphrase", help="Decryption passphrase")

    p_sign = sub.add_parser("sign-message", help="Sign a message with wallet")
    p_sign.add_argument("--key", help="Path to wallet file")
    p_sign.add_argument("--message", help="Message to sign")

    p_verify = sub.add_parser("verify-message", help="Verify a signed message")
    p_verify.add_argument("--address", required=True)
    p_verify.add_argument("--message", required=True)
    p_verify.add_argument("--signature", required=True)

    p_send = sub.add_parser("send", help="Send GBX to an address")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--amount", type=int, required=True)
    p_send.add_argument("--fee", type=int, default=0)
    p_send.add_argument("--nonce", type=int, default=0)
    p_send.add_argument("--key")
    p_send.add_argument("--node")
    p_send.add_argument("--memo", default="")

    p_bal = sub.add_parser("balance", help="Check address balance")
    p_bal.add_argument("--address", required=True)
    p_bal.add_argument("--node")

    p_mnem = sub.add_parser("generate-mnemonic", help="Generate mnemonic phrase")
    p_mnem.add_argument("--strength", type=int, default=256, choices=[128, 160, 192, 224, 256])

    p_multi = sub.add_parser("multisig-address", help="Create multisig address")
    p_multi.add_argument("--public-keys", required=True, help="Comma-separated hex public keys")
    p_multi.add_argument("--required", type=int, default=2)

    p_list = sub.add_parser("list-wallets", help="List wallets in database")
    p_list.add_argument("--db", help="Wallet database path")

    p_txhist = sub.add_parser("tx-history", help="Show transaction history")
    p_txhist.add_argument("--address", help="Filter by address")
    p_txhist.add_argument("--limit", type=int, default=20)
    p_txhist.add_argument("--db")

    args = parser.parse_args()

    commands = {
        "start-node": cmd_start_node,
        "mine": cmd_mine,
        "create-wallet": cmd_create_wallet,
        "restore-wallet": cmd_restore_wallet,
        "wallet-info": cmd_wallet_info,
        "encrypt-wallet": cmd_encrypt_wallet,
        "decrypt-wallet": cmd_decrypt_wallet,
        "sign-message": cmd_sign_message,
        "verify-message": cmd_verify_message,
        "send": cmd_send,
        "balance": cmd_balance,
        "generate-mnemonic": cmd_generate_mnemonic,
        "multisig-address": cmd_multisig_address,
        "list-wallets": cmd_list_wallets,
        "tx-history": cmd_tx_history,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()