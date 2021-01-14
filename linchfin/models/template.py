from abc import ABCMeta, abstractmethod
from linchfin.data_handler.reader import DataReader
from linchfin.common.calc import calc_corr, calc_daily_returns, calc_monthly_returns, calc_annal_returns


class ABCModelTemplate(metaclass=ABCMeta):
    engine_class = None
    data_reader_class = DataReader
    return_period_calc = {
        'D': calc_daily_returns,
        'M': calc_monthly_returns,
        'Y': calc_annal_returns,
    }

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    def init_engine(self, **kwargs):
        pass

    def get_time_series(self, start, end, symbols=None, period='D'):
        if not symbols:
            symbols = []

        reader = self.data_reader_class(start=start, end=end)
        clos = reader.get_adj_close_price(symbols=symbols)
        calc_func = self.return_period_calc[period]
        return calc_func(clos)
