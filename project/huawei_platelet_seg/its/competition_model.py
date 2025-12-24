import json
import os
import cv2
import numpy as np
from model import HuaWeiSegModel
from typing import List, Dict, Any

class Competition:
    def __init__(self, model_path: str = "./baseline/best.pt"):
        """
        初始化分割模型
        Args:
            model_path: 您提供的分割模型路径
        """
        # 验证模型文件是否存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")
        
        # 使用您提供的模型路径
        self.model = HuaWeiSegModel(model_path)
    
    def get_results(self, testset_path: str, output_dir: str = None) -> str:
        """
        对测试集文件夹中的所有图片进行分割推理并为每张图片生成单独的JSON文件
        Args:
            testset_path: 测试集图片文件夹路径
            output_dir: 输出JSON文件的目录，默认为None时在测试集同级目录创建results文件夹
        Returns:
            message: 处理结果信息
        """
        # 验证文件夹路径是否存在
        if not os.path.exists(testset_path):
            return f"错误: 测试集文件夹路径不存在: {testset_path}"
        
        # 设置输出目录
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(testset_path), "results")
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取文件夹中的所有图片文件
        image_files = self._get_image_files(testset_path)
        if not image_files:
            return f"错误: 测试集文件夹中没有找到图片文件: {testset_path}"
        
        successful_count = 0
        error_files = []
        
        try:
            # 对每张图片进行分割推理
            for i, image_file in enumerate(image_files):
                print(f"处理图片 {i+1}/{len(image_files)}: {image_file}")
                image_path = os.path.join(testset_path, image_file)
                
                try:
                    # 处理单张图片
                    image_result = self._process_single_image(image_path)
                    # 生成JSON文件名（与图片同名但扩展名为.json）
                    json_filename = os.path.splitext(image_file)[0] + ".json"
                    json_filepath = os.path.join(output_dir, json_filename)
                    
                    # 保存JSON文件
                    with open(json_filepath, "w", encoding="utf-8") as f:
                        json.dump(image_result, f, indent=2, ensure_ascii=False)
                    
                    successful_count += 1
                    print(f"已生成: {json_filename}")
                    
                except Exception as e:
                    error_msg = f"处理图片 {image_file} 时出错: {str(e), image_result}"
                    print(error_msg)
                    error_files.append((image_file, error_msg))

            # 生成处理结果报告
            result_message = f"成功处理 {successful_count} 张图片，生成的JSON文件保存在: {output_dir}"
            if error_files:
                result_message += f"\n处理失败的图片 ({len(error_files)} 张):"
                for file, error in error_files:
                    result_message += f"\n  - {file}: {error}"
            
            return result_message
            
        except Exception as e:
            return f"处理测试集失败: {str(e)}"

    
    def _get_image_files(self, folder_path: str) -> List[str]:
        """
        获取文件夹中的所有图片文件
        Args:
            folder_path: 文件夹路径
        Returns:
            image_files: 图片文件列表
        """
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
        
        image_files = []
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in image_extensions:
                    image_files.append(file)
        
        return sorted(image_files)  # 按文件名排序
    
    def _process_single_image(self, image_path: str) -> Dict[str, Any]:
        """
        处理单张图片的分割推理
        Args:
            image_path: 单张图片路径
        Returns:
            segmentation_data: 单张图片的分割结果（只包含指定的三个键）
        """
        # 验证图片文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        
        # 执行模型分割推理
        results = self.model(image_path)
        
        # 初始化分割结果（只包含指定的三个键）
        segmentation_data = {
            "segmentation_classes": [],
            "segmentation_polygons": [],
            "segmentation_scores": []
        }
        
        # 处理每个分割结果
        for r in results:
            if hasattr(r, 'masks') and r.masks is not None:
                masks = r.masks
                boxes = r.boxes if hasattr(r, 'boxes') and r.boxes is not None else None
                
                # 处理每个分割掩码
                for j, mask in enumerate(masks):
                    # 获取类别信息
                    class_id = -1
                    class_name = "unknown"
                    confidence = 0.0
                    
                    if boxes is not None and j < len(boxes):
                        box = boxes[j]
                        if hasattr(box, 'cls') and box.cls is not None:
                            class_id = int(box.cls.item())
                            # class_name = self.model.names[class_id] if hasattr(self.model, 'names') else f"class_{class_id}"
                            class_name = '0'
                        if hasattr(box, 'conf') and box.conf is not None:
                            confidence = round(box.conf.item(), 6)
                    
                    # 将分割掩码转换为多边形
                    polygon = self._mask_to_polygon(mask.data[0].cpu().numpy())
                    
                    if polygon and len(polygon) > 0:
                        segmentation_data["segmentation_classes"].append(class_name)
                        segmentation_data["segmentation_polygons"].append(polygon)
                        segmentation_data["segmentation_scores"].append(confidence)
        
        return segmentation_data
    
    def _mask_to_polygon(self, mask: np.ndarray) -> List[List[int]]:
        """
        将分割掩码转换为多边形坐标
        Args:
            mask: 二值分割掩码
        Returns:
            polygon: 多边形坐标列表 [[x1, y1], [x2, y2], ...]
        """
        try:
            # 确保掩码是uint8类型
            mask_uint8 = (mask * 255).astype(np.uint8)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return []
            
            # 取最大的轮廓
            largest_contour = max(contours, key=cv2.contourArea)
            
            # 简化轮廓点
            epsilon = 0.001 * cv2.arcLength(largest_contour, True)
            simplified_contour = cv2.approxPolyDP(largest_contour, epsilon, True)
            
            # 转换为列表格式
            polygon = []
            for point in simplified_contour:
                x, y = point[0]
                polygon.append([int(x), int(y)])
            
            return polygon
            
        except Exception as e:
            print(f"掩码转换多边形失败: {str(e)}")
            return []


# 使用示例
if __name__ == "__main__":
    try:
        # 创建竞赛实例，使用您提供的模型路径
        model_path = r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\runs\segment\train\weights\best.pt"  # 替换为您提供的模型路径
        competition = Competition(model_path)
        
        # 对测试集文件夹中的所有图片进行分割推理
        testset_path = r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\dataset_demo\images\val"  # 替换为您的测试集文件夹路径
        output_dir = r"H:\pycharm_project\PI-MAPP\project\huawei_platelet_seg\runs\results"  # 可选：指定输出目录
        
        # 处理测试集并生成JSON文件
        result_message = competition.get_results(testset_path, output_dir)
        print(result_message)
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")