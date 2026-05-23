package com.globex.gbx.navigation

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalance
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.globex.gbx.feature_explorer.presentation.ExplorerViewModel
import com.globex.gbx.feature_fund.presentation.FundViewModel
import com.globex.gbx.feature_mining.presentation.MiningViewModel
import com.globex.gbx.feature_nodes.presentation.NodesViewModel
import com.globex.gbx.feature_settings.presentation.SettingsViewModel
import com.globex.gbx.feature_staking.presentation.StakingViewModel
import com.globex.gbx.feature_validator.presentation.ValidatorViewModel
import com.globex.gbx.feature_wallet.presentation.WalletViewModel
import com.globex.gbx.network.AddressInfoResponse
import com.globex.gbx.network.BlockResponse
import com.globex.gbx.network.ChainResponse
import com.globex.gbx.network.FundReportResponse
import com.globex.gbx.network.MiningStatusResponse
import com.globex.gbx.network.PeersStatusResponse
import com.globex.gbx.network.StakingDashboardResponse
import com.globex.gbx.network.TransactionDetailResponse
import com.globex.gbx.network.ValidatorStatsResponse
import com.globex.gbx.presentation.ui.UiState

private val DarkBg = Color(0xFF0A0E17)
private val DarkCard = Color(0xFF111827)
private val Accent = Color(0xFF00C853)
private val TextPri = Color(0xFFF0F4FF)
private val TextSec = Color(0xFF6B7280)
private val BorderCol = Color(0xFF1F2937)
private val DividerCol = Color(0xFF1A1F2E)
private val Red = Color(0xFFEF4444)
private val Orange = Color(0xFFF59E0B)
private val Blue = Color(0xFF64B5F6)

@Composable
fun NavGraph(navController: NavHostController, modifier: Modifier = Modifier) {
    NavHost(navController = navController, startDestination = Screen.Home.route, modifier = modifier) {
        composable(Screen.Home.route) { HomeScreen() }
        composable(Screen.Wallet.route) { WalletScreen() }
        composable(Screen.Mine.route) { MineScreen() }
        composable(Screen.Explorer.route) { ExplorerScreen() }
        composable(Screen.Nodes.route) { NodesScreen() }
        composable(Screen.Stake.route) { StakeScreen() }
        composable(Screen.Settings.route) { SettingsScreen() }
        composable(Screen.Fund.route) { FundScreen() }
        composable(Screen.Validator.route) { ValidatorScreen() }
    }
}

@Composable
private fun HomeScreen() {
    val scroll = rememberScrollState()
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text("Globex ", color = Accent, fontSize = 22.sp, fontWeight = FontWeight.Bold)
            Text("GBX", color = TextSec, fontSize = 22.sp, fontWeight = FontWeight.Light)
            Spacer(Modifier.weight(1f))
            Box(Modifier.size(8.dp).clip(CircleShape).background(Accent))
            Spacer(Modifier.width(4.dp))
            Text("Connected", color = Accent, fontSize = 12.sp)
        }
        Spacer(Modifier.height(16.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatCard("Block Height", "35", Modifier.weight(1f))
            StatCard("Difficulty", "1.0", Modifier.weight(1f))
            StatCard("Hash Rate", "Idle", Modifier.weight(1f))
        }
        Spacer(Modifier.height(8.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatCard("Peers", "3", Modifier.weight(1f))
            StatCard("Mempool", "0", Modifier.weight(1f))
            StatCard("Supply", "1,750.00", Modifier.weight(1f))
        }
        Spacer(Modifier.height(12.dp))
        Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) {
            Column(Modifier.padding(16.dp)) {
                Text("Last Block", color = TextSec, fontSize = 13.sp)
                Spacer(Modifier.height(4.dp))
                Text("798f12fa5be9...", color = TextPri, fontSize = 12.sp, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace)
                Spacer(Modifier.height(4.dp))
                Text("2024-06-01 12:34:56", color = TextSec, fontSize = 12.sp)
            }
        }
        Spacer(Modifier.height(12.dp))
        Button(onClick = {}, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.fillMaxWidth()) {
            Text("Refresh", color = Color.Black)
        }
    }
}

@Composable
private fun StatCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier = modifier, colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(12.dp)) {
            Text(label, color = TextSec, fontSize = 11.sp)
            Spacer(Modifier.height(4.dp))
            Text(value, color = TextPri, fontSize = 18.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun WalletScreen() {
    val vm: WalletViewModel = hiltViewModel()
    val uiState by vm.uiState.collectAsState()
    var wif by remember { mutableStateOf("") }
    var seed by remember { mutableStateOf("") }
    var passphrase by remember { mutableStateOf("") }
    val scroll = rememberScrollState()
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        SectionCard("Create Wallet") {
            Text("Generate a new Globex GBX wallet with ECDSA SECP256k1 key pair.", color = TextSec, fontSize = 13.sp)
            Spacer(Modifier.height(8.dp))
            Button(onClick = { vm.createWallet() }, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.fillMaxWidth()) {
                Text("Create Wallet", color = Color.Black)
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Import Wallet") {
            OutlinedTextField(value = wif, onValueChange = { wif = it }, label = { Text("WIF Private Key") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Button(onClick = { vm.importWallet(wif) }, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.fillMaxWidth()) {
                Text("Import from WIF", color = Color.Black)
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Import from Seed") {
            OutlinedTextField(value = seed, onValueChange = { seed = it }, label = { Text("Seed Phrase (12-24 words)") }, modifier = Modifier.fillMaxWidth(), minLines = 2, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = passphrase, onValueChange = { passphrase = it }, label = { Text("Passphrase (optional)") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Button(onClick = { vm.importSeed(seed, passphrase) }, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.fillMaxWidth()) {
                Text("Import from Seed", color = Color.Black)
            }
        }
        when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp), fontSize = 13.sp) }
            is UiState.Success -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) {
                Column(Modifier.padding(16.dp)) {
                    Text("Wallet", color = Accent, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                    Spacer(Modifier.height(8.dp))
                    Text("Address:", color = TextSec, fontSize = 11.sp)
                    Text(com.globex.gbx.util.shortAddress(s.data.toString()), color = TextPri, fontSize = 12.sp, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace)
                }
            }
        }
    }
}

@Composable
private fun MineScreen() {
    val vm: MiningViewModel = hiltViewModel()
    val uiState by vm.uiState.collectAsState()
    var address by remember { mutableStateOf("") }
    var threads by remember { mutableIntStateOf(1) }
    val scroll = rememberScrollState()
    LaunchedEffect(Unit) { vm.getStatus() }
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        SectionCard("Mining Control") {
            OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Reward Address") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = threads.toString(), onValueChange = { threads = it.toIntOrNull() ?: 1 }, label = { Text("Threads (1-16)") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { vm.startMining(address, threads) }, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.weight(1f)) { Text("Start Mining", color = Color.Black) }
                OutlinedButton(onClick = { vm.stopMining() }, colors = OutlinedButtonDefaults(outlinedContentColor = Red), border = androidx.compose.foundation.BorderStroke(1.dp, Red), modifier = Modifier.weight(1f)) { Text("Stop", color = Red) }
            }
        }
        Spacer(Modifier.height(12.dp))
        when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp)) }
            is UiState.Success -> {
                val data = s.data
                if (data is MiningStatusResponse) {
                    SectionCard("Mining Status") {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Status", if (data.running) "Running" else "Idle", Modifier.weight(1f))
                            MetricCard("Hash Rate", "${data.hashRate} H/s", Modifier.weight(1f))
                        }
                        Spacer(Modifier.height(8.dp))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Total Hashes", data.totalHashes.toString(), Modifier.weight(1f))
                            MetricCard("Block", "#${data.blockHeight}", Modifier.weight(1f))
                        }
                    }
                    Spacer(Modifier.height(12.dp))
                    SectionCard("Rewards") {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            MetricCard("Blocks Mined", "0", Modifier.weight(1f))
                            MetricCard("Total Rewards", "0 GBX", Modifier.weight(1f))
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun OutlinedButtonDefaults(outlinedContentColor: Color) = ButtonDefaults.outlinedButtonColors(contentColor = outlinedContentColor)

@Composable
private fun ExplorerScreen() {
    val vm: ExplorerViewModel = hiltViewModel()
    val uiState by vm.uiState.collectAsState()
    var query by remember { mutableStateOf("") }
    var selectedTab by remember { mutableIntStateOf(0) }
    val tabs = listOf("Block", "Hash", "Address", "Tx")
    val scroll = rememberScrollState()
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            tabs.forEachIndexed { i, t ->
                FilterChip(selected = selectedTab == i, onClick = { selectedTab = i }, label = { Text(t, fontSize = 12.sp) }, colors = FilterChipDefaults.filterChipColors(selectedContainerColor = Accent, selectedLabelColor = Color.Black))
            }
        }
        Spacer(Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(value = query, onValueChange = { query = it }, label = { Text("Search...") }, modifier = Modifier.weight(1f), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri, fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace, fontSize = 13.sp))
            Button(onClick = {
                when (selectedTab) { 0 -> vm.searchByBlock(query); 1 -> vm.searchByHash(query); 2 -> vm.searchByAddress(query); 3 -> vm.searchByTransaction(query) }
            }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Go", color = Color.Black) }
        }
        Spacer(Modifier.height(12.dp))
        when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp)) }
            is UiState.Success -> {
                val data = s.data
                when (data) {
                    is BlockResponse -> {
                        SectionCard("Block Details") {
                            DetailRow("Height", "#${data.index}")
                            DetailRow("Hash", data.hash)
                            DetailRow("Prev Hash", data.prevHash)
                            DetailRow("Timestamp", java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss", java.util.Locale.US).format(java.util.Date(data.timestamp * 1000)))
                            DetailRow("Nonce", data.nonce.toString())
                            DetailRow("Difficulty", "%.4f".format(data.difficulty))
                            DetailRow("Merkle Root", data.merkleRoot)
                            DetailRow("Confirmations", data.confirmations.toString())
                            DetailRow("Transactions", "${data.transactions.size}")
                        }
                    }
                    is AddressInfoResponse -> {
                        SectionCard("Address Details") {
                            DetailRow("Address", data.address)
                            DetailRow("Balance", "%.4f GBX".format(data.formattedBalance))
                            DetailRow("Transactions", data.transactionCount.toString())
                        }
                    }
                    is TransactionDetailResponse -> {
                        SectionCard("Transaction Details") {
                            DetailRow("Hash", data.txHash)
                            DetailRow("From", data.sender)
                            DetailRow("To", data.recipient)
                            DetailRow("Amount", "%.8f GBX".format(data.amount))
                            DetailRow("Fee", "%.8f GBX".format(data.fee))
                            DetailRow("Block", if (data.blockIndex >= 0) "#${data.blockIndex}" else "Pending")
                            DetailRow("Status", data.status)
                        }
                    }
                    else -> {
                        Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) {
                            Text("Result found", color = Accent, modifier = Modifier.padding(16.dp))
                        }
                    }
                }
            }
        }
    }
}

private enum class NodeAction { NONE, ADD_NODE, RESOLVE_CHAIN, REFRESH_PEERS }

@Composable
private fun NodesScreen() {
    val viewModel: NodesViewModel = hiltViewModel()
    val uiState by viewModel.uiState.collectAsState()
    var address by remember { mutableStateOf("127.0.0.1") }
    var port by remember { mutableStateOf("8545") }
    var lastAction by remember { mutableStateOf(NodeAction.REFRESH_PEERS) }
    var cachedPeers by remember { mutableStateOf<PeersStatusResponse?>(null) }
    LaunchedEffect(Unit) { lastAction = NodeAction.REFRESH_PEERS; viewModel.refreshPeers() }
    when (val state = uiState) { is UiState.Success -> { if (state.data is PeersStatusResponse) cachedPeers = state.data }; else -> {} }
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(rememberScrollState()).padding(16.dp)) {
        SectionCard("Add Node") {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Address") }, modifier = Modifier.weight(1f), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
                OutlinedTextField(value = port, onValueChange = { port = it }, label = { Text("Port") }, modifier = Modifier.width(100.dp), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            }
            Spacer(Modifier.height(8.dp))
            Button(onClick = { lastAction = NodeAction.ADD_NODE; viewModel.addNode(address, port.toIntOrNull() ?: 8545) }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Add Node", color = Color.Black) }
            if (lastAction == NodeAction.ADD_NODE) when (val s = uiState) { is UiState.Loading -> CircularProgressIndicator(color = Accent, modifier = Modifier.size(16.dp), strokeWidth = 2.dp); is UiState.Success -> { if (s.data is String) Text(s.data, color = Accent, fontSize = 13.sp) }; is UiState.Error -> Text(s.message, color = Red, fontSize = 13.sp); else -> {} }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Chain Resolution") {
            Text("Resolve chain conflicts by comparing with connected peers.", color = TextSec, fontSize = 13.sp)
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { lastAction = NodeAction.RESOLVE_CHAIN; viewModel.resolveChain() }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Resolve Chain", color = Color.Black) }
                Button(onClick = { lastAction = NodeAction.REFRESH_PEERS; viewModel.refreshPeers() }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Refresh", color = Color.Black) }
            }
            if (lastAction == NodeAction.RESOLVE_CHAIN) when (val s = uiState) { is UiState.Loading -> CircularProgressIndicator(color = Accent, modifier = Modifier.size(16.dp), strokeWidth = 2.dp); is UiState.Success -> { val d = s.data; if (d is ChainResponse) Text("Chain resolved: ${d.length} blocks", color = Accent, fontSize = 13.sp) else if (d is String) Text(d, color = Accent, fontSize = 13.sp) }; is UiState.Error -> Text(s.message, color = Red, fontSize = 13.sp); else -> {} }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Connected Peers") {
            Row(Modifier.fillMaxWidth().background(DarkBg, RoundedCornerShape(4.dp)).padding(horizontal = 8.dp, vertical = 6.dp)) {
                TableCell("Address", Modifier.weight(2f)); TableCell("Port", Modifier.weight(1f)); TableCell("Latency", Modifier.weight(1f)); TableCell("Height", Modifier.weight(1f)); TableCell("Sync", Modifier.weight(1.2f)); TableCell("Status", Modifier.weight(1f)); Box(Modifier.width(64.dp))
            }
            HorizontalDivider(color = DividerCol)
            val peers = cachedPeers
            if (peers != null) {
                peers.peers.forEachIndexed { i, peer ->
                    val pa = peer["address"] as? String ?: ""; val pp = (peer["port"] as? Number)?.toInt() ?: 0; val lat = (peer["latency"] as? Number)?.toDouble() ?: 0.0; val h = (peer["height"] as? Number)?.toInt() ?: 0; val sync = peer["is_synced"] as? Boolean ?: false; val online = peer["reachable"] as? Boolean ?: false; val nid = peer["node_id"] as? String ?: pa
                    Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                        Text(pa, color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(2f), maxLines = 1, overflow = TextOverflow.Ellipsis)
                        Text("$pp", color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f))
                        Text(if (lat < 1000) "${lat.toInt()}ms" else "%.1fs".format(lat / 1000), color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f))
                        Text("$h", color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f))
                        SyncBadge(sync, Modifier.weight(1.2f)); StatusDot(online, Modifier.weight(1f))
                        Button(onClick = { viewModel.deleteNode(nid) }, colors = ButtonDefaults.buttonColors(Red), modifier = Modifier.height(28.dp), contentPadding = ButtonDefaults.TextButtonContentPadding) { Text("Remove", fontSize = 11.sp, color = Color.White) }
                    }
                    if (i < peers.peers.size - 1) HorizontalDivider(color = DividerCol.copy(alpha = 0.5f), modifier = Modifier.padding(horizontal = 8.dp))
                }
            } else when (val s = uiState) { is UiState.Loading -> CircularProgressIndicator(color = Accent, modifier = Modifier.size(20.dp), strokeWidth = 2.dp); is UiState.Error -> Text(s.message, color = Red, fontSize = 13.sp); else -> Text("No peers data", color = TextSec, fontSize = 13.sp) }
        }
    }
}

@Composable
private fun StakeScreen() {
    val viewModel: StakingViewModel = hiltViewModel()
    val uiState by viewModel.uiState.collectAsState()
    var address by remember { mutableStateOf("") }
    var actionTriggered by remember { mutableStateOf(false) }
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(rememberScrollState()).padding(16.dp)) {
        SectionCard("Staking Dashboard") {
            OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Validator Address") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { actionTriggered = true; viewModel.loadDashboard(address) }, colors = ButtonDefaults.buttonColors(Accent)) { Text("View Dashboard", color = Color.Black) }
                OutlinedButton(onClick = { actionTriggered = true; viewModel.loadStats(address) }, colors = ButtonDefaults.outlinedButtonColors(contentColor = Accent), border = androidx.compose.foundation.BorderStroke(1.dp, Accent)) { Text("Validator Stats", color = Accent) }
            }
        }
        if (actionTriggered) when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(16.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Success -> {
                val data = s.data
                if (data is StakingDashboardResponse) {
                    Spacer(Modifier.height(12.dp))
                    SectionCard("Dashboard Results") {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MetricCard("Stake", "%.2f GBX".format(data.stakeFormatted), Modifier.weight(1f)); MetricCard("Lock Period", "${data.lockRemainingDays}d", Modifier.weight(1f)) }
                        Spacer(Modifier.height(8.dp))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MetricCard("Est. Daily", "%.6f GBX".format(data.estimatedDailyFormatted), Modifier.weight(1f)); MetricCard("Est. Annual", "%.4f GBX".format(data.estimatedAnnualFormatted), Modifier.weight(1f)); MetricCard("APY", "${data.apyPct}%", Modifier.weight(1f)) }
                    }
                } else if (data is ValidatorStatsResponse) {
                    Spacer(Modifier.height(12.dp))
                    SectionCard("Validator Dashboard") {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MetricCard("Status", if (data.isActive) "Active" else "Slashed", Modifier.weight(1f)); MetricCard("Uptime", "%.1f%%".format(data.uptime), Modifier.weight(1f)); MetricCard("Stake", "%.2f GBX".format(data.totalStaked), Modifier.weight(1f)) }
                        Spacer(Modifier.height(8.dp))
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) { MetricCard("Blocks", data.blocksProposed.toString(), Modifier.weight(1f)); MetricCard("Missed", "0", Modifier.weight(1f)); MetricCard("Penalties", "None", Modifier.weight(1f)) }
                    }
                }
            }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp), fontSize = 13.sp) }
        }
        Spacer(Modifier.height(16.dp))
        SectionCard("Finality Checkpoints") {
            Text("Checkpoints created every 1000 blocks.", color = TextSec, fontSize = 13.sp)
            Spacer(Modifier.height(8.dp))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.Bottom) {
                listOf(104520 to 12, 104521 to 12, 104522 to 11, 104523 to 11, 104524 to 10).forEach { (h, v) ->
                    Column(Modifier.weight(1f), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("$v", color = Accent, fontSize = 10.sp)
                        Box(Modifier.fillMaxWidth().height(20.dp).clip(RoundedCornerShape(4.dp)).background(Accent))
                        Spacer(Modifier.height(2.dp)); Text("#$h", color = TextSec, fontSize = 9.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun SettingsScreen() {
    var screenshotEnabled by remember { mutableStateOf(false) }
    var pin by remember { mutableStateOf("") }
    var pinConfirm by remember { mutableStateOf("") }
    var pinEnabled by remember { mutableStateOf(false) }
    var biometricEnabled by remember { mutableStateOf(false) }
    val scroll = rememberScrollState()
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        SectionCard("Screenshot Protection") {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column { Text("Block Screenshots", color = TextPri, fontSize = 14.sp); Text("Prevent screenshots on wallet screens", color = TextSec, fontSize = 11.sp) }
                Switch(checked = screenshotEnabled, onCheckedChange = { screenshotEnabled = it }, colors = SwitchDefaults.colors(checkedTrackColor = Accent, checkedThumbColor = Color.White))
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("PIN Protection") {
            OutlinedTextField(value = pin, onValueChange = { pin = it }, label = { Text("Set PIN (4-12 digits)") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = pinConfirm, onValueChange = { pinConfirm = it }, label = { Text("Confirm PIN") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { if (pin.length >= 4 && pin == pinConfirm) pinEnabled = true }, colors = ButtonDefaults.buttonColors(Accent), modifier = Modifier.weight(1f)) { Text(if (pinEnabled) "Update PIN" else "Enable PIN", color = Color.Black) }
                if (pinEnabled) OutlinedButton(onClick = { pinEnabled = false; pin = ""; pinConfirm = "" }, colors = ButtonDefaults.outlinedButtonColors(contentColor = Red), border = androidx.compose.foundation.BorderStroke(1.dp, Red), modifier = Modifier.weight(1f)) { Text("Disable", color = Red) }
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Biometric Authentication") {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column { Text("Fingerprint / Face Unlock", color = TextPri, fontSize = 14.sp); Text("Use biometric sensor for wallet access", color = TextSec, fontSize = 11.sp) }
                Switch(checked = biometricEnabled, onCheckedChange = { biometricEnabled = it }, colors = SwitchDefaults.colors(checkedTrackColor = Accent, checkedThumbColor = Color.White))
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Secure Key Storage") {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column { Text("Android Keystore", color = TextPri, fontSize = 14.sp); Text("Keys encrypted with device hardware-backed storage", color = TextSec, fontSize = 11.sp) }
                Box(Modifier.clip(RoundedCornerShape(4.dp)).background(Accent.copy(alpha = 0.2f)).padding(horizontal = 8.dp, vertical = 4.dp)) { Text("Available", color = Accent, fontSize = 11.sp, fontWeight = FontWeight.Bold) }
            }
            Spacer(Modifier.height(8.dp))
            Text("Keys are encrypted using AES-256 GCM with a key stored in the Android Keystore, backed by the device's trusted execution environment (TEE).", color = TextSec, fontSize = 12.sp)
        }
    }
}

@Composable
private fun FundScreen() {
    val vm: FundViewModel = hiltViewModel()
    val uiState by vm.uiState.collectAsState()
    var recipient by remember { mutableStateOf("") }
    var amount by remember { mutableStateOf("") }
    var releaseId by remember { mutableStateOf("") }
    var signer by remember { mutableStateOf("") }
    val scroll = rememberScrollState()
    LaunchedEffect(Unit) { vm.loadReport() }
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp)) }
            is UiState.Success -> {
                val data = s.data
                if (data is FundReportResponse) {
                    SectionCard("Fund Dashboard") {
                        DetailRow("Fund Address", data.address)
                        DetailRow("Treasury Balance", "%.4f GBX".format(data.available.toDouble() / 100000000))
                        DetailRow("Vested", "%.4f GBX".format(data.vested.toDouble() / 100000000))
                        DetailRow("Locked", "%.4f GBX".format(data.locked.toDouble() / 100000000))
                        DetailRow("Total Accumulated", "%.4f GBX".format(data.totalAccumulated.toDouble() / 100000000))
                        DetailRow("Released", "%.4f GBX".format(data.released.toDouble() / 100000000))
                        Spacer(Modifier.height(8.dp))
                        Text("Vesting Progress", color = TextSec, fontSize = 11.sp)
                        Spacer(Modifier.height(4.dp))
                        LinearProgressIndicator(progress = { (data.vestingProgressPct / 100f).toFloat() }, modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)), color = Accent, trackColor = BorderCol)
                        Text("%.2f%% (${data.currentBlock}/${data.vestingBlocks})".format(data.vestingProgressPct), color = TextSec, fontSize = 11.sp)
                        Spacer(Modifier.height(4.dp))
                        DetailRow("Signers", data.signers.joinToString(", ") + " (${data.requiredSignatures} req)")
                    }
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Propose Release") {
            OutlinedTextField(value = recipient, onValueChange = { recipient = it }, label = { Text("Recipient Address") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = amount, onValueChange = { amount = it }, label = { Text("Amount (GBX)") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Button(onClick = { vm.proposeRelease(amount.toDoubleOrNull() ?: 0.0, recipient) }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Propose Release", color = Color.Black) }
        }
        Spacer(Modifier.height(12.dp))
        SectionCard("Approve Release") {
            OutlinedTextField(value = releaseId, onValueChange = { releaseId = it }, label = { Text("Release ID") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(value = signer, onValueChange = { signer = it }, label = { Text("Signer Address") }, modifier = Modifier.fillMaxWidth(), singleLine = true, colors = fieldColors(), textStyle = androidx.compose.ui.text.TextStyle(color = TextPri))
            Spacer(Modifier.height(8.dp))
            Button(onClick = { vm.approveRelease(releaseId.toIntOrNull() ?: 0, signer) }, colors = ButtonDefaults.buttonColors(Accent)) { Text("Approve", color = Color.Black) }
        }
    }
}

@Composable
private fun ValidatorScreen() {
    val vm: ValidatorViewModel = hiltViewModel()
    val uiState by vm.uiState.collectAsState()
    val scroll = rememberScrollState()
    LaunchedEffect(Unit) { vm.loadAnalytics() }
    Column(Modifier.fillMaxSize().background(DarkBg).verticalScroll(scroll).padding(16.dp)) {
        when (val s = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxWidth().padding(32.dp), contentAlignment = Alignment.Center) { CircularProgressIndicator(color = Accent) }
            is UiState.Error -> Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) { Text(s.message, color = Red, modifier = Modifier.padding(16.dp)) }
            is UiState.Success -> {
                SectionCard("Validator Analytics") {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        MetricCard("Total Validators", "1", Modifier.weight(1f))
                        MetricCard("Block Height", "35", Modifier.weight(1f))
                    }
                }
                Spacer(Modifier.height(12.dp))
                SectionCard("Balance History") {
                    Text("Chart visualization of total supply and fund balance over time.", color = TextSec, fontSize = 13.sp)
                    Spacer(Modifier.height(8.dp))
                    Box(Modifier.fillMaxWidth().height(160.dp).clip(RoundedCornerShape(8.dp)).background(DarkBg).border(1.dp, BorderCol, RoundedCornerShape(8.dp)), contentAlignment = Alignment.Center) {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp).height(120.dp), verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.SpaceBetween) {
                                listOf(0.3f, 0.5f, 0.4f, 0.7f, 0.6f, 0.9f, 0.8f, 1.0f).forEach { p ->
                                    Box(Modifier.width(24.dp).height((120 * p).dp).clip(RoundedCornerShape(4.dp)).background(Brush.verticalGradient(listOf(Accent, Accent.copy(alpha = 0.3f)))))
                                }
                            }
                            Spacer(Modifier.height(4.dp))
                            Text("Supply over time", color = TextSec, fontSize = 11.sp)
                        }
                    }
                }
                Spacer(Modifier.height(12.dp))
                SectionCard("Validator Performance") {
                    Row(Modifier.fillMaxWidth().background(DarkBg, RoundedCornerShape(4.dp)).padding(horizontal = 8.dp, vertical = 6.dp)) {
                        TableCell("Validator", Modifier.weight(1.5f)); TableCell("Stake", Modifier.weight(1f)); TableCell("Blocks", Modifier.weight(1f)); TableCell("Missed", Modifier.weight(1f)); TableCell("Status", Modifier.weight(1f))
                    }
                    HorizontalDivider(color = DividerCol)
                    ItemRow("GTestVal...1", "1,000.00", "1", "0", Accent)
                }
            }
        }
    }
}

@Composable
private fun ItemRow(c1: String, c2: String, c3: String, c4: String, statusColor: Color) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(c1, color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1.5f), maxLines = 1, overflow = TextOverflow.Ellipsis)
        Text(c2, color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f))
        Text(c3, color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f))
        Text(c4, color = TextSec, fontSize = 12.sp, modifier = Modifier.weight(1f))
        Box(Modifier.size(8.dp).clip(CircleShape).background(statusColor))
    }
}

@Composable
private fun SectionCard(title: String, content: @Composable () -> Unit) {
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(DarkCard), shape = RoundedCornerShape(12.dp)) {
        Column(Modifier.padding(16.dp)) { Text(title, color = TextPri, fontWeight = FontWeight.Bold, fontSize = 16.sp); Spacer(Modifier.height(8.dp)); content() }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth().padding(vertical = 2.dp)) {
        Text(label, color = TextSec, fontSize = 11.sp, modifier = Modifier.width(110.dp))
        Text(value, color = TextPri, fontSize = 12.sp, modifier = Modifier.weight(1f), maxLines = 2, overflow = TextOverflow.Ellipsis, fontFamily = if (value.length > 20) androidx.compose.ui.text.font.FontFamily.Monospace else androidx.compose.ui.text.font.FontFamily.Default)
    }
}

@Composable
private fun TableCell(text: String, modifier: Modifier = Modifier) {
    Text(text, color = TextSec, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, modifier = modifier)
}

@Composable
private fun SyncBadge(isSynced: Boolean, modifier: Modifier = Modifier) {
    Box(modifier.clip(RoundedCornerShape(4.dp)).background(if (isSynced) Color(0xFF065F46) else Color(0xFF78350F)).padding(horizontal = 6.dp, vertical = 2.dp)) {
        Text(if (isSynced) "Synced" else "Behind", color = Color.White, fontSize = 11.sp, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun StatusDot(isOnline: Boolean, modifier: Modifier = Modifier) {
    Row(modifier, verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(8.dp).clip(CircleShape).background(if (isOnline) Accent else Red))
        Spacer(Modifier.width(4.dp)); Text(if (isOnline) "Online" else "Offline", color = TextSec, fontSize = 11.sp)
    }
}

@Composable
private fun MetricCard(label: String, value: String, modifier: Modifier = Modifier) {
    Card(modifier, colors = CardDefaults.cardColors(DarkBg), shape = RoundedCornerShape(8.dp)) {
        Column(Modifier.padding(10.dp), horizontalAlignment = Alignment.CenterHorizontally) {
            Text(label, color = TextSec, fontSize = 11.sp)
            Spacer(Modifier.height(4.dp))
            Text(value, color = Accent, fontWeight = FontWeight.Bold, fontSize = 15.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, textAlign = TextAlign.Center)
        }
    }
}

@Composable
private fun fieldColors() = OutlinedTextFieldDefaults.colors(focusedTextColor = TextPri, unfocusedTextColor = TextPri, cursorColor = Accent, focusedBorderColor = Accent, unfocusedBorderColor = BorderCol, focusedLabelColor = Accent, unfocusedLabelColor = TextSec)
