import torch
import torch.nn as nn
import torch.nn.functional as F


class DenoiseCNN(nn.Module):
    def __init__(self, in_channels=3, features=64):
        super(DenoiseCNN, self).__init__()

        # 编码器部分
        self.enc1 = self._block(in_channels, features)
        self.enc2 = self._block(features, features * 2)
        self.enc3 = self._block(features * 2, features * 4)
        self.enc4 = self._block(features * 4, features * 8)

        # 解码器部分
        self.dec1 = self._block(features * 8, features * 4)
        self.dec2 = self._block(features * 4, features * 2)
        self.dec3 = self._block(features * 2, features)
        self.dec4 = nn.Conv2d(features, in_channels, kernel_size=3, padding=1)

        self.pool = nn.MaxPool2d(2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)

    def _block(self, in_channels, out_channels):
        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        # 编码
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))

        # 解码
        d1 = self.dec1(e4)
        d2 = self.dec2(self.upsample(d1) + e3)
        d3 = self.dec3(self.upsample(d2) + e2)
        d4 = self.dec4(self.upsample(d3) + e1)

        return torch.sigmoid(d4)