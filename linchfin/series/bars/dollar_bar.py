import pandas as pd
from matplotlib import pyplot as plt
from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries
from linchfin.common.calc import calc_daily_returns, calc_portfolio_return


class TimeSeriesHandler:
    def __init__(self, portfolio: Portfolio):
        self.portfolio = portfolio

    def get_mean_trading_values(self, trading_values: TimeSeries, rule='W'):
        mean_trading_values = trading_values.resample(rule).sum().mean()
        weighted_mean_trading_values = mean_trading_values * self.portfolio.to_series()
        return weighted_mean_trading_values.sum()

    def get_weighted_trading_values(self, trading_values: TimeSeries):
        return (trading_values[self.portfolio.symbols] * self.portfolio.to_series()).sum(axis=1)

    def show_plot(self, asset_closed_prices: TimeSeries, asset_trading_values: TimeSeries, rule='W'):
        asset_daily_returns = calc_daily_returns(time_series=asset_closed_prices)
        portfolio_return = calc_portfolio_return(portfolio=self.portfolio, daily_returns=asset_daily_returns)

        portfolio_mean_trading_value = self.get_mean_trading_values(trading_values=asset_trading_values,
                                                                    rule=rule)
        portfolio_trading_values = self.get_weighted_trading_values(trading_values=trading_values)
        portfolio_dollar_bar = self.get_dollar_bars(trading_value=portfolio_trading_values,
                                                    threshold=portfolio_mean_trading_value)
        mark_points = self.find_mark_points(portfolio_return, portfolio_dollar_bar.index)

        port_weights = {k: float(v) for k, v in self.portfolio.weights.items()}
        plot_title = f"Portfolio({port_weights})"
        figure = portfolio_return.add(1).plot(title=plot_title, linestyle='-',
                                              markevery=mark_points, marker='o', markerfacecolor='black')
        plt.show()
        return figure

    @staticmethod
    def find_mark_points(df, dates):
        marks = []
        for date in dates:
            marks.append(df.index.get_loc(date))
        return marks

    @classmethod
    def get_dollar_bars(cls, trading_value: TimeSeries, threshold=227362680000):
        df = pd.DataFrame(list(cls._get_dollar_iter(series=trading_value, threshold=threshold)),
                          columns=['index', 'dollar_value'])
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
    from linchfin.base.dataclasses.entities import Portfolio

    reader = DataReader(start='2018/01/01')
    # symbol = 'AAPL'
    weights = {
        "MSFT": 0.2,
        "PIO": 0.2,
        'DIS': 0.4,
        "SHY": 0.2
    }
    symbols = list(weights.keys())

    port = Portfolio()
    port.set_weights(weights=weights)
    port.is_valid()

    closed_prices = reader.get_adj_close_price(symbols=symbols)
    trading_values = reader.get_trading_value(symbols=symbols)

    time_series_handler = TimeSeriesHandler(portfolio=port)
    _mean_trading_value = time_series_handler.get_mean_trading_values(trading_values=trading_values)
    time_series_handler.show_plot(asset_closed_prices=closed_prices, asset_trading_values=trading_values, rule='M')
    print(_mean_trading_value)
