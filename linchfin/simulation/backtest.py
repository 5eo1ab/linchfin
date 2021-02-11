from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries, Weight
from linchfin.common.calc import calc_portfolio_return, calc_daily_returns


class BackTestConfig:
    pass


class BackTestRunner:
    def __init__(self, portfolio: Portfolio, config: BackTestConfig):
        self.step = 0
        self.prev_value = None
        self._value = None
        self.model_portfolio = Portfolio(weights=portfolio.weights)
        self.current_portfolio = Portfolio(weights=portfolio.weights)
        self.acc_trading_values = 0
        self.config = config

    def __iter__(self):
        return self

    def __next__(self):
        self.calc_current_portfolio()
        self.acc_trading_values += self.calc_trading_values()
        return self.step, self.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.prev_value = self._value
        self._value = value

    def calc_trading_values(self):
        return (self.current_portfolio.to_series() * self.value.loc['Adj Close'] * self.value.loc['Volume']).sum()

    def calc_current_portfolio(self):
        if self.prev_value is not None:
            changes = (1 + (self.value.loc['Adj Close'] - self.prev_value.loc['Adj Close']) / self.value.loc['Adj Close'])
            new_weights = self.current_portfolio.to_series() * changes
            new_weights = new_weights / new_weights.sum()
            self.current_portfolio.set_weights(new_weights)
            print(self.current_portfolio.to_series())
            return
        return

    def check_rebalancing_condition(self):
        pass


class BackTestSimulator:
    def run(self, portfolio: Portfolio, daily_returns: TimeSeries):
        portfolio_yield = calc_portfolio_return(portfolio=portfolio, daily_returns=daily_returns)
        return portfolio_yield

    def iter_runner(self, runner: BackTestRunner, time_series: TimeSeries):
        for i, row in time_series.iterrows():
            runner.step = i
            runner.value = row
            k = next(runner)
            print(k)


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader
    weights = {
        'SKYY': Weight('0.4'),
        'OIH': Weight('0.3'),
        'GUNR': Weight('0.3')}

    _port = Portfolio(weights=weights)
    backtester = BackTestSimulator()

    data_reader = DataReader(start='2019/01/01', end='2020/09/01')
    ts = data_reader.get_price(symbols=list(_port.weights.keys()))
    # ts = data_reader.get_adj_close_price(symbols=list(_port.weights.keys()))
    # daily_returns = calc_daily_returns(time_series=ts)
    # backtester.run(portfolio=_port, daily_returns=daily_returns)

    backtest_runner = BackTestRunner(portfolio=_port)
    backtester.iter_runner(runner=backtest_runner, time_series=ts)
