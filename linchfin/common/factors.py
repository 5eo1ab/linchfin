from linchfin.metadata import ETF_SECTORS
from linchfin.core.clustering.sectors import SectorTree
from linchfin.data_handler.reader import DataReader


if __name__ == '__main__':
    __sector_tree = SectorTree(tree_data=ETF_SECTORS)
    filtered = __sector_tree.filter(key='root', filter_func=lambda x: x.extra['cap_size'] > 10)
    # not_filtered = __sector_tree.filter(key='Strategy')
    print(filtered[0])
