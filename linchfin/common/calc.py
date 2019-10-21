import numpy as np
import pandas as pd


def calc_trading_value(prices, volumes) -> np.ndarray:
    if not isinstance(prices, np.ndarray):
        prices = np.array(prices)

    if not isinstance(volumes, np.ndarray):
        volumes = np.array(volumes)
    return prices * volumes


def calc_total_return(prices):
    return prices.diff(1)[1:].sum()


def calc_installment_return(prices, holding_idx):
    if not isinstance(holding_idx, np.ndarray):
        holding_idx = np.array(holding_idx)

    if not isinstance(holding_idx, np.ndarray):
        prices = np.array(prices)

    weighted_changes = np.diff(prices) * holding_idx[:, 1:]
    return weighted_changes.sum()


def calc_compound_rate(rate, years):
    return (1 - rate ** years) / (1 - rate)


def get_variance(sample_data_returns, weights):
    cov_matrix_portfolio = sample_data_returns.cov() * 250
    variance = np.dot(weights.T, np.dot(cov_matrix_portfolio, weights))
    return variance


def get_annual_returns(sample_data_returns, weights):
    annual_returns = sample_data_returns.mean() * 250
    expected_return = np.sum(annual_returns * weights)
    return expected_return
