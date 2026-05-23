# Globex GBX

A lightweight cryptocurrency optimised for ARM devices (Raspberry Pi, mobile) with a full Android companion app.

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
- **Staking** with lockup, rewards, and slashing events
- **Dev fund** with 5% block-reward allocation, multi-sig vesting, and release proposals
- **Charts & analytics** — balance history and validator analytics
- **Android app** (Jetpack Compose, Hilt, Room, Navigation Compose, WorkManager)

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
| GET | `/block/{identifier}` | Block by hash or height |
| GET | `/transaction/{tx_hash}` | Transaction details |
| GET | `/address/{address}` | Address info with transactions |
| POST | `/wallet/create` | Generate new wallet |
| POST | `/wallet/import` | Import wallet by private key |
| POST | `/mining/start` | Start CPU mining session |
| POST | `/mining/stop` | Stop mining session |
| GET | `/mining/status` | Mining session status |
| GET | `/mining/rewards/{address}` | Mining rewards summary |
| POST | `/nodes/register` | Register peer |
| GET | `/nodes/resolve` | Consensus resolution |
| GET | `/peers/status` | Peer list with latency/height/sync status |
| GET | `/mempool` | Pending transactions |
| GET | `/stats` | Network stats |
| GET | `/staking/dashboard/{address}` | Staking dashboard (stake/lock/rewards) |
| GET | `/staking/validator/{address}/stats` | Validator stats (uptime/blocks/penalties) |
| GET | `/fund/report` | Fund treasury dashboard |
| POST | `/fund/propose` | Propose a fund release |
| POST | `/fund/approve` | Approve a pending release |
| GET | `/fund/transactions` | Fund transaction history |
| GET | `/charts/balance-history` | Balance history for charts |
| GET | `/charts/validator-analytics` | Validator analytics with history |

## Architecture

```
globex-gbx-opencode/           # Python backend
├── config.py                  # Network parameters
├── utils.py                   # Hashing, Base58, Merkle
├── core.py                    # Block, Blockchain, PoW, mempool, SQLite
├── wallet.py                  # ECDSA keys, signing, verification
├── node.py                    # FastAPI REST server
├── miner.py                   # CPU mining client
├── staking.py                 # Hybrid PoW+PoS, validator staking
├── fund.py                    # Dev fund, multi-sig, vesting
├── cli.py                     # Command-line interface
├── gui/                       # Web dashboard (10 screens)
└── requirements.txt

globex-android-project/        # Android companion app (13 modules)
├── app/                       # Main app module (NavGraph, MainActivity)
├── core/                      # Networking, database, repository
├── feature_wallet/            # Wallet UI (balance, send, receive)
├── feature_mining/            # Mining UI with foreground service
├── feature_explorer/          # Blockchain explorer UI
├── feature_nodes/             # Peer management UI
├── feature_staking/           # Staking dashboard UI
├── feature_fund/              # Fund treasury UI
├── feature_settings/          # App settings UI
└── build.gradle.kts           # Hilt, Compose, Room config
```

## Android App

The Android app is built with **Modern Android Development** principles:

- **Language**: Kotlin 1.9+
- **UI**: Jetpack Compose & Material 3
- **DI**: Hilt
- **Networking**: Retrofit 2 + OkHttp
- **Persistence**: Room (SQLite)
- **Security**: Android Keystore (AES/GCM)
- **Navigation**: Navigation Compose (single-activity)
- **Background Services**: WorkManager for mining, foreground service

### Screens

| Screen | Description |
|---|---|
| Home | Node status, balance, quick actions |
| Wallet | Balance, send, receive, import/export |
| Mine | Start/stop mining, hashrate, rewards |
| Explorer | Block, transaction, and address search |
| Nodes | Peer monitor with latency tracking |
| Stake | Staking dashboard, validator stats, slashing history |
| Fund | Treasury dashboard, propose/approve releases |
| Validator | Detailed validator analytics |
| Settings | Node connection, theme, security |

## License

MIT
