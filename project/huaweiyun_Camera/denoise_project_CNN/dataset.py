import os
from torch.utils.data import Dataset
from PIL import Image
import torchvision.transforms as T

class PairedDataset(Dataset):
    def __init__(self, gt_dir, noisy_dir, split='train'):
        self.gt_names = sorted(os.listdir(gt_dir))
        self.noisy_names = sorted(os.listdir(noisy_dir))
        assert len(self.gt_names) == len(self.noisy_names)
        self.gt_dir, self.noisy_dir = gt_dir, noisy_dir
        self.transform = T.Compose([
            T.ToTensor(),               # 0-1
            T.Normalize(mean=[0.,0.,0.], std=[1.,1.,1.])  # 保持 0-1
        ])

    def __len__(self):
        return len(self.gt_names)

    def __getitem__(self, idx):
        gt = Image.open(os.path.join(self.gt_dir, self.gt_names[idx])).convert('RGB')
        noisy = Image.open(os.path.join(self.noisy_dir, self.noisy_names[idx])).convert('RGB')
        return self.transform(noisy), self.transform(gt)