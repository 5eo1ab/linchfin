import json
import os

WORKDIR = os.path.dirname(__file__)
ETF_SECTORS = json.load(open(os.path.join(WORKDIR, 'etf_sectors.json')))
