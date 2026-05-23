package com.globex.gbx.feature_settings.presentation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.globex.gbx.presentation.ui.UiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class SettingsViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<*>>(UiState.Loading)
    val uiState: StateFlow<UiState<*>> = _uiState.asStateFlow()

    fun toggleScreenshotProtection(enabled: Boolean) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Success("Screenshot protection: $enabled")
        }
    }

    fun setPin(pin: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Success("PIN set")
        }
    }

    fun toggleBiometric(enabled: Boolean) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Success("Biometric: $enabled")
        }
    }
}
