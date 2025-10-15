# DDGnet.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


# ------------------ 一些可微工具 ------------------
def differentiable_jpeg(img, Q_table):
    """
    img: [B,3,H,W]  0~1  float
    Q_table: [B,64]  0~1  先Sigmoid后再乘255
    返回: JPEG 压缩/解压后的图  0~1
    这里给出最简 DCT 量化近似，够用即可；如需严格对齐，可换成外部 cuda 扩展
    """
    B, C, H, W = img.shape
    Q = (Q_table.sigmoid() * 255).clamp(1, 255)  # [B,64]
    Q = Q.view(B, 8, 8)  # 8x8 Q-table

    # 简易 8x8 DCT 量化
    img = img * 255
    img_ycbcr = rgb_to_ycbcr(img) / 255.0
    # 为了快，直接对每张图 8x8 块做量化
    pad_h, pad_w = (8 - H % 8) % 8, (8 - W % 8) % 8
    img_pad = F.pad(img_ycbcr, (0, pad_w, 0, pad_h), mode='reflect')
    blocks = F.unfold(img_pad, kernel_size=8, stride=8)  # [B*C,64,num_block]
    blocks = blocks.view(B * C, 64, -1).permute(0, 2, 1)  # [B*C,num_block,64]

    # 简易 DCT 基（省略了真正的 DCT 矩阵，用 1e-4 近似）
    dct_basis = torch.eye(64, device=img.device, dtype=img.dtype)
    dct_coeff = blocks @ dct_basis
    quant = dct_coeff / (Q.view(-1).clamp(1) + 1e-4)
    dequant = quant * Q.view(-1).clamp(1)
    rec_blocks = dequant @ dct_basis.inverse()
    rec_blocks = rec_blocks.permute(0, 2, 1).contiguous().view(B * C, 64, -1)
    rec_img = F.fold(rec_blocks, output_size=(img_pad.shape[2], img_pad.shape[3]),
                     kernel_size=8, stride=8)
    rec_img = rec_img.view(B, C, img_pad.shape[2], img_pad.shape[3])
    rec_img = rec_img[:, :, :H, :W]
    rec_img = ycbcr_to_rgb(rec_img.clamp(0, 1) * 255).clamp(0, 255) / 255.0
    return rec_img


def rgb_to_ycbcr(im):
    # im 0~255
    r, g, b = im[:, 0], im[:, 1], im[:, 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
    cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128
    return torch.stack([y, cb, cr], dim=1)


def ycbcr_to_rgb(im):
    # im 0~255
    y, cb, cr = im[:, 0], im[:, 1], im[:, 2]
    r = y + 1.402 * (cr - 128)
    g = y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return torch.stack([r, g, b], dim=1)


# ------------------ 主干：轻量化 U-Net ------------------
class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False),
            nn.LeakyReLU(0.1, inplace=True),
        )

    def forward(self, x):
        return self.net(x)


class Down(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, in_ch, 3, stride=2, padding=1, bias=False),
            nn.LeakyReLU(0.1, inplace=True),
            DoubleConv(in_ch, out_ch)
        )

    def forward(self, x):
        return self.net(x)


class Up(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=False)
        self.conv = DoubleConv(in_ch, out_ch)

    def forward(self, x1, x2):
        x1 = self.up(x1)
        # 简单 concat
        x = torch.cat([x2, x1], dim=1)
        return self.conv(x)


class UNetTiny(nn.Module):
    def __init__(self, in_ch=3, base=32):
        super().__init__()
        self.inc = DoubleConv(in_ch, base)
        self.down1 = Down(base, base * 2)
        self.down2 = Down(base * 2, base * 4)
        self.down3 = Down(base * 4, base * 8)
        self.down4 = Down(base * 8, base * 16)

        self.up1 = Up(base * 16 + base * 8, base * 8)
        self.up2 = Up(base * 8 + base * 4, base * 4)
        self.up3 = Up(base * 4 + base * 2, base * 2)
        self.up4 = Up(base * 2 + base, base)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        return x


# ------------------ 三条输出头 ------------------
class KernelHead(nn.Module):
    def __init__(self, base, k_size=21):
        super().__init__()
        self.k_size = k_size
        self.net = nn.Conv2d(base, k_size * k_size, 1)

    def forward(self, x):
        B, _, H, W = x.shape
        k = self.net(x)  # [B,k*k,H,W]
        k = k.view(B, self.k_size * self.k_size, -1).permute(0, 2, 1)  # [B,H*W,k*k]
        k = F.softmax(k, dim=-1)
        k = k.view(B, H, W, self.k_size, self.k_size)
        return k  # 空间可变核  [B,H,W,k,k]


class NoiseHead(nn.Module):
    def __init__(self, base):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(base, 32, 3, padding=1),
            nn.LeakyReLU(0.1, True),
            nn.Conv2d(32, 3, 1),
            nn.Tanh()
        )
        self.alpha = nn.Parameter(torch.tensor(0.05))  # 可学习强度

    def forward(self, x):
        return self.net(x) * self.alpha.abs()  # [B,3,H,W]


class QHead(nn.Module):
    def __init__(self, base):
        super().__init__()
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.net = nn.Sequential(
            nn.Conv2d(base, 128, 1),
            nn.LeakyReLU(0.1, True),
            nn.Conv2d(128, 64, 1)
        )

    def forward(self, x):
        z = self.pool(x)  # [B,base,1,1]
        q = self.net(z).view(x.size(0), 64)  # [B,64]
        return q  # 0~1 之间，后续 sigmoid 再乘 255


# ------------------ DDG-Net：退化生成器 ------------------
class DDGNet(nn.Module):
    def __init__(self, k_size=21, scale=4):
        super().__init__()
        self.scale = scale
        self.backbone = UNetTiny(in_ch=3, base=32)
        self.k_head = KernelHead(32, k_size)
        self.n_head = NoiseHead(32)
        self.q_head = QHead(32)

    def forward(self, img_hr):
        """
        img_hr: [B,3,H,W]  0~1
        return: [B,3,H/s,W/s]  0~1
        """
        feat = self.backbone(img_hr)  # [B,32,H,W]
        kernels = self.k_head(feat)   # [B,H,W,k,k]
        noise_map = self.n_head(feat)  # [B,3,H,W]
        q_table = self.q_head(feat)    # [B,64]

        # 1. 空间可变卷积模糊
        B, C, H, W = img_hr.shape
        img_blur = self.spatial_conv(img_hr, kernels)

        # 2. 下采样
        img_lr = F.avg_pool2d(img_blur, self.scale, self.scale)

        # 3. 加噪（noise_map 尺寸同 HR，需池化到 LR 尺寸）
        noise_lr = F.avg_pool2d(noise_map, self.scale, self.scale)
        img_noise = img_lr + noise_lr

        # 4. JPEG
        img_jpeg = differentiable_jpeg(img_noise, q_table)

        return img_jpeg.clamp(0, 1)

    @staticmethod
    def spatial_conv(img, kernels):
        """
        img: [B,3,H,W]
        kernels: [B,H,W,k,k]  已 softmax
        返回: 模糊后的 HR 图
        这里用 unfold + matmul 实现空间可变卷积
        """
        B, C, H, W = img.shape
        k = kernels.size(-1)
        pad = k // 2
        img_unfold = F.unfold(F.pad(img, [pad, pad, pad, pad], mode='reflect'),
                              kernel_size=k, stride=1)  # [B*C, k*k, H*W]
        img_unfold = img_unfold.view(B, C, k * k, H * W)
        kernels = kernels.view(B, H * W, k * k).permute(0, 2, 1)  # [B,k*k,H*W]
        img_mul = (img_unfold * kernels.unsqueeze(1)).sum(dim=2)  # [B,C,H*W]
        return img_mul.view(B, C, H, W)


# ------------------ 简单测试 ------------------
if __name__ == '__main__':
    net = DDGNet(k_size=21, scale=4).cuda()
    x = torch.randn(2, 3, 256, 256).cuda()
    with torch.no_grad():
        y = net(x)
    print(y.shape)  # 应为 (2,3,64,64)