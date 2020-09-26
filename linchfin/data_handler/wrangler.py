import pandas as pd
from typing import Optional
from linchfin.base.dataclasses.value_types import TimeSeries, Feature


DAILY = 1
MONTHLY = 21
ANNUAL = 252


class DataWrangler:
    @staticmethod
    def calc_daily_yield(timeseries: TimeSeries) -> TimeSeries:
        return timeseries.pct_change(periods=DAILY)

    @staticmethod
    def calc_monthly_yield(timeseries: TimeSeries) -> TimeSeries:
        return timeseries.pct_change(periods=MONTHLY)

    @staticmethod
    def calc_annal_yield(timeseries: TimeSeries) -> TimeSeries:
        return timeseries.pct_change(periods=ANNUAL)

    @staticmethod
    def calc_corr(timeseries: TimeSeries, method='pearson', min_periods: Optional[int] = 1):
        cov = timeseries.corr(method=method, min_periods=min_periods)
        return cov

    @staticmethod
    def calc_cov(timeseries: TimeSeries,
                 min_periods: Optional[int] = None, degree_of_freedom: Optional[int] = None) -> pd.DataFrame:
        cov = timeseries.cov(min_periods=min_periods, ddof=degree_of_freedom)
        return cov


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader

    reader = DataReader(start='2019-01-01', end='2020-01-01')
    wrangler = DataWrangler()
    timeseries = reader.get_adj_close_price(symbols=['AAPL', 'PIO'])
    monthly_yield = wrangler.calc_monthly_yield(timeseries=timeseries)
    corr = wrangler.calc_corr(timeseries=monthly_yield)
    print(corr)
