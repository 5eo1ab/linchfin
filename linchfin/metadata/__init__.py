import json
import os
from collections import OrderedDict
import math
from linchfin.base.dataclasses.entities import Asset

WORKDIR = os.path.dirname(__file__)
etf_sector_data = json.load(open(os.path.join(WORKDIR, 'etf_sectors.json')))
stock_sector_data = json.load(open(os.path.join(WORKDIR, 'stock_sectors.json')))


def parse(sectors):
    dic = OrderedDict()
    if 'children' not in sectors:
        _asset = Asset(code=sectors['name'])

        _asset.extra['descriptions'] = sectors['description']
        if 'cap_size' in sectors:
            _asset.extra['cap_size'] = sectors['cap_size']
        else:
            _asset.extra['cap_size'] = math.sqrt(sectors['dx'] * sectors['dy'])
        return _asset

    for _child in sectors['children']:
        dic[_child['name']] = parse(_child)
    return dic


ETF_SECTORS = parse(etf_sector_data)
STOCK_SECTORS = parse(stock_sector_data)
