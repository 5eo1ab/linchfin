import numpy as np
import pymc3 as pm
from matplotlib import pyplot as plt
from multiprocessing import freeze_support


if __name__ == '__main__':
    freeze_support()

    with pm.Model() as model:
        parameter = pm.Exponential("poisson_param", 1.0)
        data_generator = pm.Poisson('data_generator', parameter)

        with model:
            data_plus_one = data_generator + 1

        print(parameter.tag.test_value)

    with pm.Model() as model:
        theta = pm.Exponential("theta", 2.0)
        data_generator = pm.Poisson("data_generator", theta)

    with pm.Model() as ab_testing:
        probs = {}
        probs['A'] = pm.Uniform("P(A)", 0, 1)
        probs['B'] = pm.Uniform("P(B)", 0, 1)

    with pm.Model() as model:
        lambda_1 = pm.Exponential("lambda_1", 1.0)
        lambda_2 = pm.Exponential("lambda_2", 1.0)
        tau = pm.DiscreteUniform("tau", lower=0, upper=10)

    new_deterministic_variable = lambda_1 + lambda_2
    n_data_points = 5
    idx = np.arange(n_data_points)
    with model:
        lambda_ = pm.math.switch(tau >= idx, lambda_1, lambda_2)
