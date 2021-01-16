import math
from tensorflow.keras import Sequential, Model
from tensorflow.keras.layers import Layer

from hanser.models.layers import Conv2d, Identity, GlobalAvgPool, Linear, Act, Pool2d
from hanser.models.cifar.res2net.layers import Res2Conv

class Bottle2neck(Layer):
    expansion = 4

    def __init__(self, in_channels, channels, stride, base_width=26, scale=4, start_block=False, erase_relu=False):
        super().__init__()
        out_channels = channels * self.expansion
        width = math.floor(channels * (base_width / 64)) * scale
        self.conv1 = Conv2d(in_channels, width, kernel_size=1,
                            norm='def', act='def')
        self.conv2 = Res2Conv(width, width, kernel_size=3, stride=stride, scale=scale, groups=1,
                              start_block=start_block, norm='def', act='def')
        self.conv3 = Conv2d(width, out_channels, kernel_size=1,
                            norm='def')

        if stride != 1 or in_channels != out_channels:
            shortcut = []
            if stride != 1:
                shortcut.append(Pool2d(2, 2, type='avg'))
            shortcut.append(
                Conv2d(in_channels, out_channels, kernel_size=1, norm='def'))
            self.shortcut = Sequential(shortcut)
        else:
            self.shortcut = Identity()

        self.act = Act() if not erase_relu else Identity()

    def call(self, x):
        identity = self.shortcut(x)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x + identity
        x = self.act(x)
        return x


class ResNet(Model):

    def __init__(self, block, layers, base_width=26, scale=4,
                 erase_relu=False, num_classes=1000, stages=(64, 64, 128, 256, 512)):
        super().__init__()
        self.stages = stages

        self.stem = Sequential([
            Conv2d(3, self.stages[0] // 2, kernel_size=3, stride=2,
                   norm='def', act='def'),
            Conv2d(self.stages[0] // 2, self.stages[0] // 2, kernel_size=3,
                   norm='def', act='def'),
            Conv2d(self.stages[0] // 2, self.stages[0], kernel_size=3,
                   norm='def', act='def'),
        ])
        self.maxpool = Pool2d(kernel_size=3, stride=2, type='max')
        self.in_channels = self.stages[0]

        self.layer1 = self._make_layer(
            block, self.stages[1], layers[0], stride=1,
            base_width=base_width, scale=scale, erase_relu=erase_relu)
        self.layer2 = self._make_layer(
            block, self.stages[2], layers[1], stride=2,
            base_width=base_width, scale=scale, erase_relu=erase_relu)
        self.layer3 = self._make_layer(
            block, self.stages[3], layers[2], stride=2,
            base_width=base_width, scale=scale, erase_relu=erase_relu)
        self.layer4 = self._make_layer(
            block, self.stages[4], layers[3], stride=2,
            base_width=base_width, scale=scale, erase_relu=erase_relu)

        self.avgpool = GlobalAvgPool()
        self.fc = Linear(self.in_channels, num_classes)

    def _make_layer(self, block, channels, blocks, stride, **kwargs):
        layers = [block(self.in_channels, channels, stride=stride, start_block=True,
                        **kwargs)]
        self.in_channels = channels * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.in_channels, channels, stride=1,
                                **kwargs))
        return Sequential(layers)

    def call(self, x):
        x = self.stem(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = self.fc(x)
        return x


def resnet50(**kwargs):
    return ResNet(Bottle2neck, [3, 4, 6, 3], **kwargs)

def resnet101(**kwargs):
    return ResNet(Bottle2neck, [3, 4, 23, 3], **kwargs)

def resnet152(**kwargs):
    return ResNet(Bottle2neck, [3, 8, 36, 3], **kwargs)