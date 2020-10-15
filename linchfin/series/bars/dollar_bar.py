import pandas as pd


def find_loc(df, dates):
    marks = []
    for date in dates:
        marks.append(df.index.get_loc(date))
    return marks


def get_dollar_bars(series: pd.Series, threshold=227362680000):
    def get_dollar_iter():
        acc = 0
        for i, _value in series.iteritems():
            acc += _value
            if acc > threshold:
                yield i, _value
                acc = 0

    df = pd.DataFrame(list(get_dollar_iter()), columns=['index', 'dollar_value'])
    return df.set_index('index')


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader

    reader = DataReader()
    ts = reader.get_trading_value(symbols=['AAPL'])
    db = get_dollar_bars(series=ts['AAPL'])

    from matplotlib import pyplot as plt
    ts.plot(linestyle='-', markevery=find_loc(ts, db.index), marker='o', markerfacecolor='black')
    plt.show()
