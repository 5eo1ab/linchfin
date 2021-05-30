from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.core.clustering.sectors import SectorTree
from linchfin.core.portfolio.rules import RuleEngine
from linchfin.core.portfolio.mvo import MeanVarOptimizationEngine
from linchfin.data_handler.reader import DataReader
from linchfin.metadata import ETF_SECTORS
from linchfin.common.calc import calc_daily_returns
from linchfin.common.calc import calc_total_return


if __name__ == '__main__':
    # 1. read data
    data_reader = DataReader(start='2019/01/01', end='2020/09/01')
    # 2. load sector tree
    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    # 3-1. filter asset universe
    filtered = sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 60)
    filtered = filtered[:10]
    asset_universe = AssetUniverse(assets=filtered)

    daily_close_price = data_reader.get_adj_close_price(asset_universe.symbols)
    daily_returns = calc_daily_returns(daily_close_price)
    portfolio_engine = MeanVarOptimizationEngine(asset_universe=asset_universe, rule_engine=RuleEngine())
    port = portfolio_engine.run(daily_returns=daily_returns, simulation_size=10)
    rule_engine = RuleEngine()
    weights = rule_engine.run(port, 0.05)
    port.set_weights(weights=weights)
    recommended_quantity = rule_engine.calc_recommended_quantity(portfolio=port, close_price=daily_close_price.iloc[-1])
    minimum_quantity = rule_engine.calc_minimum_quantity(portfolio=port, close_price=daily_close_price.iloc[-1])

    recommended_quantity_valuation = daily_close_price[port.symbols].iloc[-1] * recommended_quantity
    minimum_quantity_valuation = daily_close_price[port.symbols].iloc[-1] * minimum_quantity
    print("recommended port diff", port.to_series() - recommended_quantity_valuation / recommended_quantity_valuation.sum())
    print("minimum port diff", port.to_series() - minimum_quantity_valuation / minimum_quantity_valuation.sum())
