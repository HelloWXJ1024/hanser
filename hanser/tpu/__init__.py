import os

import tensorflow as tf
from tensorflow.python.distribute.values import PerReplica

from hanser.tpu.bn import TpuBatchNormalization


def get_colab_tpu():
    tpu_address = os.environ.get("COLAB_TPU_ADDR")
    if tpu_address:
        tpu_address = "grpc://" + tpu_address
        tf.keras.backend.clear_session()
        tpu = tf.distribute.cluster_resolver.TPUClusterResolver(tpu_address)
        tf.config.experimental_connect_to_cluster(tpu)
        tf.tpu.experimental.initialize_tpu_system(tpu)
        strategy = tf.distribute.experimental.TPUStrategy(tpu)
        return strategy


def auth():
    from google.colab import auth
    auth.authenticate_user()


def local_results(strategy, values):
    if isinstance(values, PerReplica):
        return strategy.experimental_local_results(values)
    elif isinstance(values, (list, tuple)):
        return values.__class__(strategy.experimental_local_results(v) for v in values)
    else:
        raise ValueError("`values` must be PerReplica, list or tuple or PerReplica, got %s" % type(values))