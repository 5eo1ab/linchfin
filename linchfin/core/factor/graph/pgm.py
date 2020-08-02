from dataclasses import dataclass, field
from typing import List


@dataclass
class Factor:
    name: str
    neighbors = dict()

    def register_node(self, factor):
        self.neighbors[factor.name] = factor


@dataclass
class MarkovFactor(Factor):
    next: List[Factor] = None
    conditional_prob = dict()


@dataclass
class BayesFactor(Factor):
    next: List[Factor] = None


if __name__ == '__main__':
    a = MarkovFactor('f1')
    b = MarkovFactor('f2')
    a.register_node(b)
