import tensorflow as tf

def load_checkpoint(ckpt_path, **ckpt_kwargs):
    ckpt = tf.train.Checkpoint(**ckpt_kwargs)
    ckpt_options = tf.train.CheckpointOptions(experimental_io_device="/job:localhost")
    status = ckpt.read(ckpt_path, ckpt_options)
    return status.assert_nontrivial_match().expect_partial()


def convert_checkpoint(ckpt_path, save_path, key_map=None):
    # This function do two things:
    #   1. filter model variables and exclude others (optimizer, epoch, ...)
    #   2. map keys to different name for loading weight

    key_map = key_map or {
        'model/fc': 'model/fc_ckpt_ignored'
    }

    reader = tf.train.load_checkpoint(ckpt_path)
    keys = list(reader.get_variable_to_shape_map().keys())
    model_keys = [ k for k in keys if k.startswith("model/") and 'OPTIMIZER_SLOT' not in k ]

    end = '/.ATTRIBUTES/VARIABLE_VALUE'
    assert all(k.endswith(end) for k in model_keys)

    root = tf.keras.layers.Layer()
    for key in model_keys:
        layer = root
        key_name = key
        for k, km in key_map.items():
            if key[:len(k)] == k:
                key_name = km + key[len(k):]
                break
        path = key_name[:-len(end)].split('/')
        for i in range(1, len(path) - 1):
            if not hasattr(layer, path[i]):
                child = tf.keras.layers.Layer()
                setattr(layer, path[i], child)
                layer = child
            else:
                layer = getattr(layer, path[i])
        if hasattr(layer, path[-1]):
            print(key)
            raise ValueError("Variable duplicate")
        setattr(layer, path[-1], tf.Variable(reader.get_tensor(key)))

    fake_ckpt = tf.train.Checkpoint(model=root)
    return fake_ckpt.write(save_path)
