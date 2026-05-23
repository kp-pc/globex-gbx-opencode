package com.globex.gbx.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable

@Composable
fun NavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Home.route,
        modifier = modifier
    ) {
        composable(Screen.Home.route) {
            HomeScreen()
        }
        composable(Screen.Wallet.route) {
            WalletScreen()
        }
        composable(Screen.Mine.route) {
            MineScreen()
        }
        composable(Screen.Explorer.route) {
            ExplorerScreen()
        }
        composable(Screen.Nodes.route) {
            NodesScreen()
        }
        composable(Screen.Stake.route) {
            StakeScreen()
        }
        composable(Screen.Settings.route) {
            SettingsScreen()
        }
        composable(Screen.Fund.route) {
            FundScreen()
        }
        composable(Screen.Validator.route) {
            ValidatorScreen()
        }
    }
}

@Composable
private fun HomeScreen() {
    androidx.compose.material3.Text("Home")
}

@Composable
private fun WalletScreen() {
    androidx.compose.material3.Text("Wallet")
}

@Composable
private fun MineScreen() {
    androidx.compose.material3.Text("Mining")
}

@Composable
private fun ExplorerScreen() {
    androidx.compose.material3.Text("Explorer")
}

@Composable
private fun NodesScreen() {
    androidx.compose.material3.Text("Nodes")
}

@Composable
private fun StakeScreen() {
    androidx.compose.material3.Text("Staking")
}

@Composable
private fun SettingsScreen() {
    androidx.compose.material3.Text("Settings")
}

@Composable
private fun FundScreen() {
    androidx.compose.material3.Text("Fund")
}

@Composable
private fun ValidatorScreen() {
    androidx.compose.material3.Text("Validator")
}
