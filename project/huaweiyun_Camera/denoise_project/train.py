import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import numpy as np
import cv2
from model import DenoiseCNN
import time


class NightDataset(Dataset):
    def __init__(self, gt_dir, noise_dir, transform=None):
        self.gt_dir = gt_dir
        self.noise_dir = noise_dir
        self.transform = transform
        self.gt_images = sorted([f for f in os.listdir(gt_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
        self.noise_images = sorted([f for f in os.listdir(noise_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])

    def __len__(self):
        return len(self.gt_images)

    def __getitem__(self, idx):
        gt_path = os.path.join(self.gt_dir, self.gt_images[idx])
        noise_path = os.path.join(self.noise_dir, self.noise_images[idx])

        gt_image = Image.open(gt_path).convert('RGB')
        noise_image = Image.open(noise_path).convert('RGB')

        if self.transform:
            gt_image = self.transform(gt_image)
            noise_image = self.transform(noise_image)

        return noise_image, gt_image


def calculate_psnr(img1, img2):
    """计算PSNR值"""
    mse = torch.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * torch.log10(1.0 / torch.sqrt(mse))


class PSNRLoss(nn.Module):
    def __init__(self):
        super(PSNRLoss, self).__init__()

    def forward(self, output, target):
        return -calculate_psnr(output, target)


def train_model(gt_dir, noise_dir, epochs=100, batch_size=4, lr=1e-4):
    # 设备配置
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    # 数据变换
    transform = transforms.Compose([
        transforms.Resize((1024, 1024)),
        transforms.ToTensor(),
    ])

    # 数据集和数据加载器
    dataset = NightDataset(gt_dir, noise_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)

    # 模型
    model = DenoiseCNN().to(device)
    criterion = PSNRLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)

    # 训练记录
    best_psnr = -float('inf')
    train_losses = []

    # 创建保存目录
    os.makedirs('checkpoints', exist_ok=True)

    print("Starting training...")

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        epoch_psnr = 0

        for batch_idx, (noise_imgs, gt_imgs) in enumerate(dataloader):
            noise_imgs = noise_imgs.to(device)
            gt_imgs = gt_imgs.to(device)

            # 前向传播
            outputs = model(noise_imgs)
            loss = criterion(outputs, gt_imgs)

            # 反向传播
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # 计算PSNR
            with torch.no_grad():
                batch_psnr = calculate_psnr(outputs, gt_imgs)

            epoch_loss += loss.item()
            epoch_psnr += batch_psnr.item()

            if batch_idx % 10 == 0:
                print(f'Epoch [{epoch + 1}/{epochs}], Batch [{batch_idx + 1}/{len(dataloader)}], '
                      f'Loss: {loss.item():.4f}, PSNR: {batch_psnr:.2f}dB')

        avg_loss = epoch_loss / len(dataloader)
        avg_psnr = epoch_psnr / len(dataloader)
        train_losses.append(avg_loss)

        print(f'Epoch [{epoch + 1}/{epochs}], Average Loss: {avg_loss:.4f}, Average PSNR: {avg_psnr:.2f}dB')

        # 保存最佳模型
        if avg_psnr > best_psnr:
            best_psnr = avg_psnr
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'loss': avg_loss,
                'psnr': avg_psnr
            }, 'checkpoints/best_model.pth')
            print(f'Best model saved with PSNR: {avg_psnr:.2f}dB')

        scheduler.step(avg_loss)

    print("Training completed!")
    return model, train_losses


if __name__ == "__main__":
    # 示例用法
    gt_dir = "path/to/gt_images"
    noise_dir = "path/to/noise_images"
    train_model(gt_dir, noise_dir)