from dataclasses import dataclass
import numpy as np
from decimal import Decimal
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


class Weight(Decimal):
    pass


class TimeSeries(pd.DataFrame):
    pass
