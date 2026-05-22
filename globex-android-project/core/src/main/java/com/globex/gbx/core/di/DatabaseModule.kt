package com.globex.gbx.core.di

import android.content.Context
import androidx.room.Room
import com.globex.gbx.data.local.GlobexDatabase
import com.globex.gbx.data.local.dao.WalletDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideGlobexDatabase(@ApplicationContext context: Context): GlobexDatabase {
        return Room.databaseBuilder(
            context,
            GlobexDatabase::class.java,
            "globex_database"
        ).build()
    }

    @Provides
    fun provideWalletDao(database: GlobexDatabase): WalletDao {
        return database.walletDao()
    }
}
