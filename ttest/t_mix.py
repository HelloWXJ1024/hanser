import numpy as np
import tensorflow as tf

from hanser.transform import mixup_batch, mixup_in_batch, cutmix_batch, resizemix_batch, image_dimensions


from PIL import Image
im = Image.open('/Users/hrvvi/Downloads/images/cat1.jpeg')
im = im.crop((66, 0, 234, 168)).resize((224, 224))
im2 = Image.open('/Users/hrvvi/Downloads/images/cat2.jpeg')
im2 = im2.crop((0, 0, 224, 224)).resize((224, 224))

image = tf.convert_to_tensor([np.array(im), np.array(im2)], dtype=np.float32)
label = tf.one_hot([0, 2], 3)

lams = []
for i in range(1):
    xt, yt = resizemix_batch(image, label, scale=(0.01, 0.49), hard=True, sample_area=True)
    lams.append(yt[0, 0].numpy())
print(yt)
xt = xt.numpy()
Image.fromarray(xt[0].astype(np.uint8)).show()

yp = tf.random.normal((2, 3))

from hanser.losses import CrossEntropy
criterion = CrossEntropy(label_smoothing=0.1)
loss1 = criterion(yt, yp)
lam = yt[0, 0]
yt_a = tf.one_hot([0, 2], 3)
yt_b = tf.one_hot([2, 0], 3)
loss2 = lam * criterion(yt_a, yp) + (1 - lam) * criterion(yt_b, yp)
np.testing.assert_allclose(loss1.numpy(), loss2.numpy())