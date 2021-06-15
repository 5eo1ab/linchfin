import collections
import math
import os
import time

import numpy as np
import pandas as pd
import scipy
import scipy.stats
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors


true_mean = np.zeros([2], dtype=np.float32)
true_var = np.array([4.0, 1.0], dtype=np.float32)
true_cor = np.array([[1.0, 0.9], [0.9, 1.0]], dtype=np.float32)

true_cov = np.expand_dims(np.sqrt(true_var), axis=1).dot(
    np.expand_dims(np.sqrt(true_var), axis=1).T) * true_cor

true_precision = np.linalg.inv(true_cov)

print(true_cov)
print('eigenvalues: ', np.linalg.eigvals(true_cov))

np.random.seed(123)
my_data = np.random.multivariate_normal(
    mean=true_mean, cov=true_cov, size=100,
    check_valid='ignore').astype(np.float32)
plt.scatter(my_data[:, 0], my_data[:, 1], alpha=0.75)
plt.show()

print('mean of observations:', np.mean(my_data, axis=0))
print('true mean:', true_mean)
print('covariance of observations:\n', np.cov(my_data, rowvar=False))
print('true covariance:\n', true_cov)


def log_lik_data_numpy(precision, data):
  # np.linalg.inv is a really inefficient way to get the covariance matrix, but
  # remember we don't care about speed here
  cov = np.linalg.inv(precision)
  rv = scipy.stats.multivariate_normal(true_mean, cov)
  return np.sum(rv.logpdf(data))

# test case: compute the log likelihood of the data given the true parameters
log_lik_data_numpy(true_precision, my_data)


PRIOR_DF = 3
PRIOR_SCALE = np.eye(2, dtype=np.float32) / PRIOR_DF

def log_lik_prior_numpy(precision):
  rv = scipy.stats.wishart(df=PRIOR_DF, scale=PRIOR_SCALE)
  return rv.logpdf(precision)

# test case: compute the prior for the true parameters
log_lik_prior_numpy(true_precision)

n = my_data.shape[0]
nu_prior = PRIOR_DF
v_prior = PRIOR_SCALE
nu_posterior = nu_prior + n
v_posterior = np.linalg.inv(np.linalg.inv(v_prior) + my_data.T.dot(my_data))
posterior_mean = nu_posterior * v_posterior
v_post_diag = np.expand_dims(np.diag(v_posterior), axis=1)
posterior_sd = np.sqrt(nu_posterior *
                       (v_posterior ** 2.0 + v_post_diag.dot(v_post_diag.T)))

sample_precision = np.linalg.inv(np.cov(my_data, rowvar=False, bias=False))
fig, axes = plt.subplots(2, 2)
fig.set_size_inches(10, 10)
for i in range(2):
  for j in range(2):
    ax = axes[i, j]
    loc = posterior_mean[i, j]
    scale = posterior_sd[i, j]
    xmin = loc - 3.0 * scale
    xmax = loc + 3.0 * scale
    x = np.linspace(xmin, xmax, 1000)
    y = scipy.stats.norm.pdf(x, loc=loc, scale=scale)
    ax.plot(x, y)
    ax.axvline(true_precision[i, j], color='red', label='True precision')
    ax.axvline(sample_precision[i, j], color='red', linestyle=':', label='Sample precision')
    ax.set_title('precision[%d, %d]' % (i, j))
plt.legend()
plt.show()

# case 1: get log probabilities for a vector of iid draws from a single
# normal distribution
norm1 = tfd.Normal(loc=0., scale=1.)
probs1 = norm1.log_prob(tf.constant([1., 0.5, 0.]))


# # case 2: get log probabilities for a vector of independent draws from
# # multiple normal distributions with different parameters.  Note the vector
# # values for loc and scale in the Normal constructor.
# norm2 = tfd.Normal(loc=[0., 2., 4.], scale=[1., 1., 1.])
# probs2 = norm2.log_prob(tf.constant([1., 0.5, 0.]))
#
# print('iid draws from a single normal:', probs1.numpy())
# print('draws from a batch of normals:', probs2.numpy())
#
# VALIDATE_ARGS = True
# ALLOW_NAN_STATS = False
#
#
# def log_lik_data(precisions, replicated_data):
#   n = tf.shape(precisions)[0]  # number of precision matrices
#   # We're estimating a precision matrix; we have to invert to get log
#   # probabilities.  Cholesky inversion should be relatively efficient,
#   # but as we'll see later, it's even better if we can avoid doing the Cholesky
#   # decomposition altogether.
#   precisions_cholesky = tf.linalg.cholesky(precisions)
#   covariances = tf.linalg.cholesky_solve(
#       precisions_cholesky, tf.linalg.eye(2, batch_shape=[n]))
#   rv_data = tfd.MultivariateNormalFullCovariance(
#       loc=tf.zeros([n, 2]),
#       covariance_matrix=covariances,
#       validate_args=VALIDATE_ARGS,
#       allow_nan_stats=ALLOW_NAN_STATS)
#
#   return tf.reduce_sum(rv_data.log_prob(replicated_data), axis=0)
#
# # For our test, we'll use a tensor of 2 precision matrices.
# # We'll need to replicate our data for the likelihood function.
# # Remember, TFP wants the data to be structured so that the sample dimensions
# # are first (100 here), then the batch dimensions (2 here because we have 2
# # precision matrices), then the event dimensions (2 because we have 2-D
# # Gaussian data).  We'll need to add a middle dimension for the batch using
# # expand_dims, and then we'll need to create 2 replicates in this new dimension
# # using tile.
# n = 2
# replicated_data = np.tile(np.expand_dims(my_data, axis=1), reps=[1, 2, 1])
# print(replicated_data.shape)
#
# # check against the numpy implementation
# precisions = np.stack([np.eye(2, dtype=np.float32), true_precision])
# n = precisions.shape[0]
# lik_tf = log_lik_data(precisions, replicated_data=replicated_data).numpy()
#
# for i in range(n):
#   print(i)
#   print('numpy:', log_lik_data_numpy(precisions[i], my_data))
#   print('tensorflow:', lik_tf[i])
#
#
# @tf.function(autograph=False)
# def log_lik_prior(precisions):
#   rv_precision = tfd.WishartTriL(
#       df=PRIOR_DF,
#       scale_tril=tf.linalg.cholesky(PRIOR_SCALE),
#       validate_args=VALIDATE_ARGS,
#       allow_nan_stats=ALLOW_NAN_STATS)
#   return rv_precision.log_prob(precisions)
#
#
# # check against the numpy implementation
# precisions = np.stack([np.eye(2, dtype=np.float32), true_precision])
# n = precisions.shape[0]
# lik_tf = log_lik_prior(precisions).numpy()
#
# for i in range(n):
#   print(i)
#   print('numpy:', log_lik_prior_numpy(precisions[i]))
#   print('tensorflow:', lik_tf[i])
#
# def get_log_lik(data, n_chains=1):
#   # The data argument that is passed in will be available to the inner function
#   # below so it doesn't have to be passed in as a parameter.
#   replicated_data = np.tile(np.expand_dims(data, axis=1), reps=[1, n_chains, 1])
#
#   @tf.function(autograph=False)
#   def _log_lik(precision):
#     return log_lik_data(precision, replicated_data) + log_lik_prior(precision)
#
#   return _log_lik
#
#
# @tf.function(autograph=False)
# def sample():
#   tf.random.set_seed(123)
#   init_precision = tf.expand_dims(tf.eye(2), axis=0)
#
#   # Use expand_dims because we want to pass in a tensor of starting values
#   log_lik_fn = get_log_lik(my_data, n_chains=1)
#
#   # we'll just do a few steps here
#   num_results = 10
#   num_burnin_steps = 10
#   states = tfp.mcmc.sample_chain(
#      num_results=num_results,
#      num_burnin_steps=num_burnin_steps,
#      current_state=[
#          init_precision,
#      ],
#      kernel=tfp.mcmc.HamiltonianMonteCarlo(
#          target_log_prob_fn=log_lik_fn,
#          step_size=0.1,
#          num_leapfrog_steps=3),
#      trace_fn=None,
#      seed=123)
#   return states
#
# try:
#   states = sample()
# except Exception as e:
#   # shorten the giant stack trace
#   lines = str(e).split('\n')
#   print('\n'.join(lines[:5]+['...']+lines[-3:]))
#
# def get_log_lik_verbose(data, n_chains=1):
#   # The data argument that is passed in will be available to the inner function
#   # below so it doesn't have to be passed in as a parameter.
#   replicated_data = np.tile(np.expand_dims(data, axis=1), reps=[1, n_chains, 1])
#
#   def _log_lik(precisions):
#     # An internal method we'll make into a TensorFlow operation via tf.py_func
#     def _print_precisions(precisions):
#       print('precisions:\n', precisions)
#       return False  # operations must return something!
#     # Turn our method into a TensorFlow operation
#     print_op = tf.compat.v1.py_func(_print_precisions, [precisions], tf.bool)
#
#     # Assertions are also operations, and some care needs to be taken to ensure
#     # that they're executed
#     assert_op = tf.assert_equal(
#         precisions, tf.linalg.matrix_transpose(precisions),
#         message='not symmetrical', summarize=4, name='symmetry_check')
#
#     # The control_dependencies statement forces its arguments to be executed
#     # before subsequent operations
#     with tf.control_dependencies([print_op, assert_op]):
#       return (log_lik_data(precisions, replicated_data) +
#               log_lik_prior(precisions))
#
#   return _log_lik
#
# @tf.function(autograph=False)
# def sample():
#   tf.random.set_seed(123)
#   init_precision = tf.eye(2)[tf.newaxis, ...]
#   log_lik_fn = get_log_lik_verbose(my_data)
#   # we'll just do a few steps here
#   num_results = 10
#   num_burnin_steps = 10
#   states = tfp.mcmc.sample_chain(
#       num_results=num_results,
#       num_burnin_steps=num_burnin_steps,
#       current_state=[
#           init_precision,
#       ],
#       kernel=tfp.mcmc.HamiltonianMonteCarlo(
#           target_log_prob_fn=log_lik_fn,
#           step_size=0.1,
#           num_leapfrog_steps=3),
#       trace_fn=None,
#       seed=123)
#
# try:
#     states = sample()
# except Exception as e:
#     # shorten the giant stack trace
#     lines = str(e).split('\n')
#     print('\n'.join(lines[:5]+['...']+lines[-3:]))
