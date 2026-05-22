import argparse
import json
import os
import sys

import config
from wallet import Wallet, create_transaction
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


def cmd_create_wallet(args):
    wallet = Wallet()
    data = wallet.to_dict()
    out_path = args.file or WALLET_FILE
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wallet created: {wallet.address}")
    print(f"Private key saved to: {out_path}")
    print("KEEP YOUR PRIVATE KEY SAFE!")


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
        print(f"Insufficient balance. Have {balance/ config.GBX:.2f} GBX, need {total_cost/ config.GBX:.2f} GBX")
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

    p_send = sub.add_parser("send", help="Send GBX to an address")
    p_send.add_argument("--from", dest="from_addr", required=True)
    p_send.add_argument("--to", required=True)
    p_send.add_argument("--amount", type=int, required=True)
    p_send.add_argument("--fee", type=int, default=0)
    p_send.add_argument("--key")
    p_send.add_argument("--node")

    p_bal = sub.add_parser("balance", help="Check address balance")
    p_bal.add_argument("--address", required=True)
    p_bal.add_argument("--node")

    args = parser.parse_args()
    commands = {
        "start-node": cmd_start_node,
        "mine": cmd_mine,
        "create-wallet": cmd_create_wallet,
        "send": cmd_send,
        "balance": cmd_balance,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
