package com.globex.gbx

import android.app.Application
import androidx.hilt.work.HiltWorkerFactory
import androidx.work.Configuration
import androidx.work.Constraints
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.NetworkType
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.globex.gbx.service.BalanceUpdateWorker
import com.globex.gbx.service.MiningUpdateWorker
import com.globex.gbx.service.NodeSyncWorker
import dagger.hilt.android.HiltAndroidApp
import java.util.concurrent.TimeUnit
import javax.inject.Inject

@HiltAndroidApp
class GlobexApp : Application(), Configuration.Provider {

    @Inject
    lateinit var hiltWorkerFactory: HiltWorkerFactory

    override val workManagerConfiguration: Configuration
        get() = Configuration.Builder()
            .setWorkerFactory(hiltWorkerFactory)
            .build()

    override fun onCreate() {
        super.onCreate()
        scheduleWorkers()
    }

    private fun scheduleWorkers() {
        val syncConstraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()

        val nodeSyncRequest = PeriodicWorkRequestBuilder<NodeSyncWorker>(15, TimeUnit.MINUTES)
            .setConstraints(syncConstraints)
            .build()

        val balanceUpdateRequest = PeriodicWorkRequestBuilder<BalanceUpdateWorker>(5, TimeUnit.MINUTES)
            .setConstraints(syncConstraints)
            .build()

        val miningUpdateRequest = PeriodicWorkRequestBuilder<MiningUpdateWorker>(1, TimeUnit.MINUTES)
            .setConstraints(syncConstraints)
            .build()

        WorkManager.getInstance(this).apply {
            enqueueUniquePeriodicWork(
                "node_sync",
                ExistingPeriodicWorkPolicy.KEEP,
                nodeSyncRequest
            )
            enqueueUniquePeriodicWork(
                "balance_update",
                ExistingPeriodicWorkPolicy.KEEP,
                balanceUpdateRequest
            )
            enqueueUniquePeriodicWork(
                "mining_update",
                ExistingPeriodicWorkPolicy.KEEP,
                miningUpdateRequest
            )
        }
    }
}
