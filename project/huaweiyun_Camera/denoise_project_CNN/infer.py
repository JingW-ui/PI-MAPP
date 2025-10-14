import os, torch, torchvision.utils as vutils
from PIL import Image
from model import UNet
from dataset import PairedDataset   # 复用 transform
import argparse, time

def load_model(weight_path, device):
    model = UNet()
    model.load_state_dict(torch.load(weight_path, map_location=device))
    model.to(device).eval()
    return model

@torch.no_grad()
def inference_one(model, noisy_path, save_path, device):
    transform = PairedDataset('','').transform
    noisy = transform(Image.open(noisy_path).convert('RGB')).unsqueeze(0).to(device)
    pred = model(noisy).clamp(0,1).cpu()
    vutils.save_image(pred, save_path)

@torch.no_grad()
def inference_folder(model, in_dir, out_dir, device):
    os.makedirs(out_dir, exist_ok=True)
    transform = PairedDataset('','').transform
    for name in os.listdir(in_dir):
        noisy = transform(Image.open(os.path.join(in_dir, name)).convert('RGB')).unsqueeze(0).to(device)
        pred = model(noisy).clamp(0,1).cpu()
        vutils.save_image(pred, os.path.join(out_dir, name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w','--weight', required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-i','--img')
    group.add_argument('-f','--folder')
    parser.add_argument('-o','--out', default='result')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_model(args.weight, device)

    if args.img:
        inference_one(model, args.img, args.out, device)
    else:
        inference_folder(model, args.folder, args.out, device)