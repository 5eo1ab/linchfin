from collections import OrderedDict, defaultdict
from typing import List

from linchfin.base.dataclasses.entities import Asset, Cluster
from linchfin.metadata import ETF_SECTORS


DELIMITER = '-'


class SectorTree:
    def __init__(self, tree_data: dict):
        self.cluster_dic = OrderedDict()
        self.root = self.parse_tree(tree_data=tree_data)

    def parse_tree(self, tree_data, keys=None):
        if not keys:
            key = 'root'
            keys = []
        else:
            key = f'{DELIMITER}'.join(keys)

        _cluster = self.cluster_dic.get(key, Cluster(name=key))
        self.cluster_dic[key] = _cluster

        for k, v in tree_data.items():
            if isinstance(v, dict):
                keys.append(k)
                _sub_cluster = self.parse_tree(tree_data=tree_data[k], keys=keys)
                keys.pop()
                _cluster.elements.append(_sub_cluster)

            elif isinstance(v, Asset):
                sub_sector = keys[-1]
                asset_class_name = '-'.join(keys)
                _cluster = self.cluster_dic.get(asset_class_name, Cluster(name=sub_sector))
                v.asset_class.asset_class_name = asset_class_name
                _cluster.elements.append(v)
            else:
                TypeError(f"Check tree data type {k}:{v}")
        return _cluster

    def categorize(self, assets: List[Asset], depth=1):
        categories = defaultdict(list)
        assert depth >= 0, "Depth must be larger than 0"

        for a in assets:
            category_keys = a.asset_class.name.split('-')
            category_name = f"{DELIMITER}".join(category_keys[:depth])
            categories[category_name].append(a)

        categorized = OrderedDict()
        for k, elements in categories.items():
            categorized[k] = Cluster(name=k, elements=elements)
        return categorized

    def filter(self, key, filter_func=lambda x: x):
        searched = self.search(node=self.get_node(key=key))
        return [_node for _node in searched if filter_func(_node)]

    def search(self, node: str or Asset or Cluster) -> List[Asset]:
        if isinstance(node, str):
            node = self.get_node(key=node)

        searched = []
        for _elem in node.elements:
            if isinstance(_elem, Cluster):
                searched += self.search(_elem)
            elif isinstance(_elem, Asset):
                searched.append(_elem)
            else:
                raise TypeError("??")
        return searched

    def get_node(self, key):
        if key not in self.cluster_dic:
            raise KeyError(f"{key} is not in cluster tree")
        return self.cluster_dic[key]


if __name__ == '__main__':
    __sector_tree = SectorTree(tree_data=ETF_SECTORS)
    filtered = __sector_tree.filter(key='Strategy', filter_func=lambda x: x.extra['cap_size'] > 10)
    not_filtered = __sector_tree.filter(key='Strategy')
    print(filtered[0].extra['desc'])
