import requests as req
import re
from collections import OrderedDict
import json

name = "name"
description = "description"
children = "children"
x = 'x'
y = 'y'
dx = 'dx'
dy = 'dy'


class FinvizCrawler:
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15'
    }
    char_maps = OrderedDict(
        [
            ('};', '}'),
            ('dx:', '\"dx\":'),
            ('dy:', '\"dy\":'),
            ('x:', '\"x\":'),
            ('y:', '\"y\":'),
            ('name:', '\"name\":'),
            ('description:', '\"description\":'),
            ('children:', '\"children\":')
        ]
    )

    def get_maps(self):
        res = req.get('https://finviz.com/js/maps/etf_788.js', headers=self.headers)
        result = self.sanitize_results(result=res.text)
        return json.loads(result)

    def sanitize_results(self, result):
        result = re.sub('[\w\s\=]+\{', '{', result)
        for src, to in self.char_maps.items():
            result = re.sub(src, to, result)
        return result


if __name__ == '__main__':
    from pprint import pprint
    crawler = FinvizCrawler()
    maps = crawler.get_maps()
    pprint(maps)
