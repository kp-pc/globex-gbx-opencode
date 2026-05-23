package com.globex.gbx.service

import android.content.Context
import androidx.hilt.work.HiltWorker
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.globex.gbx.data.local.dao.WalletDao
import dagger.assisted.Assisted
import dagger.assisted.AssistedInject

@HiltWorker
class BalanceUpdateWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted workerParams: WorkerParameters,
    private val walletDao: WalletDao
) : CoroutineWorker(context, workerParams) {

    override suspend fun doWork(): Result {
        return try {
            val wallets = walletDao.getAll().value
            if (wallets.isNotEmpty()) {
                Result.success()
            } else {
                Result.success()
            }
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
