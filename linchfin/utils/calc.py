import numpy as np
import pandas as pd


def calc_trading_value(prices, volumes) -> np.ndarray:
    if not isinstance(prices, np.ndarray):
        prices = np.array(prices)

    if not isinstance(volumes, np.ndarray):
        volumes = np.array(volumes)
    return prices * volumes


def get_dollar_bars(index, trading_values, threshold=2273626800):
    def get_dollar_iter():
        acc = 0
        for i, _value in zip(index, trading_values):
            acc += _value
            if acc > threshold:
                yield i, _value
                acc = 0

    df = pd.DataFrame(list(get_dollar_iter()), columns=['index', 'dollar_value'])
    return df.set_index('index')


def calc_total_return(prices):
    return prices.diff(1)[1:].sum()


def calc_installment_return(prices, holding_idx):
    if not isinstance(holding_idx, np.ndarray):
        holding_idx = np.array(holding_idx)

    weighted_changes = prices.diff(1)[1:] * holding_idx[1:]
    return weighted_changes.sum()
