from typing import Union
import numpy as np
import pandas as pd
from .dataclasses.value_types import Metric, Feature


CorrValueType = Union[Feature, pd.DataFrame]


class Encoder:
    @classmethod
    def encode(cls, data: Feature or Metric) -> Metric:
        raise NotImplementedError("Need to be implemented")


class CorrelationEncoder(Encoder):
    @classmethod
    def encode(cls, corr: CorrValueType) -> Metric:
        if isinstance(corr, pd.DataFrame):
            corr = Feature(name='corr', value=corr)
        encoded_value = np.sqrt(np.divide((1 - corr.value), 2))
        return Metric(name='dist', value=encoded_value)
