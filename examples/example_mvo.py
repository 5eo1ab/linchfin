from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.core.clustering.sectors import SectorTree
from linchfin.core.portfolio.rules import RuleEngine
from linchfin.core.portfolio.mvo import MeanVarOptimizationEngine
from linchfin.data_handler.reader import DataReader
from linchfin.data_handler.wrangler import DataWrangler
from linchfin.metadata import ETF_SECTORS


if __name__ == '__main__':
    # 1. read data
    data_reader = DataReader(start='2019/01/01', end='2020/09/01')
    wrangler = DataWrangler()

    # 2. load sector tree
    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    # 3-1. filter asset universe
    filtered = sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 60)
    filtered = filtered[:10]
    asset_universe = AssetUniverse(assets=filtered)

    daily_close_price = data_reader.get_adj_close_price(asset_universe.symbols)
    daily_yield = wrangler.calc_daily_yield(daily_close_price)
    portfolio_engine = MeanVarOptimizationEngine(asset_universe=asset_universe, rule_engine=RuleEngine())
    print(portfolio_engine.simulate_portfolio(daily_yield=daily_yield, simulation_size=10))
    df = portfolio_engine.run(daily_yield=daily_yield, simulation_size=10)
    print(df)
