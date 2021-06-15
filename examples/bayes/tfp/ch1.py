import tensorflow as tf
from matplotlib import pyplot as plt
import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors


class _TFColor:
    """Enum of colors used in TF docs."""
    red = '#F15854'
    blue = '#5DA5DA'
    orange = '#FAA43A'
    green = '#60BD68'
    pink = '#F17CB0'
    brown = '#B2912F'
    purple = '#B276B2'
    yellow = '#DECF3F'
    gray = '#4D4D4D'

    def __getitem__(self, i):
        return [
            self.red,
            self.orange,
            self.green,
            self.blue,
            self.pink,
            self.brown,
            self.purple,
            self.yellow,
            self.gray,
        ][i % 9]

TFColor = _TFColor()


if __name__ == '__main__':
    p = tf.linspace(start=0., stop=1., num=50)

    plt.figure(figsize=(12.5, 6))
    plt.plot(p, 2*p/(1+p), color=TFColor[3], lw=3)
    x = 0.2
    f = lambda x: 2 * x / (1+x)
    plt.scatter(x, f(x), s=140, c=TFColor[3])
    plt.show()

    prior = tf.constant([0.2, 0.8])
    posterior = tf.constant([1./3, 2./3])

    plt.figure(figsize=(12.5, 4))
    colours = [TFColor[0], TFColor[3]]
    plt.bar([0, .7], prior, alpha=.7, width=.25, color=colours[0])

    plt.bar([0+0.25, .7+0.25], posterior, alpha=.7, width=.25, color=colours[0])
