import pandas as pd
from sklearn import covariance
import numpy as np


class CovarianceEstimator:
    estimator_class = {
        'LedoitWolf': covariance.LedoitWolf
    }

    def __init__(self, method='LedoitWolf'):
        self.estimator = self.estimator_class[method]()

    @staticmethod
    def to_dataframe(df: pd.DataFrame, output):
        if isinstance(df, pd.DataFrame):
            output = pd.DataFrame(output, columns=df.columns, index=df.columns)
        return output

    def calc_cov(self, X):
        X = pd.DataFrame(X)
        _estimated = self.estimator.fit(X.dropna())
        _cov = _estimated.covariance_
        _cov = self.to_dataframe(X, output=_cov)
        return _cov

    def calc_corr(self, X):
        X = pd.DataFrame(X)
        _estimated = self.estimator.fit(X.dropna())
        _estimated_cov = _estimated.covariance_
        _estimated_var = np.diag(_estimated_cov).reshape(-1, 1)
        var_prod = np.dot(_estimated_var, _estimated_var.T)
        _corr = _estimated_cov / np.sqrt(var_prod)
        _corr = self.to_dataframe(df=X, output=_corr)
        return _corr


if __name__ == '__main__':
    real_cov = np.array([[.4, .2], [.2, .8]])
    X = np.random.multivariate_normal(mean=[0, 0], cov=real_cov,size=100)

    cov_estimator = CovarianceEstimator()
    corr = cov_estimator.calc_corr(X)
    print(corr, corr - real_cov)
