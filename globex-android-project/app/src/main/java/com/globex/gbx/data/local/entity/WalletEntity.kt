package com.globex.gbx.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "wallets")
data class WalletEntity(
    @PrimaryKey val address: String,
    val balance: Long,
    val publicKey: String
)
