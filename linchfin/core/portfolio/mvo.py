import numpy as np
import pandas as pd
import random

from collections import defaultdict
from linchfin.base.dataclasses.entities import Portfolio, AssetUniverse
from linchfin.base.dataclasses.value_types import TimeSeries, Weights, Weight
from linchfin.core.portfolio.rules import RuleEngine
from linchfin.common.calc import calc_volatility, calc_portfolio_yield, calc_sharp_ratio


class MeanVarOptimizationEngine:
    def __init__(self, asset_universe: AssetUniverse, rule_engine: RuleEngine = None):
        self.asset_universe = asset_universe
        self.rule_engine = rule_engine

    def run(self, daily_yield: TimeSeries, kind='sharp_ratio', simulation_size=1000) -> Portfolio:
        simulation_result = self.simulate_portfolio(daily_yield=daily_yield, simulation_size=simulation_size)
        weights = self.get_optimized_weights(simulation_result=simulation_result, kind=kind)
        return Portfolio(asset_universe=self.asset_universe, weights=weights)

    def get_optimized_weights(self, simulation_result: pd.DataFrame, kind) -> Weights:
        if kind not in ['sharp_ratio', 'volatility']:
            raise KeyError("unsupported optimization types")

        if kind == 'sharp_ratio':
            weights = self.get_max_sharp_ratio(simulation_result=simulation_result)
        else:
            weights = self.get_min_volatility_weights(simulation_result=simulation_result)
        return weights

    def get_min_volatility_weights(self, simulation_result):
        idx = simulation_result['volatility'].argmin()
        row = simulation_result.iloc[idx]
        return row['weights']

    def get_max_sharp_ratio(self, simulation_result):
        idx = simulation_result['sharp_ratio'].argmax()
        row = simulation_result.iloc[idx]
        return row['weights']

    def simulate_portfolio(self, daily_yield: TimeSeries, simulation_size=1000) -> pd.DataFrame:
        data = defaultdict(list)
        for idx in range(simulation_size):
            portfolio_candidate = self.get_portfolio_candidate(min_cutoff=0.01)
            portfolio_candidate_yield = calc_portfolio_yield(portfolio=portfolio_candidate, daily_yield=daily_yield)
            sharp_ratio = calc_sharp_ratio(daily_yield=portfolio_candidate_yield)
            volatility = calc_volatility(daily_yield=portfolio_candidate_yield)

            data['sharp_ratio'].append(sharp_ratio)
            data['volatility'].append(volatility)
            data['weights'].append(portfolio_candidate.weights)
        return pd.DataFrame(data=data)

    def get_portfolio_candidate(self, min_cutoff) -> Portfolio:
        random_weights = self.get_random_weights(min_cutoff=min_cutoff)
        portfolio_candi = Portfolio(asset_universe=self.asset_universe, weights=random_weights)
        portfolio_candi.is_valid()
        if self.rule_engine:
            rule_applied_weights = self.rule_engine.run(portfolio=portfolio_candi, min_cutoff=min_cutoff)
            portfolio_candi.set_weights(weights=rule_applied_weights)

        if portfolio_candi.is_valid():
            return portfolio_candi
        raise RuntimeError("Fail to get portfolio candidate")

    def get_random_weights(self, min_cutoff, asset_size=5) -> Weights:
        weights = Weights()
        selected_assets = random.choices(list(self.asset_universe.assets.values()), k=asset_size)
        selected_asset_size = len(selected_assets)

        randomized_values = np.random.random([selected_asset_size])
        random_weights = randomized_values / sum(randomized_values)

        while sum(random_weights > min_cutoff) < min_cutoff:
            randomized_values = np.random.random([selected_asset_size])
            random_weights = randomized_values / sum(randomized_values)
        random_weights[random_weights < min_cutoff] = 0
        random_weights = random_weights / sum(random_weights)

        for (_asset_id, _asset), _random_weight in zip(self.asset_universe.assets.items(), random_weights):
            weights[_asset.code] = Weight(_random_weight)
        return weights
