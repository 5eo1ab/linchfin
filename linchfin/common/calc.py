from typing import Optional

import numpy as np
import pandas as pd

from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries

DAILY = 1
MONTHLY = 21
ANNUAL = 252


def calc_beta(daily_returns: TimeSeries, bm_asset_code: str):
    def bm_cov(ts, bm_returns):
        bm_covariance = pd.concat([ts, bm_returns], axis=1).cov()
        return bm_covariance.__array__()[0, 1]

    bm_returns = daily_returns[bm_asset_code]
    bm_variance = bm_returns.var()
    return daily_returns.apply(lambda ts: bm_cov(ts, bm_returns) / bm_variance)


def calc_cumulative_returns(daily_returns: TimeSeries):
    return daily_returns.add(1).cumprod()


def calc_total_return(prices: TimeSeries):
    return (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0]


def calc_daily_returns(time_series: TimeSeries) -> TimeSeries:
    return time_series.pct_change(periods=DAILY)


def calc_monthly_returns(time_series: TimeSeries) -> TimeSeries:
    return time_series.resample('M').ffill().pct_change()


def calc_annal_returns(time_series: TimeSeries) -> TimeSeries:
    return time_series.resample('Y').ffill().pct_change()


def calc_corr(time_series: TimeSeries, method='pearson', min_periods: Optional[int] = 1):
    corr = time_series.corr(method=method, min_periods=min_periods)
    return corr


def calc_cov(time_series: TimeSeries,
             min_periods: Optional[int] = None, degree_of_freedom: Optional[int] = None) -> pd.DataFrame:
    cov = time_series.cov(min_periods=min_periods, ddof=degree_of_freedom)
    return cov


def calc_portfolio_asset_returns(portfolio: Portfolio, daily_returns: TimeSeries) -> TimeSeries:
    daily_return = daily_returns.add(1)
    daily_return.iloc[0] = portfolio.to_series()
    portfolio_asset_yields = daily_return[portfolio.symbols].cumprod()
    return portfolio_asset_yields


def calc_portfolio_return(portfolio: Portfolio, daily_returns: TimeSeries) -> TimeSeries:
    """
    calc portfolio yield
    :param portfolio: Portfolio
    :param daily_returns: TimeSeries
    :return:
    """
    portfolio_asset_yields = calc_portfolio_asset_returns(portfolio=portfolio, daily_returns=daily_returns)
    return portfolio_asset_yields.sum(axis=1).sub(1)


def calc_volatility(time_series: TimeSeries) -> float:
    """
    calculate portfolio volatility

    :param time_series: TimeSeries
    :return:
    """
    return time_series.var()


def calc_sharp_ratio(daily_returns: TimeSeries, risk_free_return: float = 0.0) -> float:
    """
    Calculate sharp ratio: (return of portfolio - risk-free rate) / standard deviation of the portfolio excess return

    :param daily_returns:
    :param risk_free_return:
    :return:
    """

    portfolio_volatility = calc_volatility(time_series=daily_returns)
    portfolio_yield_without_risk_free = daily_returns.sub(risk_free_return)
    sharp_ratio = (portfolio_yield_without_risk_free.mean()) / np.sqrt(portfolio_volatility)
    return sharp_ratio


def calc_expected_return(portfolio: Portfolio, asset_returns: pd.Series):
    portfolio_sr = portfolio.to_series()
    return (asset_returns.loc[portfolio_sr.index] * portfolio_sr).sum()
