from dataclasses import dataclass
import numpy as np
from decimal import Decimal


@dataclass
class Metric:
    name: str
    value: np.ndarray


class Weight(Decimal):
    pass
