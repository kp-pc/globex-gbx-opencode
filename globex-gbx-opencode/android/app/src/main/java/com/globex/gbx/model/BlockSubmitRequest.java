package com.globex.gbx.model;

import java.util.List;

public class BlockSubmitRequest {
    public int index;
    public long timestamp;
    public List<Transaction> transactions;
    public String prev_hash;
    public long target;
    public long nonce;
    public String merkle_root;
    public String hash;
}
