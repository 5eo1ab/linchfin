from matplotlib import pyplot

from linchfin.common.calc import calc_volatility, calc_portfolio_return, calc_sharp_ratio
from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.base.dataclasses.value_types import Feature
from linchfin.core.clustering.sectors import SectorTree
from linchfin.core.portfolio.rules import RuleEngine
from linchfin.core.portfolio.hierarchical import HierarchyRiskParityEngine
from linchfin.data_handler.reader import DataReader
from linchfin.metadata import ETF_SECTORS
from linchfin.common.calc import calc_monthly_returns, calc_corr, calc_daily_returns
from linchfin.common.cov import CovarianceEstimator
from linchfin.simulation.backtest import BacktestSimulator


if __name__ == '__main__':
    # 1. read data
    data_reader = DataReader(start='2017/01/01', end='2021/04/20')

    # 2. load sector tree
    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    # 3-1. filter asset universe
    filtered = sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 60)
    asset_universe = AssetUniverse(assets=filtered)

    # 3-2. filter asset universe(exclude: Inverse, Leverage)
    removable_assets = asset_universe.filter_assets(
        filter_func=lambda _asset: "Leverage" in _asset.asset_class.name or "Inverse" in _asset.asset_class.name
    )

    for _asset in removable_assets:
        asset_universe.pop(asset=_asset)

    # 4. load time_series
    time_series = data_reader.get_adj_close_price(symbols=asset_universe.symbols)
    time_series = time_series.dropna(axis=1)
    time_series_monthly = calc_monthly_returns(time_series=time_series)

    # 5. remove assets unloading time_series
    items = set(asset_universe.symbols) - set(time_series.columns)
    for asset_code in items:
        asset = asset_universe.get_asset(code=asset_code)
        asset_universe.pop(asset)

    # 6. calc corr
    corr = calc_corr(time_series=time_series_monthly)
    corr = Feature(name='corr', value=corr)

    # 7. run HRP
    hrp = HierarchyRiskParityEngine(asset_universe=asset_universe)
    portfolio = hrp.run(corr=corr)

    # 8. Check portfolio
    print(portfolio.is_valid())
    for k, v in portfolio.weights.items():
        print(k, v)

    for k, v in portfolio.sector_weights.items():
        print(k, v)

    rule_applied_weights = RuleEngine.run(portfolio=portfolio, min_cutoff=0.05)
    portfolio.set_weights(weights=rule_applied_weights)
    portfolio.show_summary()

    # 8. run backtest
    backtest_simulator = BacktestSimulator()
    daily_returns = calc_daily_returns(time_series=time_series)
    backtest_result = backtest_simulator.run(portfolio=portfolio, daily_returns=daily_returns)

    # 9. summary
    # 9-1. show evaluation metrics
    portfolio_returns = calc_portfolio_return(portfolio=portfolio, daily_returns=daily_returns)
    sharp_ratio = calc_sharp_ratio(daily_returns=portfolio_returns, risk_free_return=0.01)
    volatility = calc_volatility(period_returns=portfolio_returns)
    print(f"Portfolio evaluation metric\n"
          f"sharp_ratio: {sharp_ratio}\n"
          f"volatility: {volatility}\n")

    # 9-2. show plot
    backtest_result.plot()
    pyplot.show()
