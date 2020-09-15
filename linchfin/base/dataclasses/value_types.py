from dataclasses import dataclass
import numpy as np
from decimal import Decimal


@dataclass
class Feature:
    name: str
    value: np.ndarray


@dataclass
class Metric:
    name: str
    value: np.ndarray


class Weight(Decimal):
    pass
