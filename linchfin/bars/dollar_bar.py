import pandas as pd


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
