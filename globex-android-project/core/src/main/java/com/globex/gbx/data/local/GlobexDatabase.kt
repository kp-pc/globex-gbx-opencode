package com.globex.gbx.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.globex.gbx.data.local.dao.WalletDao
import com.globex.gbx.data.local.entity.WalletEntity

@Database(entities = [WalletEntity::class], version = 1)
abstract class GlobexDatabase : RoomDatabase() {
    abstract fun walletDao(): WalletDao
}
