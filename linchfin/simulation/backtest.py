from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import TimeSeries, Weight
from linchfin.common.calc import calc_portfolio_yield


class BackTestSimulator:
    def run(self, portfolio: Portfolio, daily_yield: TimeSeries):
        portfolio_yield = calc_portfolio_yield(portfolio=portfolio, daily_yield=daily_yield)
        return portfolio_yield


if __name__ == '__main__':
    from linchfin.data_handler.reader import DataReader
    from linchfin.data_handler.wrangler import DataWrangler

    weights = {
        'JDST': Weight('0.13283863778299764835111318461713381111621856689453125'),
        'DUST': Weight('0.13283863778299764835111318461713381111621856689453125'),
        'JNUG': Weight('0.133438073337116713812378065995289944112300872802734375'),
        'NUGT': Weight('0.0701666866303975178542629009825759567320346832275390625'),
        'GDXJ': Weight('0.0701666866303975178542629009825759567320346832275390625'),
        'SGDM': Weight('0.035410889212107880819058181032232823781669139862060546875'),
        'RING': Weight('0.035410889212107880819058181032232823781669139862060546875'),
        'GDX': Weight('0.04324006025578529255337656422852887772023677825927734375'),
        'TAN': Weight('0.02571939632182819457373312843628809787333011627197265625'),
        'SKYY': Weight('0.02571939632182819457373312843628809787333011627197265625'),
        'OIH': Weight('0.038697493599623655757824280954082496464252471923828125'),
        'IGF': Weight('0.038697493599623655757824280954082496464252471923828125'),
        'ACWV': Weight('0.0383184102632821155243192379202810116112232208251953125'),
        'SMH': Weight('0.0197456481130713346061611446202732622623443603515625'),
        'IXN': Weight('0.0197456481130713346061611446202732622623443603515625'),
        'URTH': Weight('0.034537437896782270663198488591660861857235431671142578125'),
        'VT': Weight('0.034537437896782270663198488591660861857235431671142578125'),
        'ACWI': Weight('0.035140928888262860929625475137072498910129070281982421875'),
        'IXC': Weight('0.0178150740709680059647990191251665237359702587127685546875'),
        'GUNR': Weight('0.0178150740709680059647990191251665237359702587127685546875')}
    _port = Portfolio(_weights=weights)
    backtester = BackTestSimulator()

    data_reader = DataReader(start='2019/01/01', end='2020/09/01')
    data_wrangler = DataWrangler()
    ts = data_reader.get_adj_close_price(symbols=list(_port.weights.keys()))
    yield_ts = data_wrangler.calc_daily_yield(ts)
    backtester.run(portfolio=_port, daily_yield=yield_ts)
