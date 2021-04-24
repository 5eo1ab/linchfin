from dataclasses import dataclass
import numpy as np
import pandas as pd


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
    pass
