import numpy as np
from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries


def calc_portfolio_yield(portfolio: Portfolio, daily_yield: TimeSeries) -> TimeSeries:
    """
    calc portfolio yield
    :param portfolio: Portfolio
    :param daily_yield: TimeSeries
    :return:
    """
    daily_return = daily_yield.add(1)
    daily_return.iloc[0] = portfolio.to_series()
    portfolio_yield = daily_return[portfolio.symbols].cumprod()
    return portfolio_yield.sum(axis=1).sub(1)


def calc_volatility(daily_yield: TimeSeries) -> float:
    """
    calculate portfolio volatility

    :param daily_yield: TimeSeries
    :return:
    """
    return daily_yield.var()


def calc_sharp_ratio(daily_yield: TimeSeries, risk_free_return: float = 0.0) -> float:
    """
    Calculate sharp ratio: (return of portfolio - risk-free rate) / standard deviation of the portfolio excess return

    :param daily_yield:
    :param risk_free_return:
    :return:
    """

    portfolio_volatility = calc_volatility(daily_yield=daily_yield)
    portfolio_yield_without_risk_free = daily_yield.sub(risk_free_return)
    sharp_ratio = (portfolio_yield_without_risk_free.iloc[-1]) / np.sqrt(portfolio_volatility)
    return sharp_ratio

#
# def calc_trading_value(prices, volumes) -> np.ndarray:
#     if not isinstance(prices, np.ndarray):
#         prices = np.array(prices)
#
#     if not isinstance(volumes, np.ndarray):
#         volumes = np.array(volumes)
#     return prices * volumes
#
#
# def calc_total_return(prices):
#     return prices.diff(1)[1:].sum()
#
#
# def calc_installment_return(prices, holding_idx):
#     if not isinstance(holding_idx, np.ndarray):
#         holding_idx = np.array(holding_idx)
#
#     if not isinstance(holding_idx, np.ndarray):
#         prices = np.array(prices)
#
#     weighted_changes = np.diff(prices) * holding_idx[:, 1:]
#     return weighted_changes.sum()
#
#
# def calc_compound_rate(rate, years):
#     return (1 - rate ** years) / (1 - rate)
#
#
# def get_variance(sample_data_returns, weights):
#     cov_matrix_portfolio = sample_data_returns.cov() * 250
#     variance = np.dot(weights.T, np.dot(cov_matrix_portfolio, weights))
#     return variance
#
#
# def get_annual_returns(sample_data_returns, weights):
#     annual_returns = sample_data_returns.mean() * 250
#     expected_return = np.sum(annual_returns * weights)
#     return expected_return
