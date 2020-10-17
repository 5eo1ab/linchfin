import pandas as pd
from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries


class TimeSeriesHandler:
    def __init__(self, portfolio: Portfolio=None):
        pass

    def get_mean_trading_values(self, trading_values: TimeSeries, rule='W'):
        portfolio_weekly_trading_mean_value = trading_values.resample(rule).sum().mean()
        return portfolio_weekly_trading_mean_value

    @staticmethod
    def find_loc(df, dates):
        marks = []
        for date in dates:
            marks.append(df.index.get_loc(date))
        return marks

    @classmethod
    def get_dollar_bars(cls, series: pd.Series, threshold=227362680000):
        df = pd.DataFrame(list(cls._get_dollar_iter(series=series, threshold=threshold)), columns=['index', 'dollar_value'])
        return df.set_index('index')

    @staticmethod
    def _get_dollar_iter(series, threshold):
        acc = 0
        for i, _value in series.iteritems():
            acc += _value
            if acc > threshold:
                yield i, _value
                acc = 0


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader

    reader = DataReader()
    # symbol = 'AAPL'
    symbols = ['AAPL', 'PIO']
    closed_prices = reader.get_adj_close_price(symbols=symbols)
    trading_values = reader.get_trading_value(symbols=symbols)

    time_series_handler = TimeSeriesHandler()
    _mean_trading_value = time_series_handler.get_mean_trading_values(trading_values=trading_values)

    print(_mean_trading_value)
    # db = time_series_handler.get_dollar_bars(series=ts[symbol], threshold=2273626800)
    #
    # from matplotlib import pyplot as plt
    # closed_prices.plot(linestyle='-', markevery=time_series_handler.find_loc(ts, db.index), marker='o', markerfacecolor='black')
    # plt.show()
