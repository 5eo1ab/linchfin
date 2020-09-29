from typing import Optional

import pandas as pd

from linchfin.base.dataclasses.value_types import TimeSeries

DAILY = 1
MONTHLY = 21
ANNUAL = 252


class DataWrangler:
    @staticmethod
    def calc_daily_yield(time_series: TimeSeries) -> TimeSeries:
        return time_series.pct_change(periods=DAILY)

    @staticmethod
    def calc_monthly_yield(time_series: TimeSeries) -> TimeSeries:
        return time_series.pct_change(periods=MONTHLY)

    @staticmethod
    def calc_annal_yield(time_series: TimeSeries) -> TimeSeries:
        return time_series.pct_change(periods=ANNUAL)

    @staticmethod
    def calc_corr(time_series: TimeSeries, method='pearson', min_periods: Optional[int] = 1):
        corr = time_series.corr(method=method, min_periods=min_periods)
        return corr

    @staticmethod
    def calc_cov(time_series: TimeSeries,
                 min_periods: Optional[int] = None, degree_of_freedom: Optional[int] = None) -> pd.DataFrame:
        cov = time_series.cov(min_periods=min_periods, ddof=degree_of_freedom)
        return cov


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader

    reader = DataReader(start='2019-01-01', end='2020-01-01')
    wrangler = DataWrangler()
    time_series = reader.get_adj_close_price(symbols=['AAPL', 'PIO'])
    monthly_yield = wrangler.calc_monthly_yield(time_series=time_series)
    corr = wrangler.calc_corr(time_series=monthly_yield)
    print(corr)
