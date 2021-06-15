from typing import List

import pandas_datareader as pdr

from linchfin.base.dataclasses.value_types import TimeSeries

CLOSE = 'Close'
HIGH = 'High'
ADJ_CLOSE = 'Adj Close'
LOW = 'Low'
OPEN = 'Open'
VOLUME = 'Volume'


class DataReader:
    def __init__(self, data_source='yahoo', start=None, end=None):
        self.reader_func = pdr.DataReader
        self.data_source = data_source
        self.start = start
        self.end = end

    def get_trading_value(self, symbols: List[str]) -> TimeSeries:
        return self.get_price(symbols=symbols, apply_func=lambda row: row['Adj Close'] * row['Volume'])

    def get_adj_close_price(self, symbols: List[str]) -> TimeSeries:
        df = self.get_timeseries(symbols=symbols)
        return df[ADJ_CLOSE]

    def get_open_price(self, symbols: List[str]) -> TimeSeries:
        df = self.get_timeseries(symbols=symbols)
        return df[OPEN]

    def get_close_price(self, symbols: List[str]) -> TimeSeries:
        df = self.get_timeseries(symbols=symbols)
        return df[CLOSE]

    def get_traidng_volume(self, symbols: List[str]) -> TimeSeries:
        df = self.get_timeseries(symbols=symbols)
        return df[VOLUME]

    def get_price(self, symbols: List[str], apply_func=None) -> TimeSeries:
        df = self.get_timeseries(symbols=symbols)
        if apply_func:
            df = df.apply(func=apply_func, axis=1)
        return df

    def get_timeseries(self, symbols: List[str]) -> TimeSeries:
        df = self.reader_func(name=symbols, data_source=self.data_source, start=self.start, end=self.end)
        return TimeSeries(df)


class CachedDataReader(DataReader):
    def get_close_price(self, symbols: List[str]) -> TimeSeries:
        pass


if __name__ == "__main__":
    dr = DataReader()
    c = dr.get_adj_close_price(['AAPL', 'PIO'])
    print(c)
    c.cov()
