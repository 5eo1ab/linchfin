from dataclasses import dataclass, field
from collections import OrderedDict
from typing import OrderedDict as Dict
from linchfin.base.dataclasses.entities import Cluster, Asset


@dataclass
class Factor:
    name: str
    neighbors: Dict = field(default_factory=OrderedDict)
    conditional_prob: Dict = field(default_factory=OrderedDict)

    def register_node(self, factor):
        self.neighbors[factor.name] = factor

    @classmethod
    def build(cls, node: Cluster):
        factor = cls(name='')
        if isinstance(node, Cluster):
            factor.name = node.name
            for _leaf in node.elements:
                factor.register_node(cls.build(_leaf))

            for _leaf in factor.neighbors.values():
                factor.conditional_prob[_leaf.name] = 1 / len(factor.neighbors)
        elif isinstance(node, Asset):
            factor.name = node.code
            factor.conditional_prob[factor.name] = 1
        return factor


@dataclass
class MarkovFactor(Factor):
    pass


@dataclass
class BayesFactor(Factor):
    pass


if __name__ == '__main__':
    from linchfin.metadata import ETF_SECTORS
    from linchfin.core.clustering.sectors import SectorTree

    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    markov_network = MarkovFactor.build(sector_tree.root)
    bayes_network = BayesFactor.build(sector_tree.root)
    a = MarkovFactor('f1')
    b = MarkovFactor('f2')
    a.register_node(b)
