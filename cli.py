import argparse
import json
import os
import sys

import config
from wallet import Wallet, WalletError, create_transaction
from miner import Miner


WALLET_FILE = "wallet.json"


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


def _prompt_password(confirm: bool = False) -> str:
    import getpass
    pw = getpass.getpass("Wallet password: ")
    if confirm:
        pw2 = getpass.getpass("Confirm password: ")
        if pw != pw2:
            print("Passwords do not match")
            sys.exit(1)
    if pw and len(pw) < 8:
        print("Warning: short passwords are not secure")
    return pw


def cmd_create_wallet(args):
    wallet = Wallet()
    password = None
    if args.password:
        password = _prompt_password(confirm=True)
    wallet.save(args.file, password=password)
    print(f"Wallet created: {wallet.address}")
    print(f"Saved to: {args.file}")
    if password:
        print("Wallet is password-protected")
    else:
        print("WARNING: Private key is stored in plaintext")
        print("Use --password or --seed for secure storage")


def cmd_seed(args):
    wallet = Wallet()
    phrase = wallet.to_seed_phrase(word_count=args.words)
    print(f"Seed phrase ({args.words} words):")
    print()
    print(phrase)
    print()
    print(f"Derived address: {wallet.address}")
    print()
    password = None
    if args.password:
        password = _prompt_password(confirm=True)
    wallet.save(args.file, password=password)
    print(f"Wallet saved to: {args.file}")
    print("Write down your seed phrase and keep it safe!")
    print("It can recover your wallet on any device.")


def cmd_recover(args):
    print("Enter your seed phrase (12-24 words):")
    phrase = sys.stdin.readline().strip()
    passphrase = args.passphrase or ""
    try:
        wallet = Wallet.from_seed_phrase(phrase, passphrase)
    except WalletError as e:
        print(f"Error: {e}")
        sys.exit(1)
    password = None
    if args.password:
        password = _prompt_password(confirm=True)
    dest = args.file or f"wallet_{wallet.address[:8]}.json"
    wallet.save(dest, password=password)
    print(f"Wallet recovered: {wallet.address}")
    print(f"Saved to: {dest}")


def cmd_export_wif(args):
    password = None
    if args.password:
        password = _prompt_password()
    try:
        wallet = Wallet.load(args.file, password=password)
    except WalletError as e:
        print(f"Error: {e}")
        sys.exit(1)
    wif = wallet.to_wif(compressed=True)
    print(f"Address: {wallet.address}")
    print(f"WIF (private key): {wif}")
    print("KEEP THIS SAFE! Anyone with it controls your funds.")


def cmd_import_wif(args):
    wif = args.wif
    try:
        wallet = Wallet.from_wif(wif)
    except WalletError as e:
        print(f"Error: {e}")
        sys.exit(1)
    password = None
    if args.password:
        password = _prompt_password(confirm=True)
    dest = args.file or f"wallet_{wallet.address[:8]}.json"
    wallet.save(dest, password=password)
    print(f"Wallet imported: {wallet.address}")
    print(f"Saved to: {dest}")


def cmd_send(args):
    node_url = args.node or f"http://127.0.0.1:{config.NODE_PORT}"
    import requests
    wallet_path = args.key or WALLET_FILE
    if not os.path.exists(wallet_path):
        print(f"Wallet file not found: {wallet_path}")
        sys.exit(1)
    password = None
    if args.password:
        password = _prompt_password()
    try:
        wallet = Wallet.load(wallet_path, password=password)
    except WalletError as e:
        print(f"Error: {e}")
        sys.exit(1)
    bal_resp = requests.get(f"{node_url}/balance/{wallet.address}", timeout=10)
    balance = bal_resp.json().get("balance", 0)
    total_cost = args.amount + (args.fee or 0)
    if balance < total_cost:
        print(f"Insufficient balance. Have {balance / config.GBX:.2f} GBX, need {total_cost / config.GBX:.2f} GBX")
        sys.exit(1)
    tx = create_transaction(wallet.address, args.to, args.amount, args.fee or 0)
    signed_tx = wallet.sign_transaction(tx)
    resp = requests.post(f"{node_url}/transactions/new", json=signed_tx, timeout=10)
    if resp.status_code == 200:
        result = resp.json()
        print(f"Transaction sent: {result.get('tx_hash', 'unknown')}")
    else:
        print(f"Failed: {resp.json().get('detail', 'unknown error')}")
        sys.exit(1)


def cmd_wallet_info(args):
    password = None
    if args.password:
        password = _prompt_password()
    try:
        wallet = Wallet.load(args.file, password=password)
    except WalletError as e:
        print(f"Error: {e}")
        sys.exit(1)
    wif = wallet.to_wif(compressed=True)
    print(f"Address:      {wallet.address}")
    print(f"Public key:   {wallet.public_key.hex()}")
    print(f"Private key:  {wallet.private_key.hex()}")
    print(f"WIF:          {wif}")
    print(f"Encrypted:    {'Yes' if password else 'No'}")


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


def main():
    parser = argparse.ArgumentParser(
        description="Globex GBX CLI - Cryptocurrency Node & Wallet"
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
    p_wallet.add_argument("--password", action="store_true", help="Encrypt wallet with password")

    p_seed = sub.add_parser("create-seed", help="Create wallet from seed phrase")
    p_seed.add_argument("--file", default=WALLET_FILE)
    p_seed.add_argument("--words", type=int, default=12, choices=[12, 15, 18, 21, 24])
    p_seed.add_argument("--password", action="store_true", help="Encrypt wallet file with password")

    p_recover = sub.add_parser("recover", help="Recover wallet from seed phrase")
    p_recover.add_argument("--file", help="Output wallet file")
    p_recover.add_argument("--passphrase", help="Optional BIP39 passphrase")
    p_recover.add_argument("--password", action="store_true", help="Encrypt wallet file with password")

    p_wif_export = sub.add_parser("export-wif", help="Export private key in WIF format")
    p_wif_export.add_argument("--file", default=WALLET_FILE)
    p_wif_export.add_argument("--password", action="store_true", help="Wallet is password-protected")

    p_wif_import = sub.add_parser("import-wif", help="Import wallet from WIF private key")
    p_wif_import.add_argument("--wif", required=True, help="WIF private key string")
    p_wif_import.add_argument("--file", help="Output wallet file")
    p_wif_import.add_argument("--password", action="store_true", help="Encrypt wallet file with password")

    p_info = sub.add_parser("wallet-info", help="Show wallet details")
    p_info.add_argument("--file", default=WALLET_FILE)
    p_info.add_argument("--password", action="store_true", help="Wallet is password-protected")

    p_send = sub.add_parser("send", help="Send GBX to an address")
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--amount", type=int, required=True)
    p_send.add_argument("--fee", type=int, default=0)
    p_send.add_argument("--key", help="Wallet file path")
    p_send.add_argument("--password", action="store_true", help="Wallet is password-protected")
    p_send.add_argument("--node")

    p_bal = sub.add_parser("balance", help="Check address balance")
    p_bal.add_argument("--address", required=True)
    p_bal.add_argument("--node")

    args = parser.parse_args()
    commands = {
        "start-node": cmd_start_node,
        "mine": cmd_mine,
        "create-wallet": cmd_create_wallet,
        "create-seed": cmd_seed,
        "recover": cmd_recover,
        "export-wif": cmd_export_wif,
        "import-wif": cmd_import_wif,
        "wallet-info": cmd_wallet_info,
        "send": cmd_send,
        "balance": cmd_balance,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
