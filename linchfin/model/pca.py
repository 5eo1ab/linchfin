import numpy as np


a = np.random.randn(9, 6) + 1j*np.random.randn(9, 6)
u, s, vh = np.linalg.svd(a)

print()