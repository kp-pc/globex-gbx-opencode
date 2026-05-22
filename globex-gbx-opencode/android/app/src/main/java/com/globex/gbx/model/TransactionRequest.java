package com.globex.gbx.model;

public class TransactionRequest {
    public String sender;
    public String recipient;
    public long amount;
    public long fee;
    public long nonce;
    public String public_key;
    public String signature;
}
