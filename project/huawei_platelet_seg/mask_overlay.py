import os
import numpy as np
from PIL import Image, ImageDraw

def overlay_masks():
    # 定义路径
    labels_dir = r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\runs\segment\labels"
    images_dir = "h:\\pycharm_project\\PI-MAPP\\project\\huawei_platelet_seg\\dataset_demo\\images"
    output_dir = "h:\\pycharm_project\\PI-MAPP\\project\\huawei_platelet_seg\\runs\\masks_my"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理train和val数据集
    for split in ["train", "val"]:
        split_labels_dir = os.path.join(labels_dir, split)
        split_images_dir = os.path.join(images_dir, split)
        split_output_dir = os.path.join(output_dir, split)
        
        os.makedirs(split_output_dir, exist_ok=True)
        
        # 获取所有图像文件
        image_files = [f for f in os.listdir(split_images_dir) if f.endswith(".png")]
        
        for image_file in image_files:
            # 获取图像路径和对应的标签路径
            image_path = os.path.join(split_images_dir, image_file)
            label_path = os.path.join(split_labels_dir, image_file.replace(".png", ".txt"))
            
            # 读取图像
            image = Image.open(image_path)
            width, height = image.size
            
            # 将16位灰度图像转换为8位以便叠加
            if image.mode == "I;16":
                image_array = np.array(image)
                image_array = (image_array / 256).astype(np.uint8)  # 将16位转换为8位
                image = Image.fromarray(image_array, mode="L")
            
            # 创建RGBA图像以便叠加彩色掩码
            image_rgba = image.convert("RGBA")
            
            # 创建掩码层
            mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(mask)
            
            # 读取并绘制标签
            if os.path.exists(label_path):
                with open(label_path, "r") as f:
                    lines = f.readlines()
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 5:  # 至少需要类别和4个坐标点
                        continue
                    
                    # 解析类别和归一化坐标
                    class_id = int(parts[0])
                    coords = list(map(float, parts[1:]))
                    
                    # 将归一化坐标转换为图像坐标
                    points = []
                    for i in range(0, len(coords), 2):
                        x = coords[i] * width
                        y = coords[i+1] * height
                        points.append((x, y))
                    
                    # 绘制多边形掩码 (内部使用#999768，边缘使用#C9C566加深强调)
                    # 内部填充
                    draw.polygon(points, fill=(153, 151, 104, 220))  # #999768 高透明度
                    # 边缘轮廓
                    draw.polygon(points, outline=(201, 197, 102, 255), width=2)  # #C9C566 不透明
            
            # 将掩码叠加到原图上
            result = Image.alpha_composite(image_rgba, mask)
            
            # 转换回RGB并保存
            result_rgb = result.convert("RGB")
            output_path = os.path.join(split_output_dir, image_file)
            result_rgb.save(output_path, format="PNG")
            
            print(f"Processed: {image_file}")

if __name__ == "__main__":
    overlay_masks()
