from dataclasses import dataclass, field
from collections import OrderedDict
from typing import List, Dict, OrderedDict as OrderedDictType
from uuid import uuid4
import pandas as pd

from .value_types import Weight


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
    asset_id: str = field(default_factory=uuid4)
    asset_name: str = field(default='')
    asset_class: AssetClass = field(default_factory=AssetClass)


@dataclass
class AssetUniverse(Entity):
    universe_id: str = field(default_factory=uuid4)
    assets: OrderedDictType[str, Asset] = field(default_factory=OrderedDict)

    def __post_init__(self):
        if isinstance(self.assets, list):
            asset_dic = OrderedDict()
            for _asset in self.assets:
                asset_dic[_asset.asset_name] = _asset
            self.assets = asset_dic
        elif isinstance(self.assets, OrderedDict):
            pass
        else:
            raise TypeError("Unsupported Assets to initialize universe")

    @property
    def symbols(self):
        return [_asset.asset_name for _asset in self.assets.values()]

    def append(self, asset: Asset):
        self.assets[asset.asset_id] = asset

    def pop(self, asset: str or Asset):
        if isinstance(asset, Asset):
            self.assets.pop(asset.asset_id)
        else:
            self.assets.pop(asset)


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
        weights = OrderedDict()
        for asset_id, _asset in self.asset_universe.assets.items():
            print(asset_id)
            if asset_id in self._weights:
                raise KeyError(f"asset name is conflicted, {_asset}")
            weights[_asset.asset_name] = self._weights[asset_id]
        return weights

    def set_weights(self, weights: Dict[str, Weight] or pd.Series):
        for k, v in weights.items():
            _asset = self.asset_universe.assets[str(k)]
            self._weights[_asset.asset_id] = Weight(v)

    def is_valid(self):
        if not round(sum(self.weights.values()), 4) == 1.0:
            return False
        return True
