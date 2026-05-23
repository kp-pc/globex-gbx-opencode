package com.globex.gbx.feature_wallet.presentation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.globex.gbx.presentation.ui.UiState
import com.globex.gbx.repository.GlobexRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class WalletViewModel @Inject constructor(
    private val repository: GlobexRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<*>>(UiState.Loading)
    val uiState: StateFlow<UiState<*>> = _uiState.asStateFlow()

    private val _balance = MutableStateFlow<UiState<Long>>(UiState.Loading)
    val balance: StateFlow<UiState<Long>> = _balance.asStateFlow()

    fun loadWallet(address: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _balance.value = UiState.Loading
            repository.getBalance(address)
                .onSuccess { _balance.value = UiState.Success(it.balance) }
                .onFailure { _balance.value = UiState.Error(it.message ?: "Unknown error") }
        }
    }

    fun createWallet() {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.createWallet()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to create wallet") }
        }
    }

    fun importWallet(privateKey: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.importWallet(privateKey)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to import wallet") }
        }
    }

    fun sendTransaction(sender: String, recipient: String, amount: Long, fee: Long) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.sendTransaction(sender, recipient, amount, fee)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Transaction failed") }
        }
    }
}
