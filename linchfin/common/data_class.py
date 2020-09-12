from dataclasses import dataclass, field
from typing import List, Dict



@dataclass
class AssetClass:
    asset_class_id: str
    asset_class_name: str


@dataclass
class Asset:
    asset_id: str
    asset_name: str
    asset_class: AssetClass


@dataclass
class AssetUniverse:
    universe_id: str
    assets: List[Asset]


@dataclass
class Portfolio:
    portfolio_id: str
    assets: Dict[str, float] = field(default_factory=dict)

    def set_asset(self, asset: Asset, weight: float):
        if asset.asset_id in self.assets:
            raise RuntimeError("Asset already exist")
        self.assets[asset.asset_id] = weight

    def is_valid(self):
        if not round(sum(self.assets.values()), 4) == 1:
            return False
        return True
