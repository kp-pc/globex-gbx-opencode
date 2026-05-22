# Globex GBX

A lightweight cryptocurrency optimised for ARM devices (Raspberry Pi, mobile).

## Features

- **Proof-of-Work** (SHA-256) with 60s block time
- **Hybrid PoW + PoS** consensus with validator staking and slashing
- **Adjustable difficulty** — ARM-friendly
- **Block reward**: 50 GBX, halving every 500,000 blocks
- **Max supply**: 21,000,000 GBX
- **Transaction fees** with priority ordering
- **Merkle tree** for transaction integrity
- **ECDSA keys** (SECP256k1) with Base58Check addresses
- **SQLite** persistence — lightweight, zero-config
- **REST API** (FastAPI) with full node functionality
- **CPU miner** with configurable threads
- **Web dashboard** served by the node with real-time mining stats
- **Staking** with lockup, rewards, and slashing
- **Dev fund** with multi-sig and vesting

## Quick Start

### Install

```bash
pip install -r requirements.txt
```

### Start a Node

```bash
python cli.py start-node --port 8545
```

Open [http://127.0.0.1:8545/index.html](http://127.0.0.1:8545/index.html) for the dashboard.

### Create a Wallet

```bash
python cli.py create-wallet
```

### Send a Transaction

```bash
python cli.py send --from <ADDRESS> --to <RECIPIENT> --amount 100000000
```

### Start Mining

```bash
python cli.py mine --address <YOUR_ADDRESS> --threads 2
```

### Check Balance

```bash
python cli.py balance --address <ADDRESS>
```

## CLI Reference

| Command | Arguments | Description |
|---|---|---|
| `start-node` | `--host` `--port` | Start a Globex node |
| `create-wallet` | `--file` | Generate a new wallet |
| `send` | `--from` `--to` `--amount` `--fee` `--key` | Send GBX |
| `balance` | `--address` | Check address balance |
| `mine` | `--address` `--threads` `--node` | Start CPU mining |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Node status |
| GET | `/chain` | Full blockchain |
| GET | `/balance/{address}` | Address balance |
| POST | `/transactions/new` | Submit transaction |
| GET | `/mine?address=` | Mine a block |
| POST | `/blocks/submit` | Submit mined block |
| GET | `/blocks/latest` | Latest block |
| POST | `/nodes/register` | Register peer |
| GET | `/nodes/resolve` | Consensus resolution |
| GET | `/mempool` | Pending transactions |
| GET | `/peers` | Connected peers |
| GET | `/stats` | Network stats |
| GET | `/mining/stats` | Real-time mining statistics |

## Architecture

```
globex-gbx-opencode/
├── config.py      # Network parameters
├── utils.py       # Hashing, Base58, Merkle
├── core.py        # Block, Blockchain, PoW, mempool, SQLite
├── wallet.py      # ECDSA keys, signing, verification
├── node.py        # FastAPI REST server
├── miner.py       # CPU mining client
├── staking.py     # Hybrid PoW+PoS, validator staking
├── fund.py        # Dev fund, multi-sig, vesting
├── cli.py         # Command-line interface
├── gui/           # Web dashboard
└── requirements.txt
```

## License

MIT
