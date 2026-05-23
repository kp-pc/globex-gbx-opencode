package com.globex.gbx.network

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

interface GlobexApiService {

    @GET("/")
    suspend fun getNodeInfo(): Response<NodeInfoResponse>

    @GET("/chain")
    suspend fun getChain(): Response<ChainResponse>

    @GET("/balance/{address}")
    suspend fun getBalance(@Path("address") address: String): Response<BalanceResponse>

    @GET("/mempool")
    suspend fun getMempool(): Response<MempoolResponse>

    @GET("/stats")
    suspend fun getStats(): Response<StatsResponse>

    @POST("/transactions/new")
    suspend fun sendTransaction(@Body request: SendTransactionRequest): Response<TransactionResponse>

    @POST("/wallet/create")
    suspend fun createWallet(): Response<WalletResponse>

    @POST("/wallet/import")
    suspend fun importWallet(@Body request: ImportWalletRequest): Response<WalletResponse>

    @GET("/block/{identifier}")
    suspend fun getBlock(@Path("identifier") identifier: String): Response<BlockResponse>

    @GET("/transaction/{tx_hash}")
    suspend fun getTransaction(@Path("tx_hash") txHash: String): Response<TransactionDetailResponse>

    @GET("/address/{address}")
    suspend fun getAddressInfo(@Path("address") address: String): Response<AddressInfoResponse>

    @GET("/staking/dashboard/{address}")
    suspend fun getStakingDashboard(@Path("address") address: String): Response<StakingDashboardResponse>

    @GET("/staking/validator/{address}/stats")
    suspend fun getValidatorStats(@Path("address") address: String): Response<ValidatorStatsResponse>

    @GET("/fund/report")
    suspend fun getFundReport(): Response<FundReportResponse>

    @POST("/fund/propose")
    suspend fun proposeRelease(@Body request: ProposeRequest): Response<ProposeResponse>

    @POST("/fund/approve")
    suspend fun approveRelease(@Body request: ApproveRequest): Response<ApproveResponse>

    @GET("/peers/status")
    suspend fun getPeersStatus(): Response<PeersStatusResponse>

    @POST("/mining/start")
    suspend fun startMining(@Body request: MiningStartRequest): Response<MiningStartResponse>

    @POST("/mining/stop")
    suspend fun stopMining(): Response<MiningStopResponse>

    @GET("/mining/status")
    suspend fun getMiningStatus(): Response<MiningStatusResponse>

    @GET("/mining/rewards/{address}")
    suspend fun getMiningRewards(@Path("address") address: String): Response<MiningRewardsResponse>
}

data class NodeInfoResponse(
    @SerializedName("node_id") val nodeId: String,
    val address: String,
    val port: Int,
    @SerializedName("is_online") val isOnline: Boolean,
    @SerializedName("chain_length") val chainLength: Int,
    val peers: Int,
    val version: String
)

data class ChainResponse(
    val chain: List<Map<String, Any>>?,
    val length: Int
)

data class BalanceResponse(
    val address: String,
    val balance: Long
)

data class MempoolResponse(
    val transactions: List<Map<String, Any>>,
    val count: Int
)

data class StatsResponse(
    @SerializedName("total_blocks") val totalBlocks: Int,
    @SerializedName("total_transactions") val totalTransactions: Int,
    @SerializedName("total_nodes") val totalNodes: Int,
    @SerializedName("total_staked") val totalStaked: Long,
    @SerializedName("network_hashrate") val networkHashrate: Double,
    @SerializedName("active_validators") val activeValidators: Int
)

data class SendTransactionRequest(
    val sender: String,
    val recipient: String,
    val amount: Long,
    val fee: Long
)

data class TransactionResponse(
    val message: String,
    val transaction: Map<String, Any>?
)

data class WalletResponse(
    val address: String,
    @SerializedName("private_key") val privateKey: String,
    @SerializedName("public_key") val publicKey: String
)

data class ImportWalletRequest(
    @SerializedName("private_key") val privateKey: String
)

data class BlockResponse(
    val block: Map<String, Any>?
)

data class TransactionDetailResponse(
    val transaction: Map<String, Any>?
)

data class AddressInfoResponse(
    val address: String,
    val balance: Long,
    val transactions: List<Map<String, Any>>
)

data class StakingDashboardResponse(
    @SerializedName("total_staked") val totalStaked: Long,
    @SerializedName("total_rewards") val totalRewards: Long,
    @SerializedName("active_stakes") val activeStakes: Int,
    val validators: List<Map<String, Any>>
)

data class ValidatorStatsResponse(
    val address: String,
    @SerializedName("total_staked") val totalStaked: Long,
    val uptime: Double,
    val commission: Double,
    @SerializedName("is_active") val isActive: Boolean,
    @SerializedName("blocks_proposed") val blocksProposed: Int
)

data class FundReportResponse(
    val name: String,
    @SerializedName("total_allocated") val totalAllocated: Long,
    val remaining: Long,
    val releases: List<Map<String, Any>>
)

data class ProposeRequest(
    val amount: Long,
    val recipient: String,
    val reason: String
)

data class ProposeResponse(
    val success: Boolean,
    val message: String,
    @SerializedName("proposal_id") val proposalId: String?
)

data class ApproveRequest(
    @SerializedName("proposal_id") val proposalId: String
)

data class ApproveResponse(
    val success: Boolean,
    val message: String
)

data class PeersStatusResponse(
    val peers: List<Map<String, Any>>,
    val count: Int
)

data class MiningStartRequest(
    val address: String
)

data class MiningStartResponse(
    val success: Boolean,
    val message: String,
    @SerializedName("session_id") val sessionId: String?
)

data class MiningStopResponse(
    val success: Boolean,
    val message: String
)

data class MiningStatusResponse(
    @SerializedName("session_id") val sessionId: String,
    val address: String,
    val hashrate: Double,
    @SerializedName("total_hashes") val totalHashes: Long,
    @SerializedName("is_running") val isRunning: Boolean
)

data class MiningRewardsResponse(
    @SerializedName("total_rewards") val totalRewards: Long,
    @SerializedName("blocks_mined") val blocksMined: Int
)
