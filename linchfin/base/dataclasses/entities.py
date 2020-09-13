from dataclasses import dataclass, field
from collections import OrderedDict
from typing import Dict, OrderedDict as OrderedDictType
from uuid import uuid4
import pandas as pd

from .value_types import Weight


@dataclass
class AssetClass:
    asset_class_id: str = field(default_factory=uuid4)
    asset_class_name: str = field(default='')


@dataclass
class Asset:
    asset_id: str = field(default_factory=uuid4)
    asset_name: str = field(default='')
    asset_class: AssetClass = field(default_factory=AssetClass)


@dataclass
class AssetUniverse:
    universe_id: str = field(default_factory=uuid4)
    assets: OrderedDictType[str, Asset] = field(default_factory=OrderedDict)

    def append(self, asset: Asset):
        self.assets[asset.asset_id] = asset

    def pop(self, asset: str or Asset):
        if isinstance(asset, Asset):
            self.assets.pop(asset.asset_id)
        else:
            self.assets.pop(asset)


@dataclass
class Cluster:
    e1: int
    e2: int
    d: float
    size: int


@dataclass
class Portfolio:
    portfolio_id: str = field(default_factory=uuid4)
    weights: Dict[str, Weight] = field(default_factory=dict)
    asset_universe: AssetUniverse = field(default_factory=AssetUniverse)

    def set_weights(self, weights: Dict[str, Weight] or pd.Series):
        for k, v in weights.items():
            _asset = self.asset_universe.assets[str(k)]
            self.weights[_asset.asset_id] = Weight(v)

    def is_valid(self):
        if not round(sum(self.weights.values()), 4) == 1.0:
            return False
        return True
