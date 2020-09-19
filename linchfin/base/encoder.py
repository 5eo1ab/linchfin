import numpy as np

from .dataclasses.value_types import Metric, Feature


class Encoder:
    @classmethod
    def encode(cls, data: Feature or Metric) -> Metric:
        raise NotImplementedError("Need to be implemented")


class CorrelationEncoder(Encoder):
    @classmethod
    def encode(cls, data: Feature) -> Metric:
        encoded_value = np.sqrt(np.divide((1 - data.value), 2))
        return Metric(name='dist', value=encoded_value)
