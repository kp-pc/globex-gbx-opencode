package com.globex.gbx.feature_fund.presentation

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
class FundViewModel @Inject constructor(
    private val repository: GlobexRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<*>>(UiState.Loading)
    val uiState: StateFlow<UiState<*>> = _uiState.asStateFlow()

    fun loadReport() {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.getFundReport()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to load report") }
        }
    }

    fun proposeRelease(amount: Long, recipient: String, reason: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.proposeRelease(amount, recipient, reason)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to propose release") }
        }
    }

    fun approveRelease(proposalId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.approveRelease(proposalId)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to approve release") }
        }
    }
}
