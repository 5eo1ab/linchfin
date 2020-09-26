import json
import os
from collections import OrderedDict
from linchfin.base.dataclasses.entities import Asset


WORKDIR = os.path.dirname(__file__)
etf_sector_data = json.load(open(os.path.join(WORKDIR, 'etf_sectors.json')))


def parse(sectors):
    dic = OrderedDict()
    if 'children' not in sectors:
        _asset = Asset(asset_name=sectors['name'])
        _asset.extra['desc'] = sectors['description']
        _asset.extra['cap_size'] = sectors['cap_size']
        return _asset

    for _child in sectors['children']:
        dic[_child['name']] = parse(_child)
    return dic


ETF_SECTORS = parse(etf_sector_data)