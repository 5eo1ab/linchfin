from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Iterable, Dict


@dataclass
class IterValueMixin:
    value: pd.DataFrame

    def iterrows(self):
        return self.value.iterrows()

    def __getitem__(self, item):
        return self.value.__getitem__(key=item)


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


class Prices(pd.Series):
    pass


class TimeSeries(pd.DataFrame):
    def pivot(self, *args, **kwargs) -> TimeSeries:
        ts = TimeSeries(super().pivot(*args, **kwargs), dtype=float)
        ts.index = pd.to_datetime(ts.index)
        return ts
