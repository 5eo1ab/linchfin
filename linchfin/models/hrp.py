from linchfin.models.template import ABCModelTemplate
from linchfin.core.portfolio.hierarchical import HierarchyRiskParityEngine
from linchfin.base.dataclasses.entities import AssetUniverse
from linchfin.base.dataclasses.value_types import Feature
from linchfin.common.calc import calc_corr


class HierarchyRiskParityModel(ABCModelTemplate):
    engine_class = HierarchyRiskParityEngine

    def __init__(self, asset_universe: AssetUniverse, start, end, period='D'):
        self._engine = None
        self.asset_universe = asset_universe
        self.init_engine()
        self.start = start
        self.end = end
        self.period = period

    def init_engine(self, **kwargs):
        kwargs.update(self.get_init_engine_kwargs())
        self._engine = self.engine_class(kwargs)

    def get_init_engine_kwargs(self):
        return {
            'asset_universe': self.asset_universe
        }

    def run(self, *args, **kwargs):
        features = self.get_features()
        return self._engine.run(features)

    def get_features(self) -> Feature:
        ts = self.get_time_series(symbols=self.asset_universe.symbols,
                                  start=self.start, end=self.end, period=self.period)
        corr_val = calc_corr(ts)
        return Feature(name='corr', value=corr_val)


if __name__ == '__main__':
    from linchfin.base.dataclasses.entities import Asset, AssetUniverse

    symbols = [
        'MSFT', 'KO', 'PG', 'LULU', 'NKE', 'NVDA'
    ]

    universes = AssetUniverse(assets=[Asset(code=s) for s in symbols])
    a = HierarchyRiskParityModel(asset_universe=universes, start='2020-01-01',
                                 end='2021-01-14')
    port = a.run()
    print(port)
