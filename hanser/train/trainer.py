import tensorflow as tf

import time


def print_results(prefix, elapsed, results):
    s = "%s \tcost: %ds" % (prefix, elapsed)
    for name, val in results:
        s = s + ", %s: %.3f" % (name, val)
    print(s)


class Trainer:

    def __init__(self, model, criterion, optimizer, lr_schedule, metrics=(), test_metrics=(), weight_decay=None, tpu=None, strategy=None):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.lr_schedule = lr_schedule
        self.metrics = metrics
        self.test_metrics = test_metrics
        self.weight_decay = weight_decay
        self.tpu = tpu
        self.strategy = strategy

    def _train_step(self, inputs):
        images, labels = inputs
        with tf.GradientTape() as tape:
            preds = self.model(images, training=True)
            loss1 = self.criterion(labels, preds)
            if self.weight_decay is not None:
                loss2 = self.weight_decay * tf.add_n([
                    tf.nn.l2_loss(v)
                    for v in tf.trainable_variables()
                    if 'batch_normalization' not in v.name
                ])
                loss = loss1 + loss2
            else:
                loss = loss1
            # loss = loss / strategy.num_replicas_in_sync
        grads = tape.gradient(loss, self.model.trainable_variables)
        update_vars = self.optimizer.apply_gradients(
            zip(grads, self.model.trainable_variables))

        update_ops = [update_vars]
        for metric in self.metrics:
            if 'loss' in metric.name:
                update_op = metric.update_state(loss1)
            else:
                update_op = metric.update_state(labels, preds)
            update_ops.append(update_op)
        #     update_accuracy = training_accuracy.update_state(labels, logits)
        with tf.control_dependencies(update_ops):
            return tf.identity(loss)

    def _test_step(self, inputs):
        images, labels = inputs
        preds = self.model(images, training=False)
        loss = self.criterion(labels, preds)

        update_ops = []
        for metric in self.test_metrics:
            if 'loss' in metric.name:
                update_op = metric.update_state(loss)
            else:
                update_op = metric.update_state(labels, preds)
            update_ops.append(update_op)
        #     update_accuracy = training_accuracy.update_state(labels, logits)
        with tf.control_dependencies(update_ops):
            return tf.identity(loss)

    def train_and_evaluate(self, epochs, ds_train, steps_per_epoch, ds_val, val_steps):
        if self.tpu is None:
            train_it = ds_train.make_initializable_iterator()
            val_it = ds_val.make_initializable_iterator()

            train_op = self._train_step(train_it.get_next())
            val_op = self._test_step(val_it.get_next())

            target = ''
            config = None
        else:
            ds_train = self.strategy.experimental_distribute_dataset(ds_train)
            ds_val = self.strategy.experimental_distribute_dataset(ds_val)

            train_it = ds_train.make_initializable_iterator()
            val_it = ds_val.make_initializable_iterator()

            train_op = self.strategy.experimental_local_results(
                self.strategy.experimental_run_v2(
                    self._train_step, args=(train_it.get_next(),)))
            val_op = self.strategy.experimental_local_results(
                self.strategy.experimental_run_v2(
                    self._test_step, args=(val_it.get_next(),)))

            target = self.tpu.master()
            config = tf.ConfigProto(
                allow_soft_placement = True,
                cluster_def=self.tpu.cluster_spec().as_cluster_def()
            )

        with tf.Session(target=target, config=config) as sess:
            all_variables = self.model.variables + self.optimizer.variables()
            for metric in self.metrics:
                all_variables.extend(metric.variables)
            for metric in self.test_metrics:
                all_variables.extend(metric.variables)

            sess.run([v.initializer for v in all_variables])
            sess.run(train_it.initializer)
            sess.run(val_it.initializer)
            #     checkpoint.restore(manager.latest_checkpoint)

            for epoch in range(epochs):
                print('Epoch %s' % (epoch + 1))
                start = time.time()
                for step in range(steps_per_epoch):
                    lr = self.lr_schedule(epoch + float(step) / steps_per_epoch)
                    tf.keras.backend.set_value(self.optimizer.lr, lr)
                    sess.run(train_op)
                elapsed = time.time() - start
                metric_results = []
                for m in self.metrics:
                    metric_results.append((m.name, sess.run(m.result())))
                    m.reset_states()
                print_results("Train", elapsed, metric_results)

                start = time.time()
                for step in range(val_steps):
                    sess.run(val_op)
                elapsed = time.time() - start
                metric_results = []
                for m in self.test_metrics:
                    metric_results.append((m.name, sess.run(m.result())))
                    m.reset_states()
                print_results("Val", elapsed, metric_results)

    def evaluate(self):
        pass