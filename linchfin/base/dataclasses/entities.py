from dataclasses import dataclass, field
from collections import OrderedDict
from typing import List, Dict, OrderedDict as OrderedDictType
from uuid import uuid4
import pandas as pd

from .value_types import Weight, AssetId, AssetName


@dataclass
class Entity:
    def __post_init__(self):
        self.extra = OrderedDict()


@dataclass
class AssetClass(Entity):
    asset_class_id: str = field(default_factory=uuid4)
    asset_class_name: str = field(default='')


@dataclass
class Asset(Entity):
    asset_id: AssetId = field(default_factory=uuid4)
    asset_name: str = field(default='')
    asset_class: AssetClass = field(default_factory=AssetClass)


@dataclass
class AssetUniverse(Entity):
    universe_id: str = field(default_factory=uuid4)
    assets: OrderedDictType[AssetId, Asset] = field(default_factory=OrderedDict)
    asset_name_map: OrderedDictType = field(init=False)

    def __post_init__(self):
        if isinstance(self.assets, list):
            asset_dic = OrderedDict()
            for _asset in self.assets:
                asset_dic[_asset.asset_id] = _asset
            self.assets = asset_dic
        elif isinstance(self.assets, OrderedDict):
            pass
        else:
            raise TypeError("Unsupported Assets to initialize universe")
        self.asset_name_map = OrderedDict()
        for asset_id, _asset in self.assets.items():
            self.asset_name_map[_asset.asset_name] = asset_id

    @property
    def symbols(self):
        return [_asset.asset_name for _asset in self.assets.values()]

    def get_asset(self, name: AssetName) -> Asset:
        asset_id = self.get_asset_id(name=name)
        return self.assets[asset_id]

    def get_asset_id(self, name: AssetName) -> AssetId:
        name = str(name)
        return self.asset_name_map[name]

    def append(self, asset: Asset):
        self.assets[asset.asset_id] = asset
        self.asset_name_map[asset.asset_name] = asset.asset_id

    def pop(self, asset: str or Asset):
        if isinstance(asset, Asset):
            self.assets.pop(asset.asset_id)
        else:
            self.assets.pop(asset)
        self.asset_name_map.pop(asset.asset_name)


@dataclass
class Cluster(Entity):
    name: str = field(default='')
    elements: List = field(default_factory=list)
    d: float = field(default=0)
    size: int = field(default=0)


@dataclass
class Portfolio(Entity):
    portfolio_id: str = field(default_factory=uuid4)
    _weights: Dict[str, Weight] = field(default_factory=dict)
    asset_universe: AssetUniverse = field(default_factory=AssetUniverse)

    @property
    def weights(self):
        return self._weights

    def set_weights(self, weights: Dict[str, Weight] or pd.Series):
        for _asset_name, _w in weights.items():
            if _asset_name in self._weights:
                raise KeyError(f"asset name is conflicted, {_asset_name}")

            _asset = self.asset_universe.get_asset(name=_asset_name)
            self._weights[_asset.asset_name] = Weight(_w)

    def is_valid(self):
        if not round(sum(self.weights.values()), 4) == 1.0:
            return False
        return True
