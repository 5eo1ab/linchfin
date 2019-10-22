import pandas as pd
import numpy as np
import os
from linchfin.common.calc import *

current_dir = os.path.dirname(__file__)
os.chdir(current_dir)

print(current_dir)
CPIAUCSL = pd.read_csv('sample/data/CPIAUCSL.csv')
FEDFUNDS = pd.read_csv('sample/data/FEDFUNDS.csv')
T10Y2Y = pd.read_csv('sample/data/T10Y2Y.csv')
print(T10Y2Y)