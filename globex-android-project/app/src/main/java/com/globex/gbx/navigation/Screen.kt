package com.globex.gbx.navigation

sealed class Screen(val route: String) {
    data object Home : Screen("home")
    data object Wallet : Screen("wallet")
    data object Mine : Screen("mine")
    data object Explorer : Screen("explorer")
    data object Nodes : Screen("nodes")
    data object Stake : Screen("stake")
    data object Settings : Screen("settings")
    data object Fund : Screen("fund")
    data object Validator : Screen("validator")
}
