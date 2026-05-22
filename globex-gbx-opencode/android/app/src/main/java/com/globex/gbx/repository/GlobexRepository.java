package com.globex.gbx.repository;

import com.globex.gbx.model.*;
import com.globex.gbx.network.GlobexApiService;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.util.concurrent.CompletableFuture;

public class GlobexRepository {

    private final GlobexApiService apiService;

    public GlobexRepository(String baseUrl) {
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(baseUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        this.apiService = retrofit.create(GlobexApiService.class);
    }

    public CompletableFuture<NodeStatus> getNodeStatus() {
        CompletableFuture<NodeStatus> future = new CompletableFuture<>();
        apiService.getNodeStatus().enqueue(new retrofit2.Callback<NodeStatus>() {
            @Override
            public void onResponse(retrofit2.Call<NodeStatus> call, retrofit2.Response<NodeStatus> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<NodeStatus> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<BlockchainResponse> getChain() {
        CompletableFuture<BlockchainResponse> future = new CompletableFuture<>();
        apiService.getChain().enqueue(new retrofit2.Callback<BlockchainResponse>() {
            @Override
            public void onResponse(retrofit2.Call<BlockchainResponse> call, retrofit2.Response<BlockchainResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<BlockchainResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<BalanceResponse> getBalance(String address) {
        CompletableFuture<BalanceResponse> future = new CompletableFuture<>();
        apiService.getBalance(address).enqueue(new retrofit2.Callback<BalanceResponse>() {
            @Override
            public void onResponse(retrofit2.Call<BalanceResponse> call, retrofit2.Response<BalanceResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<BalanceResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Void> newTransaction(TransactionRequest request) {
        CompletableFuture<Void> future = new CompletableFuture<>();
        apiService.newTransaction(request).enqueue(new retrofit2.Callback<Void>() {
            @Override
            public void onResponse(retrofit2.Call<Void> call, retrofit2.Response<Void> response) {
                if (response.isSuccessful()) {
                    future.complete(null);
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Void> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Block> mineBlock(String address) {
        CompletableFuture<Block> future = new CompletableFuture<>();
        apiService.mineBlock(address).enqueue(new retrofit2.Callback<Block>() {
            @Override
            public void onResponse(retrofit2.Call<Block> call, retrofit2.Response<Block> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Block> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Void> submitBlock(BlockSubmitRequest request) {
        CompletableFuture<Void> future = new CompletableFuture<>();
        apiService.submitBlock(request).enqueue(new retrofit2.Callback<Void>() {
            @Override
            public void onResponse(retrofit2.Call<Void> call, retrofit2.Response<Void> response) {
                if (response.isSuccessful()) {
                    future.complete(null);
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Void> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Block> getLatestBlock() {
        CompletableFuture<Block> future = new CompletableFuture<>();
        apiService.getLatestBlock().enqueue(new retrofit2.Callback<Block>() {
            @Override
            public void onResponse(retrofit2.Call<Block> call, retrofit2.Response<Block> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Block> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Void> registerPeer(PeerRequest request) {
        CompletableFuture<Void> future = new CompletableFuture<>();
        apiService.registerPeer(request).enqueue(new retrofit2.Callback<Void>() {
            @Override
            public void onResponse(retrofit2.Call<Void> call, retrofit2.Response<Void> response) {
                if (response.isSuccessful()) {
                    future.complete(null);
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Void> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<Void> resolveConflicts() {
        CompletableFuture<Void> future = new CompletableFuture<>();
        apiService.resolveConflicts().enqueue(new retrofit2.Callback<Void>() {
            @Override
            public void onResponse(retrofit2.Call<Void> call, retrofit2.Response<Void> response) {
                if (response.isSuccessful()) {
                    future.complete(null);
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<Void> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<MempoolResponse> getMempool() {
        CompletableFuture<MempoolResponse> future = new CompletableFuture<>();
        apiService.getMempool().enqueue(new retrofit2.Callback<MempoolResponse>() {
            @Override
            public void onResponse(retrofit2.Call<MempoolResponse> call, retrofit2.Response<MempoolResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<MempoolResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<PeersResponse> getPeers() {
        CompletableFuture<PeersResponse> future = new CompletableFuture<>();
        apiService.getPeers().enqueue(new retrofit2.Callback<PeersResponse>() {
            @Override
            public void onResponse(retrofit2.Call<PeersResponse> call, retrofit2.Response<PeersResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<PeersResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<StatsResponse> getStats() {
        CompletableFuture<StatsResponse> future = new CompletableFuture<>();
        apiService.getStats().enqueue(new retrofit2.Callback<StatsResponse>() {
            @Override
            public void onResponse(retrofit2.Call<StatsResponse> call, retrofit2.Response<StatsResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<StatsResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }

    public CompletableFuture<MiningStatsResponse> getMiningStats() {
        CompletableFuture<MiningStatsResponse> future = new CompletableFuture<>();
        apiService.getMiningStats().enqueue(new retrofit2.Callback<MiningStatsResponse>() {
            @Override
            public void onResponse(retrofit2.Call<MiningStatsResponse> call, retrofit2.Response<MiningStatsResponse> response) {
                if (response.isSuccessful()) {
                    future.complete(response.body());
                } else {
                    future.completeExceptionally(new Exception("Error: " + response.code()));
                }
            }

            @Override
            public void onFailure(retrofit2.Call<MiningStatsResponse> call, Throwable t) {
                future.completeExceptionally(t);
            }
        });
        return future;
    }
}
