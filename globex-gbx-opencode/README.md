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
- **Android SDK** (Retrofit & Repositories) for easy integration
- **Security** (Android Keystore) for hardware-backed local data protection
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

## Android Integration

The project includes a pre-built Android SDK using Retrofit for easy integration with your mobile applications.

### Dependencies

Add the following to your `build.gradle` file:

```gradle
dependencies {
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
}
```

### Usage

Initialize the `GlobexRepository` with your node's base URL:

```java
GlobexRepository repository = new GlobexRepository("http://your-node-url:8545/");

// Fetch node status
repository.getNodeStatus().thenAccept(status -> {
    System.out.println("Chain length: " + status.chain_length);
}).exceptionally(ex -> {
    ex.printStackTrace();
    return null;
});
```

## Security

Sensitive data (such as wallet private keys or API tokens) can be securely stored on-device using the `SecurityManager` utility. This implementation uses the **Android Keystore**, ensuring that encryption keys are stored in a hardware-backed environment (TEE/SE), making them virtually impossible to extract even if the device is compromised.

### Usage

```java
import com.globex.gbx.util.SecurityManager;

// Encrypt data
String encrypted = SecurityManager.encrypt("my_private_key");

// Decrypt data
String decrypted = SecurityManager.decrypt(encrypted);
```

## 🛠 Technical Architecture

Globex Android is built using **Modern Android Development (MAD)** principles:

### 🏗 Clean Architecture Layers
- **Domain Layer**: Pure Kotlin. Contains business entities (`Wallet`, `Block`), Use Cases, and Repository interfaces.
- **Data Layer**: Implementation of repositories, Retrofit API services, and DTOs.
- **Presentation Layer**: Jetpack Compose UI with MVVM (ViewModel $\rightarrow$ StateFlow $\rightarrow$ UI).

### ⚙️ Technology Stack
- **Language**: Kotlin (1.9+)
- **UI Framework**: Jetpack Compose & Material 3
- **Dependency Injection**: Hilt
- **Networking**: Retrofit 2 & OkHttp (with Gzip and Logging)
- **Asynchrony**: Kotlin Coroutines & Flow
- **Local Security**: Android Keystore System (AES/GCM)
- **Navigation**: Compose Navigation (Single Activity Architecture)

### 🔌 API Integration
The app communicates with the Globex Node via a REST API:
- **Chain Management**: `/chain`, `/blocks/latest`
- **Mining**: `/mine` (with real-time hashrate tracking)
- **Wallets**: `/balance/{address}`, `/transactions/new`
- **Network**: `/nodes/register`, `/nodes/resolve`

### 📱 Android SDK for Developers
Developers can integrate Globex functionality into their own apps using the `GlobexRepository`:

```kotlin
val repo = GlobexRepository(nodeUrl)
repo.getChain().collect { chain -> 
    // Handle blockchain data
}
```

## License

MIT
