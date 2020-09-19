from dataclasses import dataclass, field
from collections import OrderedDict
from linchfin.base.dataclasses.entities import AssetClass
from linchfin.metadata import ETF_SECTORS


def parse(sectors):
    dic = OrderedDict()
    if 'children' not in sectors:
        _sector = Sector(asset_class_name=sectors['name'], desc=sectors['description'], cap_size=sectors['cap_size'])
        return _sector

    for _child in sectors['children']:
        dic[_child['name']] = parse(_child)
    return dic


@dataclass
class Sector(AssetClass):
    desc: str = field(default='')
    cap_size: float = field(default=0)


class SectorTree:
    def __init__(self, sector_dic):
        self.sector_dic = sector_dic

    @property
    def keys(self):
        return list(self.sector_dic.keys())
    #
    # @classmethod
    # def get_instance(cls, tree_data: dict):
    #     def build_tree(sector_tree: SectorTree, tree_data, base_key=''):
    #         for k, v in tree_data.items():
    #             if base_key:
    #                 sector_name = f"{base_key}-{k}"
    #             else:
    #                 sector_name = k
    #                 sector_tree.base_keys.append(k)
    #
    #             if isinstance(v, dict):
    #                 build_tree(sector_tree, tree_data=tree_data[k], base_key=k)
    #             elif isinstance(v, Sector):
    #                 sector_tree.register(k=sector_name, sector=v)
    #             else:
    #                 TypeError(f"Check tree data type {k}:{v}")
    #         return sector_tree
    #
    #     _sector_tree = cls()
    #     return build_tree(sector_tree=_sector_tree, tree_data=tree_data)

    def register(self, k, sector: Sector):
        self.sector_dic[k] = sector

    def search(self, sector_dic=None):
        if sector_dic is None:
            sector_dic = self.sector_dic

        for k, v in sector_dic.items():
            if isinstance(v, Sector):
                print(v.cap_size)
                return v.cap_size
            elif isinstance(v, OrderedDict):
                self.search(v)
            else:
                TypeError(f"Check tree data type {k}:{v}")


if __name__ == '__main__':
    etf_sectors = parse(ETF_SECTORS)
    sector_tree = SectorTree(sector_dic=etf_sectors)
    print(sector_tree.search())

    # sector_tree = SectorTree.get_instance(tree_data=etf_sectors)
    # print(sector_tree.keys)
    # print(sector_tree.base_keys)
    # print(sector_tree.sector_dic)
