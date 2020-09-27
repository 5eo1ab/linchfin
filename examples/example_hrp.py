from linchfin.data_handler.reader import DataReader
from linchfin.data_handler.wrangler import DataWrangler
from linchfin.core.clustering.sectors import SectorTree
from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.base.dataclasses.value_types import Feature, Metric, TimeSeries
from linchfin.metadata import ETF_SECTORS
from linchfin.core.clustering.hierarchical import HierarchyRiskParityEngine


if __name__ == '__main__':
    data_reader = DataReader(start='2019/01/01', end='2020/01/01')
    wrangler = DataWrangler()

    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    filtered = sector_tree.filter(key='Global', filter_func=lambda x: x.cap_size > 10)
    asset_universe = AssetUniverse(assets=filtered)

    timeseries = data_reader.get_adj_close_price(symbols=asset_universe.symbols)
    monthly_timeseries = wrangler.calc_monthly_yield(timeseries=timeseries)
    corr = wrangler.calc_corr(timeseries=monthly_timeseries)
    corr = Feature(name='corr', value=corr)

    hrp = HierarchyRiskParityEngine(asset_universe=asset_universe)
    portfolio = hrp.run(corr=corr)
    print(portfolio.is_valid())
    for k, v in portfolio.weights.items():
        print(k, v)

    for k, v in portfolio.sector_weights.items():
        print(k, v)
    portfolio.round(portfolio.weights)
    portfolio.show_summary()
