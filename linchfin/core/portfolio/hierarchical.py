from typing import List

import numpy as np
import pandas as pd
import scipy.cluster.hierarchy as sch
from matplotlib import pyplot as plt

from linchfin.base.dataclasses.entities import (
    Asset, AssetUniverse, Portfolio, Cluster
)
from linchfin.base.dataclasses.value_types import Metric, Feature
from linchfin.core.clustering.hierarchical import HierarchicalCorrCluster


class HierarchyRiskParityEngine(HierarchicalCorrCluster):
    def __init__(self, asset_universe, estimation=True):
        super().__init__(estimation=estimation)
        self.asset_universe = asset_universe

    def run(self, corr: Feature) -> Portfolio:
        portfolio = Portfolio(asset_universe=self.asset_universe)
        dist = self.distance_encoder.encode(corr=corr)

        linkage = self.calc_linkage(distance=dist)
        sort_ix = self.get_quansi_diag(linkage)
        weights = self.get_recursive_bisect(corr=corr, sort_ix=sort_ix)

        weights.index = corr.columns[weights.index]
        portfolio.set_weights(weights)
        return portfolio

    def get_clusters(self, distance: Metric) -> List[Cluster]:
        links = self.calc_linkage(distance=distance)
        return [Cluster(elements=[int(p1), int(p2)], d=dist, size=int(size))
                for p1, p2, dist, size in links]

    def get_recursive_bisect(self, corr: Feature, sort_ix: list):
        w = pd.Series(1, index=sort_ix)
        c_items = [sort_ix]

        while len(c_items) > 0:
            c_items = [
                i[j:k]
                for i in c_items
                for j, k in ((0, len(i) // 2), (len(i) // 2, len(i)))
                if len(i) > 1
            ]

            for i in range(0, len(c_items), 2):
                c_item0 = c_items[i]
                c_item1 = c_items[i + 1]
                c_var0 = self.get_cluster_var(corr, c_item0)
                c_var1 = self.get_cluster_var(corr, c_item1)
                alpha = 1 - c_var0 / (c_var0 + c_var1)
                w[c_item0] *= alpha
                w[c_item1] *= 1 - alpha
        return w

    def get_cluster_var(self, corr: Feature, c_items):
        _corr_value = corr.value.loc[corr.columns[c_items], corr.columns[c_items]]
        w_ = self.get_ivp(_corr_value).reshape(-1, 1)
        c_var = np.dot(np.dot(w_.T, _corr_value), w_)[0, 0]
        return c_var

    def get_ivp(self, cov: pd.DataFrame, **kwargs):
        ivp = 1. / np.diag(cov)
        return ivp / ivp.sum()


if __name__ == '__main__':
    from linchfin.base.dataclasses.value_types import AssetCode

    _p = np.array(
        [
            [1, 0.7, 0.2],
            [0.7, 1, -0.2],
            [0.2, -0.2, 1]
        ]
    )

    _asset_universe = AssetUniverse()
    for idx, _ in enumerate(_p):
        _asset_universe.append(Asset(code=AssetCode(idx)))

    _p = Feature(name='correlation', value=pd.DataFrame(_p))
    hcp = HierarchyRiskParityEngine(asset_universe=_asset_universe)
    hcp.show_dendrogram(corr=_p)
    _portfolio = hcp.run(corr=_p)
    print(_portfolio.is_valid())
    print(_portfolio.weights)
    print(_portfolio.show_summary())
