from hanser.models.common.resnetpp import Bottleneck
from hanser.models.imagenet.iresnet.resnet import _IResNet
from hanser.models.imagenet.stem import SpaceToDepthStem


class IResNet(_IResNet):

    def __init__(self, block, layers, num_classes=1000, channels=(64, 64, 128, 256, 512),
                 drop_path=0, dropout=0, se_reduction=4, se_mode=0):
        stem_channels, *channels = channels
        stem = SpaceToDepthStem(stem_channels)
        super().__init__(stem, block, layers, num_classes, channels,
                         strides=(1, 2, 2, 2), dropout=dropout, se_last=False,
                         drop_path=drop_path, se_reduction=se_reduction, se_mode=se_mode)


def resnet50(**kwargs):
    return IResNet(Bottleneck, [3, 4, 8, 3], **kwargs)