from typing import List

import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import scipy.cluster.hierarchy as sch

from linchfin.common.cov import CovarianceEstimator
from linchfin.base.dataclasses.entities import Cluster
from linchfin.base.encoder import CorrelationEncoder
from linchfin.base.dataclasses.value_types import Metric, Feature, TimeSeries


class HierarchicalCorrCluster:
    cov_estimator = CovarianceEstimator()

    def __init__(self, estimation=True):
        self.distance_encoder = CorrelationEncoder()
        self.estimation = estimation

    def calc_correlation(self, x: pd.DataFrame):
        if self.estimation:
            return self.cov_estimator.calc_corr(x)
        return x.corr()

    def calc_covariance(self, x: pd.DataFrame):
        if self.estimation:
            return self.cov_estimator.calc_cov(x)
        return x.cov()

    def calc_threshold(self, distances):
        return distances.max() / 2

    @staticmethod
    def calc_linkage(distance: Metric) -> np.array:
        links = sch.linkage(distance.value, 'single')
        return links

    def get_sorted_corr(self, corr: pd.DataFrame or Feature, indices) -> Feature:
        if isinstance(corr, Feature):
            corr_value = corr.value
        else:
            corr_value = corr
        sorted_corr = corr_value[corr_value.index[indices]].iloc[indices]
        return Feature(name='corr', value=sorted_corr)

    @staticmethod
    def get_quansi_diag(link):
        link = link.astype(int)
        last_cluster = link[-1]
        sort_ix = pd.Series([link[-1, 0], link[-1, 1]])
        num_items = last_cluster[3]

        while sort_ix.max() >= num_items:
            sort_ix.index = range(0, sort_ix.shape[0] * 2, 2)  # make space
            df0 = sort_ix[sort_ix >= num_items]
            i = df0.index
            j = df0.values - num_items

            sort_ix[i] = link[j, 0]
            df0 = pd.Series(link[j, 1], index=i + 1)
            sort_ix = sort_ix.append(df0)
            sort_ix = sort_ix.sort_index()  # re-sort
            sort_ix.index = range(sort_ix.shape[0])  # reindex
        return sort_ix.tolist()

    def run(self, time_series: TimeSeries):
        _corr = self.calc_correlation(time_series.fillna(0))
        dist = self.distance_encoder.encode(corr=Feature(name='corr', value=_corr))
        linkage = self.calc_linkage(dist)
        diag_indices = self.get_quansi_diag(linkage)
        _sorted_corr = self.get_sorted_corr(corr=_corr, indices=diag_indices)
        return _sorted_corr

    def assign_cluster(self, sorted_corr: Feature):
        diff_metrics = ((sorted_corr.value.diff(1).pow(2)).sum(axis=1) ** 1 / 2)
        threshold = diff_metrics.mean()
        return (diff_metrics > threshold).astype(int).cumsum()

    def get_clusters(self, distance: Metric) -> List[Cluster]:
        links = self.calc_linkage(distance=distance)
        return [Cluster(elements=[int(p1), int(p2)], d=dist, size=int(size))
                for p1, p2, dist, size in links]

    def show_dendrogram(self, corr: Feature, **kwargs):
        plt.title("Hierarchical Cluster")
        plt.xlabel("index")
        plt.ylabel("Distance")
        links = sch.linkage(corr.value.to_numpy(), 'single')
        sch.dendrogram(links, **kwargs)
        plt.show()

    def show_heatmap(self, corr: Feature):
        sns.heatmap(corr.value)
        plt.show()


if __name__ == '__main__':
    # from matplotlib import pyplot
    # from linchfin.common.calc import calc_volatility, calc_portfolio_return, calc_sharp_ratio
    from linchfin.base.dataclasses.entities import AssetUniverse
    from linchfin.base.dataclasses.value_types import Feature
    from linchfin.core.clustering.sectors import SectorTree
    # from linchfin.core.portfolio.rules import RuleEngine
    # from linchfin.core.portfolio.hierarchical import HierarchyRiskParityEngine
    from linchfin.data_handler.reader import DataReader
    from linchfin.metadata import ETF_SECTORS
    from linchfin.common.calc import (
        calc_monthly_returns, calc_corr, calc_daily_returns
    )
    from linchfin.common.cov import CovarianceEstimator
    # from linchfin.core.portfolio.hierarchical import HierarchyRiskParityEngine
    # from linchfin.simulation.backtest import BacktestSimulator

    data_reader = DataReader(start='2019/01/01', end='2021/04/01')
    sector_tree = SectorTree(tree_data=ETF_SECTORS)
    # 3-1. filter asset universe
    filtered = sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 63)
    asset_universe = AssetUniverse(assets=filtered)

    # 4. load time_series
    time_series = data_reader.get_adj_close_price(symbols=asset_universe.symbols)
    time_series = time_series.dropna(axis=1)
    time_series_monthly = calc_monthly_returns(time_series=time_series)

    hcorr_cluster = HierarchicalCorrCluster()
    _sorted_corr = hcorr_cluster.run(time_series=time_series_monthly.fillna(0))
    hcorr_cluster.show_heatmap(corr=_sorted_corr)
