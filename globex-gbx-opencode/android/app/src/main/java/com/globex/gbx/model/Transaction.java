package com.globex.gbx.model;

public class Transaction {
    public String sender;
    public String recipient;
    public long amount;
    public long fee;
    public long timestamp;
    public long nonce;
    public String signature;
    public String public_key;
    public String tx_hash;
}
