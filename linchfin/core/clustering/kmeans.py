from sklearn.cluster import KMeans
import seaborn as sns
from matplotlib import pyplot as plt


class KMeansCluster(KMeans):
    def heatmap(self, X):
        predicted = self.predict(X=X)
        sns.heatmap(X.iloc[predicted.argsort()])
        plt.show()


if __name__ == "__main__":
    from linchfin.data_handler.reader import DataReader
    from linchfin.core.analysis.profiler import AssetProfiler
    from linchfin.core.clustering.sectors import SectorTree, ETF_SECTORS
    from linchfin.base.dataclasses.entities import AssetUniverse

    sector_tree = SectorTree(ETF_SECTORS)
    profiler = AssetProfiler()
    tickers = []
    data_reader = DataReader()
    au = AssetUniverse(assets=sector_tree.search(sector_tree.root))
    ts = data_reader.get_adj_close_price(symbols=au.symbols[:30] + ['SPY'])
    asset_profile = profiler.profile(prices=ts, factors=profiler.metrics)

    km = KMeansCluster(n_clusters=3)
    km.fit(asset_profile.fillna(0))
    km.heatmap(asset_profile.fillna(0))
    # km.predict(asset_profile)
