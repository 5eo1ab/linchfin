import scipy.cluster.hierarchy as sch
import numpy as np
import pandas as pd
from dataclasses import dataclass
from matplotlib import pyplot as plt


@dataclass
class Cluster:
    e1: int
    e2: int
    d: float
    size: int

    def __post_init__(self):
        for k, _field in self.__dataclass_fields__.items():
            v = getattr(self, k)
            if not isinstance(v, _field.type):
                setattr(self, k, _field.type(getattr(self, k)))


class HierarchyCluster:
    def __init__(self):
        pass

    @staticmethod
    def calc_correlation(x: np.array):
        return x.corr()

    @staticmethod
    def calc_covariance(x: np.array):
        return x.cov()

    def run(self, corr):
        _clusters = self.get_clusters(corr=corr)
        sort_ix = self.get_quansi_diag(_clusters)
        weights = self.get_recursive_bisect(cov=pd.DataFrame(p), sort_ix=sort_ix)
        return weights

    def get_clusters(self, corr: np.array):
        dist = ((1 - corr) / 2.) ** .5
        links = sch.linkage(dist, 'single')
        return [Cluster(*c) for c in links]

    def get_quansi_diag(self, link):
        # link = link.astype(int)
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

    hcp = HierarchyCluster()
    hcp.show_dendrogram(corr=p)
    w = hcp.run(corr=p)
    print("weights:", w)