package com.globex.gbx.domain.model

data class Wallet(
    val address: String,
    val balance: Long,
    val publicKey: String
)

data class Transaction(
    val id: String,
    val sender: String,
    val recipient: String,
    val amount: Long,
    val fee: Long,
    val timestamp: Long,
    val txHash: String
)

data class Block(
    val index: Int,
    val hash: String,
    val prevHash: String,
    val timestamp: Long,
    val transactions: List<Transaction>,
    val nonce: Long,
    val target: String
)

data class Node(
    val id: String,
    val address: String,
    val port: Int,
    val isOnline: Boolean
)

data class MiningSession(
    val sessionId: String,
    val address: String,
    val hashrate: Double,
    val totalHashes: Long,
    val isRunning: Boolean
)

data class Validator(
    val address: String,
    val stakeAmount: Long,
    val uptime: Double,
    val isActive: Boolean
)

data class Stake(
    val id: String,
    val address: String,
    val amount: Long,
    val timestamp: Long
)

data class Fund(
    val name: String,
    val totalAllocated: Long,
    val remaining: Long
)

data class Checkpoint(
    val index: Int,
    val hash: String,
    val timestamp: Long
)
