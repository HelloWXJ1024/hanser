import functools
import math
from tensorflow.keras import Sequential, Model
from tensorflow.keras.layers import Layer

from hanser.models.layers import Conv2d, Act, Identity, GlobalAvgPool, Linear, Norm, Pool2d
from hanser.models.cifar.res2net.layers import Res2Conv


class GenBottleneck(Layer):
    expansion = 4

    def __init__(self, in_channels, channels, stride,
                 start_block=False, end_block=False, exclude_bn0=False, conv_cls=Conv2d):
        super().__init__()
        out_channels = channels * self.expansion
        width = getattr(self, "width", channels)
        if not start_block and not exclude_bn0:
            self.bn0 = Norm(in_channels)
        if not start_block:
            self.act0 = Act()
        self.conv1 = Conv2d(in_channels, width, kernel_size=1)
        self.bn1 = Norm(width)
        self.act1 = Act()
        self.conv2 = conv_cls(
            in_channels=width, out_channels=width, kernel_size=3, stride=stride,
            norm='def', act='def', start_block=start_block)
        self.conv3 = Conv2d(width, out_channels, kernel_size=1)

        if start_block:
            self.bn3 = Norm(out_channels)

        if end_block:
            self.bn3 = Norm(out_channels)
            self.act3 = Act()

        if stride != 1 or in_channels != out_channels:
            shortcut = []
            if stride != 1:
                shortcut.append(Pool2d(2, 2, type='avg'))
            shortcut.append(
                Conv2d(in_channels, out_channels, kernel_size=1, norm='def'))
            self.shortcut = Sequential(shortcut)
        else:
            self.shortcut = Identity()
        self.start_block = start_block
        self.end_block = end_block
        self.exclude_bn0 = exclude_bn0

    def call(self, x):
        identity = self.shortcut(x)
        if self.start_block:
            x = self.conv1(x)
        else:
            if not self.exclude_bn0:
                x = self.bn0(x)
            x = self.act0(x)
            x = self.conv1(x)
        x = self.bn1(x)
        x = self.act1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        if self.start_block:
            x = self.bn3(x)
        x = x + identity
        if self.end_block:
            x = self.bn3(x)
            x = self.act3(x)
        return x


class GenIResNet(Model):

    def __init__(self, block, layers, num_classes=10, stages=(64, 64, 128, 256), **kwargs):
        super().__init__()
        self.stages = stages

        self.stem = Conv2d(3, self.stages[0], kernel_size=3, norm='def', act='def')
        self.in_channels = self.stages[0]

        self.layer1 = self._make_layer(
            block, self.stages[1], layers[0], stride=1, **kwargs)
        self.layer2 = self._make_layer(
            block, self.stages[2], layers[1], stride=2, **kwargs)
        self.layer3 = self._make_layer(
            block, self.stages[3], layers[2], stride=2, **kwargs)

        self.avgpool = GlobalAvgPool()
        self.fc = Linear(self.in_channels, num_classes)

    def _make_layer(self, block, channels, blocks, stride, **kwargs):
        layers = [block(self.in_channels, channels, stride=stride, start_block=True,
                        **kwargs)]
        self.in_channels = channels * block.expansion
        for i in range(1, blocks):
            layers.append(block(self.in_channels, channels, stride=1,
                                exclude_bn0=i == 1, end_block=i == blocks - 1,
                                **kwargs))
        return Sequential(layers)


    def call(self, x):
        x = self.stem(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)

        x = self.avgpool(x)
        x = self.fc(x)
        return x


class Bottle2neck(GenBottleneck):

    def __init__(self, in_channels, channels, stride, base_width, scale, start_block=False, end_block=False,
                 exclude_bn0=False):
        self.width = lambda: math.floor(channels * (base_width / 64)) * scale
        conv_cls = functools.partial(Res2Conv, scale=scale, groups=1)
        super().__init__(in_channels, channels, stride, start_block, end_block, exclude_bn0, conv_cls=conv_cls)


class IRes2Net(GenIResNet):

    def __init__(self, depth, base_width=26, scale=4, num_classes=10, stages=(64, 64, 128, 256)):
        layers = [(depth - 2) // 9] * 3
        super().__init__(Bottle2neck, layers, num_classes, stages,
                         base_width=base_width, scale=scale)


class IRes2Net(GenIResNet):

    def __init__(self, depth, base_width=26, scale=4, num_classes=10, stages=(64, 64, 128, 256)):
        layers = [(depth - 2) // 9] * 3
        super().__init__(Bottle2neck, layers, num_classes, stages,
                         base_width=base_width, scale=scale)
