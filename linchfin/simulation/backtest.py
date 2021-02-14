import math
from datetime import timedelta
from dataclasses import dataclass, field
from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries, Weight
from linchfin.common.calc import calc_portfolio_return
from linchfin.models.template import ABCModelTemplate
from linchfin.models.hrp import HierarchyRiskParityModel


@dataclass
class BackTestConfig:
    acc_trading_values_threshold: float = field(default=50000000000)


class BackTestIterator:
    def __init__(self, runner: 'BackTestRunner', time_series_iter):
        self.step = 0
        self.runner = runner
        self.acc_trading_values = 0
        self.log_acc_return = 0
        self.time_series_iter = time_series_iter
        self.idx = None
        self._value = None
        self.prev_value = None

    def __next__(self):
        self.step += 1
        self.idx, self.value = next(self.time_series_iter)
        self.calc_current_portfolio()
        self.acc_trading_values += self.calc_trading_values()
        return self.idx, self

    @property
    def acc_return(self):
        return math.exp(self.log_acc_return)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.prev_value = self._value
        self._value = value

    @property
    def is_rebalancing_condition_met(self):
        return self.acc_trading_values > self.runner.config.acc_trading_values_threshold

    def calc_trading_values(self):
        return (self.runner.current_portfolio.to_series() * self.value.loc['Adj Close'] * self.value.loc['Volume']).sum()

    def calc_current_portfolio(self):
        if self.prev_value is not None:
            changes = (1 + (self.value.loc['Adj Close'] - self.prev_value.loc['Adj Close']) / self.value.loc['Adj Close'])
            new_weights = self.runner.current_portfolio.to_series() * changes
            self.log_acc_return += math.log(new_weights.sum())
            new_weights = new_weights / new_weights.sum()
            self.runner.current_portfolio.set_weights(new_weights)
            return
        return


class BackTestRunner:
    def __init__(self, model: ABCModelTemplate, config: BackTestConfig = None):
        if config is None:
            config = BackTestConfig()

        self.prev_value = None
        self._value = None
        self._iterator = None
        self.model = model
        portfolio = model.run()
        print("INIT PORT", portfolio.to_series())
        self.model_portfolio = Portfolio(weights=portfolio.weights)
        self.current_portfolio = Portfolio(weights=portfolio.weights)
        self.config = config

    def __iter__(self):
        self._iterator = BackTestIterator(runner=self, time_series_iter=self.time_series.iterrows())
        return self._iterator

    def __call__(self, time_series: TimeSeries):
        self.time_series = time_series
        return self

    def do_rebalancing(self, **kwargs):
        # TODO calc portfolio based on time_series
        _start = self._iterator.idx - timedelta(days=90)
        _end = self._iterator.idx
        self.model.start = _start.strftime("%Y-%m-%d")
        self.model.end = _end.strftime("%Y-%m-%d")
        _port = self.model.run()
        print("NEW_PORT", _port.to_series())
        lr = 0.5
        cur_weights = self.model_portfolio.to_series()
        new_weights = _port.to_series()
        adaptive_weights = (cur_weights + lr * (new_weights - cur_weights)).loc[cur_weights.index]
        _port.set_weights(weights=adaptive_weights)
        self.update_portfolio(portfolio=_port)

    def update_portfolio(self, portfolio: Portfolio):
        self.model_portfolio = Portfolio(weights=portfolio.weights)
        self.current_portfolio = Portfolio(weights=portfolio.weights)


class BackTestSimulator:
    def run(self, portfolio: Portfolio, daily_returns: TimeSeries):
        portfolio_yield = calc_portfolio_return(portfolio=portfolio, daily_returns=daily_returns)
        return portfolio_yield

    def iter_runner(self, runner: BackTestRunner, time_series: TimeSeries):
        for idx, runner_iter in runner(time_series):
            if runner_iter.is_rebalancing_condition_met:
                print("REB", idx, runner_iter.acc_trading_values)
                print("SUMMARY", idx, runner_iter.acc_return)
                print('-' * 30)
                runner_iter.acc_trading_values = 0

                if runner_iter.idx.year >= 2020 and runner_iter.idx.month == 2:
                    runner.do_rebalancing()


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader
    weights = {
        'SKYY': Weight('0.4'),
        'OIH': Weight('0.3'),
        'GUNR': Weight('0.3')}

    _port = Portfolio(weights=weights)
    backtester = BackTestSimulator()

    start, end = '2019/01/01', '2020/01/01'
    data_reader = DataReader(start='2020/01/01', end='2021/01/01')

    symbols = ['MSFT', 'KO', 'PG', 'LULU', 'NKE', 'NVDA']
    ts = data_reader.get_price(symbols=symbols)
    hrp_model = HierarchyRiskParityModel(asset_universe=symbols, start=start, end=end)
    backtest_config = BackTestConfig()
    backtest_runner = BackTestRunner(model=hrp_model, config=backtest_config)
    backtester.iter_runner(runner=backtest_runner, time_series=ts)
