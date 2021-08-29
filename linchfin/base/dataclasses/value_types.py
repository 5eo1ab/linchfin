from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Type


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


class TimeSeriesRow(pd.Series):
    @property
    def _constructor(self) -> Type["TimeSeriesRow"]:
        return TimeSeriesRow

    @property
    def _constructor_expanddim(self) -> Type["TimeSeries"]:
        return TimeSeries


class TimeSeries(pd.DataFrame):
    _constructor_sliced: Type[TimeSeriesRow] = TimeSeriesRow

    def pivot(self, *args, **kwargs) -> TimeSeries:
        ts = TimeSeries(super().pivot(*args, **kwargs), dtype=float)
        ts.index = pd.to_datetime(ts.index)
        return ts

    @property
    def _constructor(self) -> Type["TimeSeries"]:
        return TimeSeries
