from linchfin.base.dataclasses.entities import Asset, AssetUniverse
from typing import Iterable, List


class AssetFilter:
    def __init__(self, includes=None, excludes=None, *args, **kwargs):
        self.includes = includes or []
        self.excludes = excludes or []
        assert not set(self.includes).intersection(self.excludes), "Intersection between includes and excludes"

    def filter(self, asset_universe: Iterable) -> AssetUniverse:
        filtered_assets = [asset for asset in asset_universe if self.is_filtered(asset=asset)]
        return AssetUniverse(assets=filtered_assets)

    def check(self, asset: Asset):
        return self.is_filtered(asset) and not self.is_excluded(asset)

    def is_filtered(self, asset: Asset):
        _included = True
        if self.includes:
            _included = asset.name in self.includes
        return _included

    def is_excluded(self, asset: Asset):
        _excluded = False
        if self.excludes:
            _excluded = asset.name not in self.excludes
        return _excluded


class AssetClassFilter(AssetFilter):
    def is_filtered(self, asset: Asset):
        _included = True
        if self.includes:
            _included =\
                bool(sum([_in.lower() in asset.asset_class.name.lower() for _in in self.includes]))
        return _included

    def is_excluded(self, asset: Asset):
        _excluded = False
        if self.excludes:
            _excluded =\
                bool(sum([_ex.lower() in asset.asset_class.name.lower() for _ex in self.excludes]))
        return _excluded


class AssetFilterBackends:
    def __init__(self, filters: List[AssetFilter]):
        self.filters = filters

    def filter(self, asset_universe: Iterable) -> AssetUniverse:
        filtered_assets = []

        for _asset in asset_universe:
            filter_results = [True for _filter in self.filters if _filter.check(_asset)]

            if sum(filter_results):
                filtered_assets.append(_asset)
        return AssetUniverse(assets=filtered_assets)


if __name__ == '__main__':
    from linchfin.core.clustering.sectors import SectorTree, ETF_SECTORS

    etf_sector_tree = SectorTree(ETF_SECTORS)
    filters = [
        AssetFilter(includes=['SPY']),
        AssetClassFilter(excludes=['Inverse', 'Forex'])
    ]
    filter_backends = AssetFilterBackends(filters=filters)
    a = filter_backends.filter(etf_sector_tree.assets)
    print([i.asset_class.name for i in a])
