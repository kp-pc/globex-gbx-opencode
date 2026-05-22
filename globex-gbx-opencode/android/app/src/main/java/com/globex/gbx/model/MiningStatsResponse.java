package com.globex.gbx.model;

public class MiningStatsResponse {
    public boolean is_mining;
    public double hash_rate;
    public long current_nonce;
    public int last_block_height;
    public String last_block_hash;
    public long total_hashes;
}
