package com.globex.gbx.core.di

import com.globex.gbx.network.GlobexApiService
import com.globex.gbx.repository.GlobexRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideGlobexRepository(apiService: GlobexApiService): GlobexRepository {
        return GlobexRepository(apiService)
    }
}
