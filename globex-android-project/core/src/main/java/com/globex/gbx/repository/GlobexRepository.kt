package com.globex.gbx.repository

import com.globex.gbx.network.AddressInfoResponse
import com.globex.gbx.network.ApproveRequest
import com.globex.gbx.network.ApproveResponse
import com.globex.gbx.network.BalanceResponse
import com.globex.gbx.network.BlockResponse
import com.globex.gbx.network.ChainResponse
import com.globex.gbx.network.FundReportResponse
import com.globex.gbx.network.GlobexApiService
import com.globex.gbx.network.ImportWalletRequest
import com.globex.gbx.network.MempoolResponse
import com.globex.gbx.network.MiningRewardsResponse
import com.globex.gbx.network.MiningStartRequest
import com.globex.gbx.network.MiningStartResponse
import com.globex.gbx.network.MiningStatusResponse
import com.globex.gbx.network.MiningStopResponse
import com.globex.gbx.network.NodeInfoResponse
import com.globex.gbx.network.PeersStatusResponse
import com.globex.gbx.network.ProposeRequest
import com.globex.gbx.network.ProposeResponse
import com.globex.gbx.network.SendTransactionRequest
import com.globex.gbx.network.StakingDashboardResponse
import com.globex.gbx.network.StatsResponse
import com.globex.gbx.network.TransactionDetailResponse
import com.globex.gbx.network.TransactionResponse
import com.globex.gbx.network.ValidatorStatsResponse
import com.globex.gbx.network.WalletResponse
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class GlobexRepository @Inject constructor(
    private val apiService: GlobexApiService
) {
    suspend fun getNodeInfo(): Result<NodeInfoResponse> = apiCall { apiService.getNodeInfo() }
    suspend fun getChain(): Result<ChainResponse> = apiCall { apiService.getChain() }
    suspend fun getBalance(address: String): Result<BalanceResponse> = apiCall { apiService.getBalance(address) }
    suspend fun getMempool(): Result<MempoolResponse> = apiCall { apiService.getMempool() }
    suspend fun getStats(): Result<StatsResponse> = apiCall { apiService.getStats() }
    suspend fun sendTransaction(sender: String, recipient: String, amount: Long, fee: Long): Result<TransactionResponse> =
        apiCall { apiService.sendTransaction(SendTransactionRequest(sender, recipient, amount, fee)) }
    suspend fun createWallet(): Result<WalletResponse> = apiCall { apiService.createWallet() }
    suspend fun importWallet(privateKey: String): Result<WalletResponse> =
        apiCall { apiService.importWallet(ImportWalletRequest(privateKey)) }
    suspend fun getBlock(identifier: String): Result<BlockResponse> = apiCall { apiService.getBlock(identifier) }
    suspend fun getTransaction(txHash: String): Result<TransactionDetailResponse> =
        apiCall { apiService.getTransaction(txHash) }
    suspend fun getAddressInfo(address: String): Result<AddressInfoResponse> =
        apiCall { apiService.getAddressInfo(address) }
    suspend fun getStakingDashboard(address: String): Result<StakingDashboardResponse> =
        apiCall { apiService.getStakingDashboard(address) }
    suspend fun getValidatorStats(address: String): Result<ValidatorStatsResponse> =
        apiCall { apiService.getValidatorStats(address) }
    suspend fun getFundReport(): Result<FundReportResponse> = apiCall { apiService.getFundReport() }
    suspend fun proposeRelease(amount: Long, recipient: String, reason: String): Result<ProposeResponse> =
        apiCall { apiService.proposeRelease(ProposeRequest(amount, recipient, reason)) }
    suspend fun approveRelease(proposalId: String): Result<ApproveResponse> =
        apiCall { apiService.approveRelease(ApproveRequest(proposalId)) }
    suspend fun getPeersStatus(): Result<PeersStatusResponse> = apiCall { apiService.getPeersStatus() }
    suspend fun startMining(address: String): Result<MiningStartResponse> =
        apiCall { apiService.startMining(MiningStartRequest(address)) }
    suspend fun stopMining(): Result<MiningStopResponse> = apiCall { apiService.stopMining() }
    suspend fun getMiningStatus(): Result<MiningStatusResponse> = apiCall { apiService.getMiningStatus() }
    suspend fun getMiningRewards(address: String): Result<MiningRewardsResponse> =
        apiCall { apiService.getMiningRewards(address) }

    private suspend fun <T> apiCall(call: suspend () -> retrofit2.Response<T>): Result<T> {
        return try {
            val response = call()
            if (response.isSuccessful) {
                response.body()?.let { Result.success(it) }
                    ?: Result.failure(Exception("Empty response body"))
            } else {
                Result.failure(Exception("API error: ${response.code()} ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
