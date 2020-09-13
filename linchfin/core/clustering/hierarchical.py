import scipy.cluster.hierarchy as sch
import numpy as np
import pandas as pd
from dataclasses import dataclass
from matplotlib import pyplot as plt
from linchfin.base.dataclasses.entities import (
    Asset, AssetUniverse, Portfolio, Cluster
)
from linchfin.base.dataclasses.value_types import Metric
from linchfin.base.encoder import EuclideanEncoder
from typing import List


@dataclass
class HierarchyCluster(Cluster):
    def __post_init__(self):
        for k, _field in self.__dataclass_fields__.items():
            v = getattr(self, k)
            if not isinstance(v, _field.type):
                setattr(self, k, _field.type(getattr(self, k)))


class HierarchyRiskParityEngine:
    def __init__(self, asset_universe):
        self.asset_universe = asset_universe
        self.distance_encoder = EuclideanEncoder()

    @staticmethod
    def calc_correlation(x: np.array):
        return x.corr()

    @staticmethod
    def calc_covariance(x: np.array):
        return x.cov()

    def run(self, corr: Metric) -> Portfolio:
        portfolio = Portfolio(asset_universe=self.asset_universe)
        dist = self.distance_encoder.encode(data=corr)

        _clusters = self.get_clusters(distance=dist)
        sort_ix = self.get_quansi_diag(_clusters)
        weights = self.get_recursive_bisect(cov=pd.DataFrame(p.value), sort_ix=sort_ix)
        portfolio.set_weights(weights)
        return portfolio

    def get_clusters(self, distance: Metric) -> List[Cluster]:
        links = sch.linkage(distance.value, 'single')
        return [HierarchyCluster(*c) for c in links]

    def get_quansi_diag(self, link):
        last_cluster = link[-1]
        sort_ix = pd.Series([last_cluster.e1, last_cluster.e2])
        num_items = last_cluster.size

        while sort_ix.max() >= num_items:
            sort_ix.index = range(0, sort_ix.shape[0] * 2, 2) # make space
            df0 = sort_ix[sort_ix >= num_items]
            i = df0.index
            j = df0.values - num_items

            current_cluster = link[j.item()]
            sort_ix[i] = current_cluster.e1
            df0 = pd.Series(current_cluster.e2, index=i+1)
            sort_ix = sort_ix.append(df0)
            sort_ix = sort_ix.sort_index()  # re-sort
            sort_ix.index = range(sort_ix.shape[0])  # reindex
        return sort_ix.tolist()

    def get_recursive_bisect(self, cov: pd.DataFrame, sort_ix: list):
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
                c_item1 = c_items[i+1]
                c_var0 = self.get_cluster_var(cov, c_item0)
                c_var1 = self.get_cluster_var(cov, c_item1)
                alpha = 1 - c_var0 / (c_var0 + c_var1)
                w[c_item0] *= alpha
                w[c_item1] *= 1-alpha
        return w

    def get_cluster_var(self, cov, c_items):
        cov_ = cov.loc[c_items, c_items]
        w_ = self.get_ivp(cov_).reshape(-1, 1)
        c_var = np.dot(np.dot(w_.T, cov_), w_)[0, 0]
        return c_var

    def get_ivp(self, cov, **kwargs):
        ivp = 1./np.diag(cov)
        return ivp/ivp.sum()

    def show_dendrogram(self, corr, **kwargs):
        plt.title("Hierarchical Cluster")
        plt.xlabel("index")
        plt.ylabel("Distance")
        links = sch.linkage(corr, 'single')
        sch.dendrogram(links, **kwargs)
        plt.show()


if __name__ == '__main__':
    p = np.array(
        [
            [1, 0.7, 0.2],
            [0.7, 1, -0.2],
            [0.2, -0.2, 1]
        ]
    )

    _asset_universe = AssetUniverse()
    for idx, _ in enumerate(p):
        _asset_universe.append(Asset(str(idx)))

    p = Metric(name='correlation', value=p)
    hcp = HierarchyRiskParityEngine(asset_universe=_asset_universe)
    hcp.show_dendrogram(corr=p.value)
    _portfolio = hcp.run(corr=p)
    print(_portfolio.is_valid())
    print(_portfolio)
