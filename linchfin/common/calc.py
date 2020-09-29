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
    sharp_ratio = (portfolio_yield_without_risk_free.mean()) / np.sqrt(portfolio_volatility)
    return sharp_ratio

