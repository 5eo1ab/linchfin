import pymc3 as pm
from pymc3 import DiscreteUniform, Exponential, Deterministic, Poisson, Uniform
import numpy as np

if __name__ == '__main__':
    # Predictor variable
    size = 100
    X1 = np.random.randn(size)
    X2 = np.random.randn(size) * 0.2

    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=0, sigma=10)
        beta = pm.Normal("beta", mu=0, sigma=10, shape=2)
        sigma = pm.HalfNormal("sigma", sigma=1)

        # Expected value of outcome
        mu = alpha + beta[0] * X1 + beta[1] * X2

        # Likelihood (sampling distribution) of observations
        Y_obs = pm.Normal("Y_obs", mu=mu, sigma=sigma, observed=Y)