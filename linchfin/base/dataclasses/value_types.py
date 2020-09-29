from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from collections import OrderedDict
import numpy as np
import pandas as pd


@dataclass
class Feature:
    name: str
    value: pd.DataFrame

    def __post_init__(self):
        if isinstance(self.value, np.ndarray):
            self.value = pd.DataFrame(self.value)

    @property
    def columns(self):
        return self.value.columns


@dataclass
class Metric:
    name: str
    value: np.ndarray


class Weights(OrderedDict):
    pass


class Weight(Decimal):
    pass


class TimeSeries(pd.DataFrame):
    pass


class AssetId(UUID):
    pass


class AssetCode(str):
    pass
