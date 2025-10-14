import os, time, tqdm, torch, torch.nn as nn
from torch.utils.data import DataLoader
from torchvision.utils import save_image
from model import UNet
from dataset import PairedDataset

def psnr_tensor(img1, img2, max_val=1.):
    mse = torch.mean((img1 - img2) ** 2)
    return 20 * torch.log10(max_val / torch.sqrt(mse))

class PSNRLoss(nn.Module):
    def forward(self, pred, target):
        return -psnr_tensor(pred, target)   # 最大化 PSNR <=> 最小化负 PSNR

def train():
    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cpu' if torch.cuda.is_available() else 'cpu')
    batch = 1          # 1024² 显存占用高，可调 1-2
    epochs = 50
    lr = 1e-3
    train_loader = DataLoader(PairedDataset('H:/pycharm_project/github_projects/NAFNet/datasets/val_data/input-fenkuai','H:/pycharm_project/github_projects/NAFNet/datasets/val_data/gt_fenkuai'),
                              batch_size=batch, shuffle=True, num_workers=4, pin_memory=True)
    val_loader = DataLoader(PairedDataset(r'H:\pycharm_project\github_projects\NAFNet\datasets\val\noise',r'H:\pycharm_project\github_projects\NAFNet\datasets\val\gt'),
                            batch_size=1, shuffle=False)

    model = UNet().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(opt, mode='max', patience=10, factor=0.5)
    criterion = PSNRLoss()

    best_psnr = 0
    os.makedirs('weights', exist_ok=True)

    for epoch in range(1, epochs+1):
        model.train()
        epoch_loss = 0
        for noisy, clean in tqdm.tqdm(train_loader, ncols=60):
            noisy, clean = noisy.to(device), clean.to(device)
            opt.zero_grad()
            pred = model(noisy)
            loss = criterion(pred, clean)
            loss.backward()
            opt.step()
            epoch_loss += loss.item()
        # validation
        model.eval()
        psnr_val = 0
        with torch.no_grad():
            for noisy, clean in val_loader:
                noisy, clean = noisy.to(device), clean.to(device)
                pred = model(noisy)
                psnr_val += psnr_tensor(pred.clamp(0,1), clean).item()
        psnr_val /= len(val_loader)
        scheduler.step(psnr_val)

        print(f'Epoch {epoch:03d} | loss={epoch_loss/len(train_loader):.3f} | Val PSNR={psnr_val:.2f}')
        if psnr_val > best_psnr:
            best_psnr = psnr_val
            torch.save(model.state_dict(), 'weights/best.pth')
            print('  * best checkpoint saved.')

if __name__ == '__main__':
    train()