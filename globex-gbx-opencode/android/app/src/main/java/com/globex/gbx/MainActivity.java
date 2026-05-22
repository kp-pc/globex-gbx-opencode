package com.globex.gbx;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.globex.gbx.model.NodeStatus;
import com.globex.gbx.model.StatsResponse;
import com.globex.gbx.repository.GlobexRepository;

import java.util.concurrent.CompletableFuture;

public class MainActivity extends AppCompatActivity {

    private static final String PREFS_NAME = "globex_prefs";
    private static final String KEY_NODE_URL = "node_url";

    private TextView tvChainHeight;
    private TextView tvMempoolSize;
    private TextView tvPeersCount;
    private TextView tvLastBlockHash;
    private Button btnOpenWeb;

    private GlobexRepository repository;
    private String nodeUrl;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_native_dashboard);

        initViews();
        loadNodeUrl();
    }

    private void initViews() {
        tvChainHeight = findViewById(R.id.tvChainHeight);
        tvMempoolSize = findViewById(R.id.tvMempoolSize);
        tvPeersCount = findViewById(R.id.tvPeersCount);
        tvLastBlockHash = findViewById(R.id.tvLastBlockHash);
        btnOpenWeb = findViewById(R.id.btnOpenWeb);

        btnOpenWeb.setOnClickListener(v -> {
            Intent intent = new Intent(MainActivity.this, WebViewActivity.class);
            intent.putExtra("URL", nodeUrl);
            startActivity(intent);
        });
    }

    private void loadNodeUrl() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        nodeUrl = prefs.getString(KEY_NODE_URL, null);

        if (nodeUrl == null || !nodeUrl.endsWith("/")) {
            nodeUrl = (nodeUrl == null ? "http://10.0.2.2:8545/" : nodeUrl) + "/";
        }

        repository = new GlobexRepository(nodeUrl);
        refreshData();
    }

    private void refreshData() {
        // Fetch Node Status
        repository.getNodeStatus().thenAccept(status -> {
            runOnUiThread(() -> {
                tvChainHeight.setText("Chain Height: " + status.chain_length);
                tvMempoolSize.setText("Mempool: " + status.mempool_size);
                tvPeersCount.setText("Peers: " + status.peers_count);
            });
        }).exceptionally(ex -> {
            runOnUiThread(() -> Toast.makeText(MainActivity.this, "Connection Error", Toast.LENGTH_SHORT).show());
            return null;
        });

        // Fetch Stats for Last Block
        repository.getStats().thenAccept(stats -> {
            runOnUiThread(() -> {
                if (stats.last_block_hash != null) {
                    tvLastBlockHash.setText("Hash: " + stats.last_block_hash.substring(0, 16) + "...");
                }
            });
        }).exceptionally(ex -> null);
    }
}
