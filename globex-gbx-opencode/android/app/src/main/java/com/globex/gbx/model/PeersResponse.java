package com.globex.gbx.model;

import java.util.List;

public class PeersResponse {
    public List<PeerInfo> peers;

    public static class PeerInfo {
        public String address;
        public int port;
    }
}
