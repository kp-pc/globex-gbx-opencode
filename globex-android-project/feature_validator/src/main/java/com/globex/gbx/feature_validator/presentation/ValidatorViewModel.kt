package com.globex.gbx.feature_validator.presentation

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
class ValidatorViewModel @Inject constructor(
    private val repository: GlobexRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<*>>(UiState.Loading)
    val uiState: StateFlow<UiState<*>> = _uiState.asStateFlow()

    fun loadValidatorStats(address: String) {
        viewModelScope.launch(Dispatchers.IO) {
            _uiState.value = UiState.Loading
            repository.getValidatorStats(address)
                .onSuccess { _uiState.value = UiState.Success(it) }
                .onFailure { _uiState.value = UiState.Error(it.message ?: "Failed to load validator stats") }
        }
    }
}
