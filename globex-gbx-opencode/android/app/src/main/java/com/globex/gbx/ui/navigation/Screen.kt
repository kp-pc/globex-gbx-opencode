package com.globex.gbx.ui.navigation

import androidx.compose.runtime.Stable

@Stable
sealed class Screen(val route: String) {
    object NativeDashboard : Screen("native_dashboard")
    object WebDashboard : Screen("web_dashboard")
}
