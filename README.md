# LinchFin

LinchFin is a financial machine learning library for python3 to handle financial modelling.

The core algorithm is based on the book[^1] and papers. Algorithms are still on development.  
If you have any issue or idea, please contact to me.

## Pipelines

The basic flow of producing optimized portfolio is the below

1. load time series data
2. wrangling time series data
3. get the features of the time series
4. run portfolio module
5. apply rule engine
6. test portfolio
7. evaluate portfolio risk


## Structure (on development)

The core concept is from DDD (Data Driven Development). Between the modules, inputs and outputs are objects like entities, data values and aggregation

### data classes

1. AssetClass
2. Asset
3. AssetUniverse
4. Cluster
5. Portfolio

### value types

1. Feature
2. Metric
3. Weights
4. Weight
5. Prices
6. TimeSeries
7. AssetId
8. AssetCode

### Aggregator

*Not yet*


## Cores (on development)

#### Encoder

Converse the data to features or metrics keeping the attributes.

#### RuleEngine

apply portfolio rules

#### Clustering

Build a cluster for assets having similar attributes.

#### Portfolio

Generate a portfolio based on asset allocation theories.

#### Backtesting

Run a backtest simulation to test the portfolio.

#### Risk Management

calculate the valuation and risk exposures.


## Algorithms

- HRP (Hierarchical Risk Parity)
- MVO (Mean Variance Optimization)
- Gibbs sampling
- Monte Carlo Simulation
- Monte Carlo Markov Chain


[^1]: Advances in financial machine learning, Marcos Lopez de prado, 2017