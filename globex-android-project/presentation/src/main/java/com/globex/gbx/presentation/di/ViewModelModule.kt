package com.globex.gbx.presentation.di

import androidx.lifecycle.ViewModel
import com.globex.gbx.feature_explorer.presentation.ExplorerViewModel
import com.globex.gbx.feature_fund.presentation.FundViewModel
import com.globex.gbx.feature_mining.presentation.MiningViewModel
import com.globex.gbx.feature_nodes.presentation.NodesViewModel
import com.globex.gbx.feature_settings.presentation.SettingsViewModel
import com.globex.gbx.feature_staking.presentation.StakingViewModel
import com.globex.gbx.feature_validator.presentation.ValidatorViewModel
import com.globex.gbx.feature_wallet.presentation.WalletViewModel
import dagger.Binds
import dagger.MapKey
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.android.components.ViewModelComponent
import dagger.multibindings.IntoMap
import kotlin.reflect.KClass

@MustBeDocumented
@Target(AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
@MapKey
annotation class ViewModelKey(val value: KClass<out ViewModel>)

@Module
@InstallIn(ViewModelComponent::class)
abstract class ViewModelModule {

    @Binds
    @IntoMap
    @ViewModelKey(WalletViewModel::class)
    abstract fun bindWalletViewModel(viewModel: WalletViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(MiningViewModel::class)
    abstract fun bindMiningViewModel(viewModel: MiningViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(ExplorerViewModel::class)
    abstract fun bindExplorerViewModel(viewModel: ExplorerViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(NodesViewModel::class)
    abstract fun bindNodesViewModel(viewModel: NodesViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(StakingViewModel::class)
    abstract fun bindStakingViewModel(viewModel: StakingViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(SettingsViewModel::class)
    abstract fun bindSettingsViewModel(viewModel: SettingsViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(FundViewModel::class)
    abstract fun bindFundViewModel(viewModel: FundViewModel): ViewModel

    @Binds
    @IntoMap
    @ViewModelKey(ValidatorViewModel::class)
    abstract fun bindValidatorViewModel(viewModel: ValidatorViewModel): ViewModel
}
