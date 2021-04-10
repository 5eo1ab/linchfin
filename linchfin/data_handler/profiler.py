from typing import List
from linchfin.base.dataclasses.value_types import TimeSeries
from linchfin.common.calc import *


class AssetProfiler:
    price_profile_func_map = {
        'total_returns': calc_total_return,
    }
    period_return_func = {
        'daily': calc_daily_returns,
        'monthly': calc_monthly_returns,
        'annual': calc_annual_returns
    }

    def __init__(self, bm_ticker="SPY"):
        self.bm_ticker = bm_ticker

    @property
    def period_return_profile_func_map(self):
        _period_return_profile_func_map = {
            'daily': self.daily_return_profile_func_map,
            'monthly': self.monthly_return_profile_func_map,
        }
        return _period_return_profile_func_map

    @property
    def daily_return_profile_func_map(self):
        _func_map = {
            'daily_volatility': calc_volatility,
            'sharp_ratio': calc_sharp_ratio,
            'cumulative_returns': calc_cumulative_returns,
            'beta': lambda daily_returns: calc_beta(daily_returns, self.bm_ticker)
        }
        return _func_map

    @property
    def monthly_return_profile_func_map(self):
        _func_map = {
                'monthly_volatility': calc_volatility,
            }
        return _func_map

    def profile(self, prices, factors: List[str] = None):
        factors_based_prices = list(set(self.price_profile_func_map.keys()).intersection(factors))
        factors_based_period_returns = dict()
        for _period, _period_func_map in self.period_return_profile_func_map.items():
            factors_based_period_returns[_period] = list(set(_period_func_map.keys()).intersection(factors))

        _profile = pd.DataFrame(columns=prices.columns)
        results = [self.profile_by_price(prices=prices, factors=factors_based_prices)]

        for _period, _period_func_map in self.period_return_profile_func_map.items():
            target_factors = factors_based_period_returns[_period]
            if target_factors:
                calc_period_return_func = self.period_return_func[_period]
                _period_returns = calc_period_return_func(prices)
                results.append(
                    self.profile_by_period_returns(period_returns=_period_returns,
                                                   period=_period, factors=target_factors)
                )

        profile_result = pd.concat(results)
        return profile_result

    def profile_by_price(self, prices: TimeSeries, factors: List[str] = None):
        _profile = pd.DataFrame(columns=prices.columns)
        for _factor in factors:
            _func = self.price_profile_func_map[_factor]
            _profile.loc[_factor] = _func(prices)
        return _profile

    def profile_by_period_returns(self, period_returns, factors, period='daily'):
        _profile = pd.DataFrame(columns=period_returns.columns)
        for _factor in factors:
            _func = self.period_return_profile_func_map[period][_factor]
            _profile.loc[_factor] = _func(period_returns)
        return _profile


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader

    tickers = ['MSFT', 'AAPL', 'TSLA', 'SPY']
    dr = DataReader(start='2019/01/01', end='2021/04/01')
    ts = dr.get_adj_close_price(tickers)

    profiler = AssetProfiler(bm_ticker='SPY')
    _profile_result = profiler.profile(prices=ts, factors=['total_returns', 'daily_returns', 'beta', 'daily_volatility', 'monthly_volatility'])
    print(_profile_result)
