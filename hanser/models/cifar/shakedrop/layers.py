import tensorflow as tf
from tensorflow.keras.layers import Layer

@tf.custom_gradient
def ShakeDropOp(x, p, alpha_min, alpha_max, beta_min, beta_max):
    gate = tf.random.uniform() > (1 - p)

    out = tf.cond(
        gate,
        lambda: x * tf.random.uniform(x.shape, alpha_min, alpha_max, dtype=x.dtype),
        lambda: x)

    def custom_grad(dy):
        grad = tf.cond(
            gate,
            lambda: dy * tf.random.uniform(dy.shape, beta_min, beta_max, dtype=dy.dtype),
            lambda: dy)
        return grad, None, None, None

    return out, custom_grad


class ShakeDrop(Layer):
    def __init__(self, p, alphas, betas, **kwargs):
        self.p = p
        self.alphas = alphas
        self.betas = betas
        super().__init__(**kwargs)

    def call(self, x, training):
        if training:
            return ShakeDropOp(x, self.p, self.alphas[0], self.alphas[1], self.betas[0], self.betas[1])
        else:
            return x * (1 - self.p)

    def get_config(self):
        base_config = super().get_config()
        base_config['p'] = self.p
        base_config['alphas'] = self.alphas
        base_config['betas'] = self.betas
        return base_config
