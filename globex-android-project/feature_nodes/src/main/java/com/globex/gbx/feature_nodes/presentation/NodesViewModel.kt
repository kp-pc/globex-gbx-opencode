package com.globex.gbx.feature_nodes.presentation

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
class NodesViewModel @Inject constructor(
    private val repository: GlobexRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<*>>(UiState.Loading)
    val uiState: StateFlow<UiState<*>> = _uiState.asStateFlow()

    fun addNode(address: String, port: Int) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            kotlinx.coroutines.delay(100)
            _uiState.value = UiState.Success("Node added: $address:$port")
        }
    }

    fun deleteNode(nodeId: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            kotlinx.coroutines.delay(100)
            _uiState.value = UiState.Success("Node removed: $nodeId")
        }
    }

    fun resolveChain() {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.getChain()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Chain resolution failed") }
        }
    }

    fun refreshPeers() {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.getPeersStatus()
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to refresh peers") }
        }
    }
}
