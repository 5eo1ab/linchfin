from matplotlib import pyplot

from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.base.dataclasses.value_types import Feature
from linchfin.core.clustering.hierarchical import HierarchyRiskParityEngine
from linchfin.core.clustering.sectors import SectorTree
from linchfin.data_handler.reader import DataReader
from linchfin.data_handler.wrangler import DataWrangler
from linchfin.metadata import ETF_SECTORS
from linchfin.simulation.backtest import BackTestSimulator

if __name__ == '__main__':
    # 1. read data
    data_reader = DataReader(start='2019/01/01', end='2020/09/01')
    wrangler = DataWrangler()

    # 2. load sector tree
    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    # 3-1. filter asset universe
    filtered = sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 60)
    asset_universe = AssetUniverse(assets=filtered)

    # 3-2. filter asset universe(exclude: Inverse, Leverage)
    removable_assets = []
    for asset_id, asset in asset_universe.assets.items():
        if "Inverse" in asset.asset_class.asset_class_name or "Leverage" in asset.asset_class.asset_class_name:
            removable_assets.append(asset)

    for _asset in removable_assets:
        asset_universe.pop(asset=_asset)

    # 4. load time_series
    time_series = data_reader.get_adj_close_price(symbols=asset_universe.symbols)
    time_series = time_series.dropna(axis=1)
    time_series_monthly = wrangler.calc_monthly_yield(time_series=time_series)

    # 5. remove assets unloading time_series
    items = set(asset_universe.symbols) - set(time_series.columns)
    for asset_code in items:
        asset = asset_universe.get_asset(code=asset_code)
        asset_universe.pop(asset)

    # 6. calc corr
    corr = wrangler.calc_corr(time_series=time_series_monthly)
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

    portfolio.round(portfolio.weights)
    portfolio.show_summary()

    # 8. run backtest
    backtest_simulator = BackTestSimulator()
    daily_yield = wrangler.calc_daily_yield(time_series=time_series)
    backtest_result = backtest_simulator.run(portfolio=portfolio, daily_yield=daily_yield)

    # 9. show plot
    backtest_result.plot()
    pyplot.show()
