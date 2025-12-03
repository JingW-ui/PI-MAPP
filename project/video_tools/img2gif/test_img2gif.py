#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Img2Gif 测试脚本
用于测试Img2Gif应用的基本功能
"""

import sys
import os
import tempfile
from PIL import Image
from PyQt5.QtWidgets import QApplication
from img2gif import Img2GifApp, GifConverterThread


def create_test_images():
    """创建测试用的图片文件"""
    temp_dir = tempfile.mkdtemp()
    image_paths = []
    
    # 创建几张测试图片
    for i in range(3):
        img = Image.new('RGB', (200, 200), color=(i*50, i*50, i*50))
        file_path = os.path.join(temp_dir, f'test_image_{i+1}.png')
        img.save(file_path)
        image_paths.append(file_path)
    
    return image_paths, temp_dir


def test_converter_thread():
    """测试GIF转换线程"""
    print("创建测试图片...")
    image_paths, temp_dir = create_test_images()
    
    # 创建输出文件路径
    output_path = os.path.join(temp_dir, 'test_output.gif')
    
    print(f"测试图片路径: {image_paths}")
    print(f"输出GIF路径: {output_path}")
    
    # 创建并启动转换线程
    thread = GifConverterThread(image_paths, output_path, 500)
    
    # 连接信号
    def on_progress(value):
        print(f"转换进度: {value}%")
    
    def on_finished(path):
        print(f"转换完成! GIF保存在: {path}")
        # 验证GIF文件是否创建成功
        if os.path.exists(path):
            print("GIF文件创建成功!")
        else:
            print("错误: GIF文件未创建")
    
    def on_error(error_msg):
        print(f"转换出错: {error_msg}")
    
    thread.progress_updated.connect(on_progress)
    thread.conversion_finished.connect(on_finished)
    thread.error_occurred.connect(on_error)
    
    # 启动线程
    thread.start()
    
    # 等待线程完成
    thread.wait()
    
    # 清理临时文件
    for path in image_paths:
        os.remove(path)
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rmdir(temp_dir)
    
    print("测试完成!")


def main():
    """主函数"""
    print("开始测试Img2Gif应用...")
    
    # 测试转换线程
    test_converter_thread()
    
    print("所有测试完成!")


if __name__ == '__main__':
    main()