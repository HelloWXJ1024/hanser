import os
import functools
import tensorflow as tf

DEFAULT_IMAGE_SIZE = 224
NUM_CHANNELS = 3

NUM_IMAGES = {
    'train': 1281167,
    'validation': 50000,
}

_NUM_TRAIN_FILES = 1024
_SHUFFLE_BUFFER = 10000


def get_filenames(data_dir, training):
  """Return filenames for dataset."""
  if training:
    return [
        os.path.join(data_dir, 'train-%05d-of-01024' % i)
        for i in range(_NUM_TRAIN_FILES)]
  else:
    return [
        os.path.join(data_dir, 'validation-%05d-of-00128' % i)
        for i in range(128)]


def parse_example_proto(example_serialized):
    feature_map = {
        'image/encoded': tf.io.FixedLenFeature([], dtype=tf.string,
                                               default_value=''),
        'image/class/label': tf.io.FixedLenFeature([], dtype=tf.int64,
                                                   default_value=-1),
    }

    features = tf.io.parse_single_example(serialized=example_serialized,
                                          features=feature_map)
    label = tf.cast(features['image/class/label'], dtype=tf.int32)

    return features['image/encoded'], label


def parse_example_proto_and_decode(example_serialized):
    image_buffer, label = parse_example_proto(example_serialized)
    image_buffer = tf.reshape(image_buffer, shape=[])
    image_buffer = tf.io.decode_jpeg(image_buffer, 3)
    return image_buffer, label

def decode_and_transform(transform):
    def fn(x, training):
        image, label = parse_example_proto(x)
        return transform(image, label, training)
    return fn

def input_fn(data_dir, training, transform, batch_size):
    filenames = get_filenames(data_dir, training)
    dataset = tf.data.Dataset.from_tensor_slices(filenames)

    if training:
        dataset = dataset.shuffle(buffer_size=_NUM_TRAIN_FILES)

    dataset = dataset.interleave(
        tf.data.TFRecordDataset,
        cycle_length=10,
        num_parallel_calls=tf.data.experimental.AUTOTUNE)

    if training:
        dataset = dataset.map(
            parse_example_proto_and_decode,
            num_parallel_calls=tf.data.experimental.AUTOTUNE)
    dataset = dataset.cache()

    if training:
        dataset = dataset.shuffle(buffer_size=_SHUFFLE_BUFFER)
        dataset = dataset.repeat()

    if training:
        parse_record_fn = transform
    else:
        parse_record_fn = decode_and_transform(transform)

    map_fn = functools.partial(
        parse_record_fn,
        training=training)

    dataset = dataset.map(
        map_fn, num_parallel_calls=tf.data.experimental.AUTOTUNE)
    dataset = dataset.batch(batch_size, drop_remainder=training)

    dataset = dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)

    options = tf.data.Options()
    options.experimental_slack = True
    dataset = dataset.with_options(options)
    return dataset


def make_imagenet_dataset(data_dir, batch_size, eval_batch_size, transform, **kwargs):
    ds_train = input_fn(data_dir, training=True, transform=transform, batch_size=batch_size, **kwargs)
    ds_eval = input_fn(data_dir, training=False, transform=transform, batch_size=eval_batch_size, **kwargs)
    return ds_train, ds_eval