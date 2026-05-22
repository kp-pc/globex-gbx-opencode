package com.globex.gbx.network;

import com.globex.gbx.model.*;
import retrofit2.Call;
import retrofit2.http.*;

public interface GlobexApiService {

    @GET("/")
    Call<NodeStatus> getNodeStatus();

    @GET("/chain")
    Call<BlockchainResponse> getChain();

    @GET("/balance/{address}")
    Call<BalanceResponse> getBalance(@Path("address") String address);

    @POST("/transactions/new")
    Call<Void> newTransaction(@Body TransactionRequest request);

    @GET("/mine")
    Call<Block> mineBlock(@Query("address") String address);

    @POST("/blocks/submit")
    Call<Void> submitBlock(@Body BlockSubmitRequest request);

    @GET("/blocks/latest")
    Call<Block> getLatestBlock();

    @POST("/nodes/register")
    Call<Void> registerPeer(@Body PeerRequest request);

    @GET("/nodes/resolve")
    Call<Void> resolveConflicts();

    @GET("/mempool")
    Call<MempoolResponse> getMempool();

    @GET("/peers")
    Call<PeersResponse> getPeers();

    @GET("/stats")
    Call<StatsResponse> getStats();

    @GET("/mining/stats")
    Call<MiningStatsResponse> getMiningStats();
}
