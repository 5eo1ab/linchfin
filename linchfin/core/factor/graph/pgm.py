import pandas as pd
from dataclasses import dataclass, field
from collections import OrderedDict
from typing import OrderedDict as Dict, List
from linchfin.base.dataclasses.entities import Cluster, Asset


class Query:
    def __init__(self, cpd: pd.DataFrame, vars=None):
        self.cpd = cpd
        if not vars:
            vars = []
        self.vars = vars

    def __call__(self, **kwargs):
        vars_dic = OrderedDict()

        for v in self.vars:
            vars_dic[v] = None
        vars_dic.update(kwargs)

        indexer_params = []
        for k, v in vars_dic.items():
            if v is None:
                indexer_params.append(slice(None))
            else:
                indexer_params.append([f"{k}{v}"])

        return self.cpd.loc.__getitem__(tuple(indexer_params))


@dataclass
class Factor:
    name: str
    neighbors: Dict = field(default_factory=OrderedDict)
    conditional_prob: Dict = field(default_factory=OrderedDict)
    vars: List = field(default_factory=list)

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

    def infer_prob(self, name, init_prob=1):
        for _factor_name, _factor in self.neighbors.items():
            if name == _factor:
                pass

    def query(self, cpd: pd.DataFrame, **kwargs):
        q = Query(cpd=cpd, vars=self.vars)
        return q(**kwargs)


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
    a = MarkovFactor('f1', vars=['A', 'B', 'C'])
    b = MarkovFactor('f2')
    a.register_node(b)

    import pandas as pd

    values = [['A0', 'A1'], ['B0', 'B1'], ['C0', 'C1']]
    cpd = pd.DataFrame([(11, 1, 1)], index=pd.MultiIndex.from_product(values),
                       columns=['volume', 'rate', 'inflation'])
    a.query(cpd=cpd, A=0, B=1)

