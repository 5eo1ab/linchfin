import math
import logging
from matplotlib import pyplot as plt
from datetime import timedelta
from dataclasses import dataclass, field
from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries, Weight
from linchfin.common.calc import calc_portfolio_return
from linchfin.models.template import ABCModelTemplate
from linchfin.models.hrp import HierarchyRiskParityModel


logger = logging.getLogger('linchfin')


@dataclass
class BacktestConfig:
    base: float = field(default=0)
    acc_trading_values_threshold: float = field(default=30000000000)
    use_dynamic_rebalancing: bool = field(default=True)
    rebalancing_learing_rate: float = field(default=0.5)
    mode: str = field(default='debug')
    show_plot: bool = field(default=True)
    lookback_period: int = field(default=90)


class BacktestIterator:
    def __init__(self, runner: 'BacktestRunner', time_series_iter):
        self.step = 0
        self.runner = runner
        self.acc_trading_values = 0
        self.log_acc_return = 0
        self.time_series_iter = time_series_iter
        self.idx = None
        self.changes = None
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
            self.changes = (1 + (self.value.loc['Adj Close'] - self.prev_value.loc['Adj Close']) / self.value.loc['Adj Close'])
            new_weights = self.runner.current_portfolio.to_series() * self.changes
            self.log_acc_return += math.log(new_weights.sum())
            new_weights = new_weights / new_weights.sum()
            self.runner.current_portfolio.set_weights(new_weights)
            return
        return


class BacktestRunner:
    def __init__(self, model: ABCModelTemplate, config: BacktestConfig = None):
        if config is None:
            config = BacktestConfig()

        self.prev_value = None
        self._value = None
        self._iterator = None
        self.model = model
        portfolio = model.run()
        self.model_portfolio = Portfolio(weights=portfolio.weights)
        self.current_portfolio = Portfolio(weights=portfolio.weights)
        self.config = config

    def __iter__(self):
        self._iterator = BacktestIterator(runner=self, time_series_iter=self.time_series.iterrows())
        return self._iterator

    def __call__(self, time_series: TimeSeries):
        self.time_series = time_series
        return self

    def do_rebalancing(self, **kwargs):
        # TODO calc portfolio based on time_series
        _start = self._iterator.idx - timedelta(days=self.config.lookback_period)
        _end = self._iterator.idx
        self.model.start = _start.strftime("%Y-%m-%d")
        self.model.end = _end.strftime("%Y-%m-%d")
        _port = self.model.run()
        logger.info(f"port based {self._iterator.idx}\n:{_port.to_series()}")
        lr = self.config.rebalancing_learing_rate
        cur_weights = self.model_portfolio.to_series()
        new_weights = _port.to_series()
        adaptive_weights = (cur_weights + lr * (new_weights - cur_weights)).loc[cur_weights.index]
        _port.set_weights(weights=adaptive_weights)
        self.update_portfolio(portfolio=_port)

    def update_portfolio(self, portfolio: Portfolio):
        self.model_portfolio = Portfolio(weights=portfolio.weights)
        self.current_portfolio = Portfolio(weights=portfolio.weights)


class BacktestSimulator:
    def run(self, portfolio: Portfolio, daily_returns: TimeSeries):
        portfolio_yield = calc_portfolio_return(portfolio=portfolio, daily_returns=daily_returns)
        return portfolio_yield

    def iter_runner(self, runner: BacktestRunner, time_series: TimeSeries):
        acc_returns = TimeSeries()
        weight_changes = TimeSeries()
        rebalancing_indices = []

        for idx, (_ts, runner_iter) in enumerate(runner(time_series)):
            acc_returns = acc_returns.append(TimeSeries({"acc_return": runner_iter.acc_return}, index=[_ts]))
            weight_changes = weight_changes.append(TimeSeries(runner.current_portfolio.weights, index=[_ts]))

            if runner_iter.is_rebalancing_condition_met:
                logger.debug("REB", _ts, runner_iter.acc_trading_values)
                logger.debug("SUMMARY", _ts, runner_iter.acc_return)
                runner_iter.acc_trading_values = 0

                if runner.config.use_dynamic_rebalancing:
                    rebalancing_indices.append(idx)
                    runner.do_rebalancing()

        if runner.config.show_plot:
            plt.figure()
            fig, axes = plt.subplots(nrows=2, ncols=1)
            acc_returns.plot(ax=axes[0], linestyle='-', markevery=rebalancing_indices,
                             marker='x', markerfacecolor='black')
            weight_changes.astype(float).plot(ax=axes[1])
            plt.show()


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader
    Backtester = BacktestSimulator()

    start, end = '2018/01/01', '2020/01/01'
    data_reader = DataReader(start='2019/01/01', end='2021/01/01')

    # symbols = ['MSFT', 'KO', 'PG', 'LULU', 'NKE', 'NVDA']
    symbols = [
        'VTI',
        'XLK', 'XLF', 'XLE', 'XLI', 'XLB', 'XLU',
        'LQD', 'IEF', 'TLT', 'SLV',
        ]
    ts = data_reader.get_price(symbols=symbols)
    hrp_model = HierarchyRiskParityModel(asset_universe=symbols, start=start, end=end)
    Backtest_config = BacktestConfig(base=100000, rebalancing_learing_rate=0.8, lookback_period=250,
                                     acc_trading_values_threshold=30000000000)
    Backtest_runner = BacktestRunner(model=hrp_model, config=Backtest_config)
    Backtester.iter_runner(runner=Backtest_runner, time_series=ts)
