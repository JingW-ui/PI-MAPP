import os
import torch
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms
from model import DenoiseCNN
import glob


class Denoiser:
    def __init__(self, model_path):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = DenoiseCNN().to(self.device)

        # 加载模型权重
        checkpoint = torch.load(model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize((1024, 1024)),
            transforms.ToTensor(),
        ])

        self.inverse_transform = transforms.ToPILImage()

    def denoise_single_image(self, image_path, output_path=None):
        """对单张图像进行去噪"""
        # 读取图像
        if isinstance(image_path, str):
            image = Image.open(image_path).convert('RGB')
        else:
            image = image_path

        original_size = image.size
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 推理
        with torch.no_grad():
            denoised_tensor = self.model(image_tensor)

        # 转换回PIL图像
        denoised_image = self.inverse_transform(denoised_tensor.squeeze(0).cpu())
        denoised_image = denoised_image.resize(original_size, Image.Resampling.LANCZOS)

        # 保存结果
        if output_path:
            denoised_image.save(output_path)
            print(f"Denoised image saved to: {output_path}")

        return denoised_image

    def denoise_folder(self, input_folder, output_folder):
        """对文件夹中的所有图像进行去噪"""
        os.makedirs(output_folder, exist_ok=True)

        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_paths = []

        for extension in image_extensions:
            image_paths.extend(glob.glob(os.path.join(input_folder, extension)))
            image_paths.extend(glob.glob(os.path.join(input_folder, extension.upper())))

        print(f"Found {len(image_paths)} images in {input_folder}")

        for image_path in image_paths:
            filename = os.path.basename(image_path)
            output_path = os.path.join(output_folder, f"denoised_{filename}")

            try:
                self.denoise_single_image(image_path, output_path)
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

        print(f"All images processed. Results saved to: {output_folder}")


def calculate_psnr_numpy(img1, img2):
    """计算两幅图像的PSNR值"""
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(255.0 / np.sqrt(mse))


if __name__ == "__main__":
    # 示例用法
    denoiser = Denoiser('checkpoints/best_model.pth')

    # 测试单张图像
    denoiser.denoise_single_image('test_image.jpg', 'denoised_test_image.jpg')

    # 测试文件夹
    denoiser.denoise_folder('test_images', 'denoised_results')