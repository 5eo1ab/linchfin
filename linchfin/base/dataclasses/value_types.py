from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from collections import OrderedDict
import numpy as np
import pandas as pd


@dataclass
class IterValueMixin:
    value: pd.DataFrame

    def iterrows(self):
        return self.value.iterrows()


@dataclass
class Feature(IterValueMixin, object):
    name: str
    value: pd.DataFrame

    def __post_init__(self):
        if isinstance(self.value, np.ndarray):
            self.value = pd.DataFrame(self.value)

    @property
    def columns(self):
        return self.value.columns


@dataclass
class Metric(IterValueMixin, object):
    name: str
    value: np.ndarray


class Weights(OrderedDict):
    pass


class Weight(Decimal):
    pass


class Prices(pd.Series):
    pass


class TimeSeries(pd.DataFrame):
    pass


class AssetId(UUID):
    pass


class AssetCode(str):
    pass
