from linchfin.base.dataclasses.entities import Portfolio
from linchfin.base.dataclasses.value_types import Weight, Weights, Prices
import random
from collections import OrderedDict
from math import gcd


class RuleEngine:
    @classmethod
    def run(cls, portfolio: Portfolio, min_cutoff=0.05) -> Weights:
        updated_weights = portfolio.weights.copy()
        cutoff = Weight(100 * min_cutoff)

        if 100 % cutoff:
            raise ValueError(f"Can't apply indivisible cutoff({min_cutoff})")

        accept_ratios = OrderedDict()
        for _asset_code, _weight in portfolio.weights.items():
            w = Weight(_weight * 100)
            updated_weights[_asset_code] = (w // cutoff) * cutoff
            accept_ratios[_asset_code] = float((w % cutoff) / cutoff)

        sum_of_weights = sum(updated_weights.values())
        if not sum_of_weights:
            raise RuntimeError(f"All weight is smaller than cutoff({cutoff}%)")

        while sum_of_weights != 100:
            for _asset_code, _weight in updated_weights.items():
                sum_of_weights = sum(updated_weights.values())
                if sum_of_weights == 100:
                    break

                if random.random() <= accept_ratios[_asset_code]:
                    updated_weights[_asset_code] += cutoff
                    accept_ratios[_asset_code] = 0
        weights = cls.to_representation(weights=updated_weights)
        return weights

    @classmethod
    def to_representation(cls, weights):
        weight_list = list(weights.items())
        for _asset_code, _weight in weight_list:
            weights[_asset_code] = round(_weight * Weight(0.01), 3)
            if _weight == 0:
                weights.pop(_asset_code)
        return weights

    @staticmethod
    def calc_recommended_quantity(portfolio: Portfolio, close_price: Prices):
        def multiple_gcd(array):
            while len(array) > 1:
                array.append(gcd(array.pop(), array.pop()))
            return array[0]

        asset_close_price = close_price[portfolio.symbols]
        optimal_qty = portfolio.to_series() * asset_close_price.sum() / asset_close_price
        available_qty = (optimal_qty * 10).round().astype(int)
        gcd_value = multiple_gcd(available_qty.to_list())
        psudo_optimal_qty = available_qty / gcd_value
        return psudo_optimal_qty

    def calc_recommended_cash(self, portfolio: Portfolio, close_price: Prices):
        psudo_optimal_qty = self.calc_recommended_quantity(portfolio=portfolio, close_price=close_price)
        return (psudo_optimal_qty * close_price).sum().astype(int)

    def calc_recommended_quantity_diff(self, portfolio: Portfolio, close_price: Prices):
        recommended_qty = self.calc_recommended_quantity(portfolio=portfolio, close_price=close_price)
        portfolio_valuation = recommended_qty * close_price
        return portfolio.to_series() - portfolio_valuation / portfolio_valuation.sum()

    def calc_minimum_quantity(self, portfolio: Portfolio, close_price: Prices):
        psudo_optimal_qty = self.calc_recommended_quantity(portfolio=portfolio, close_price=close_price)
        return (psudo_optimal_qty / psudo_optimal_qty.min()).astype(int)

    def calc_minimum_cash(self, portfolio: Portfolio, close_price: Prices):
        minimum_qty = self.calc_minimum_quantity(portfolio=portfolio, close_price=close_price)
        return (minimum_qty * close_price).sum().astype(int)

    def calc_minimum_quantity_diff(self, portfolio: Portfolio, close_price: Prices):
        minimum_qty = self.calc_minimum_quantity(portfolio=portfolio, close_price=close_price)
        portfolio_valuation = minimum_qty * close_price
        return portfolio.to_series() - portfolio_valuation / portfolio_valuation.sum()


if __name__ == '__main__':
    _weights = {
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
    _port = Portfolio(weights=_weights)

    rule_engine = RuleEngine()
    print(_port.weights)
    weights = rule_engine.run(portfolio=_port, min_cutoff=0.1)
    print(weights)
