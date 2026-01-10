import sys
import os
import logging
from datetime import datetime
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox,
                             QSpinBox, QGroupBox, QProgressBar, QSlider, QTextEdit)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'img2gif.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon


class GifConverterThread(QThread):
    """后台线程用于处理GIF转换"""
    progress_updated = pyqtSignal(int)
    conversion_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, image_paths, output_path, duration, scale_factor=1.0):
        super().__init__()
        self.image_paths = image_paths
        self.output_path = output_path
        self.duration = duration
        self.scale_factor = scale_factor
    
    def run(self):
        try:
            images = []
            total_images = len(self.image_paths)
            
            for i, path in enumerate(self.image_paths):
                # 发送进度更新信号
                progress = int((i / total_images) * 100)
                self.progress_updated.emit(progress)
                
                # 打开图片并添加到列表
                img = Image.open(path)
                # 转换为RGB模式（去除alpha通道）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 根据缩放因子调整图像大小
                if self.scale_factor != 1.0:
                    width, height = img.size
                    new_width = int(width * self.scale_factor)
                    new_height = int(height * self.scale_factor)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                images.append(img)
            
            # 保存为GIF
            if images:
                images[0].save(
                    self.output_path,
                    save_all=True,
                    append_images=images[1:],
                    duration=self.duration,
                    loop=0,
                    optimize=True,  # 优化GIF大小
                    quality=90  # 设置质量参数
                )
                self.conversion_finished.emit(self.output_path)
            else:
                self.error_occurred.emit("没有有效的图片可以转换")
                
        except Exception as e:
            self.error_occurred.emit(str(e))


class Img2GifApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.converter_thread = None
        self.init_ui()
        logger.info("图片转GIF工具启动")
    
    def init_ui(self):
        self.setWindowTitle('图片转GIF工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        try:
            # 获取当前脚本的目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建图标路径
            icon_path = os.path.join(current_dir, 'img', 'app.ico')
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logger.info(f"成功加载图标: {icon_path}")
            else:
                logger.warning(f"图标文件不存在: {icon_path}")
        except Exception as e:
            logger.error(f"加载图标时发生错误: {str(e)}")
            
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 创建顶部按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(10, 10, 10, 10)
        
        self.add_images_btn = QPushButton('添加图片')
        self.add_images_btn.clicked.connect(self.add_images)
        self.add_images_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.remove_image_btn = QPushButton('移除选中图片')
        self.remove_image_btn.clicked.connect(self.remove_selected_image)
        self.remove_image_btn.setEnabled(False)
        self.remove_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.clear_images_btn = QPushButton('清空所有图片')
        self.clear_images_btn.clicked.connect(self.clear_images)
        self.clear_images_btn.setEnabled(False)
        self.clear_images_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.convert_btn = QPushButton('转换为GIF')
        self.convert_btn.clicked.connect(self.convert_to_gif)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # 注意：save_gif_btn已在预览区域创建，这里只需要设置样式
        pass
        
        button_layout.addWidget(self.add_images_btn)
        button_layout.addWidget(self.remove_image_btn)
        button_layout.addWidget(self.clear_images_btn)
        button_layout.addWidget(self.convert_btn)
        
        # 创建图片列表区域
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SingleSelection)
        self.image_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.image_list.setMinimumHeight(150)
        self.image_list.setMaximumHeight(250)
        
        # 创建预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.setSpacing(15)
        preview_layout.setContentsMargins(10, 10, 10, 10)
        self.preview_label = QLabel("请选择一张图片进行预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        preview_layout.addWidget(self.preview_label)
        
        # 添加GIF预览和保存区域
        self.gif_preview_label = QLabel("转换完成后将在此显示GIF预览")
        self.gif_preview_label.setAlignment(Qt.AlignCenter)
        self.gif_preview_label.setMinimumSize(400, 300)
        self.gif_preview_label.setVisible(False)
        preview_layout.addWidget(self.gif_preview_label)
        
        # 添加GIF大小显示和保存按钮
        save_layout = QHBoxLayout()
        self.gif_size_label = QLabel("GIF大小:")
        self.gif_size_label.setVisible(False)
        self.save_gif_btn = QPushButton("保存GIF")
        self.save_gif_btn.setVisible(False)
        self.save_gif_btn.clicked.connect(self.save_gif)
        self.save_gif_btn.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        save_layout.addWidget(self.gif_size_label)
        save_layout.addWidget(self.save_gif_btn)
        save_layout.addStretch()
        preview_layout.addLayout(save_layout)
        
        # 创建设置区域
        settings_group = QGroupBox("转换设置")
        settings_layout = QHBoxLayout(settings_group)
        
        duration_label = QLabel("每帧持续时间(ms):")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(10, 5000)
        self.duration_spinbox.setValue(500)
        self.duration_spinbox.setSingleStep(100)
        
        # 添加尺寸缩放滑块
        size_label = QLabel("图片尺寸比例:")
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 100)  # 10% 到 100%
        self.size_slider.setValue(100)  # 默认100%
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(10)
        
        self.size_label_display = QLabel("100%")  # 显示当前百分比
        
        settings_layout.addWidget(duration_label)
        settings_layout.addWidget(self.duration_spinbox)
        
        settings_layout.addWidget(size_label)
        settings_layout.addWidget(self.size_slider)
        settings_layout.addWidget(self.size_label_display)
        
        settings_layout.addStretch()
        
        # 连接滑块值变化信号
        self.size_slider.valueChanged.connect(self.on_size_slider_changed)
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # 添加所有组件到主布局
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.image_list)
        main_layout.addWidget(preview_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(self.progress_bar)
        
        # 连接列表项点击事件
        self.image_list.itemClicked.connect(self.show_preview)
    
    def add_images(self):
        """添加图片文件"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片文件",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if file_paths:
            added_count = 0
            for path in file_paths:
                if path not in self.image_paths:
                    self.image_paths.append(path)
                    # 只显示文件名
                    file_name = os.path.basename(path)
                    self.image_list.addItem(file_name)
                    added_count += 1
            
            logger.info(f"添加了 {added_count} 张图片")
            
            # 更新按钮状态
            self.update_button_states()
    
    def remove_selected_image(self):
        """移除选中的图片"""
        current_row = self.image_list.currentRow()
        if current_row >= 0:
            # 获取要移除的图片路径
            removed_path = self.image_paths[current_row]
            removed_name = os.path.basename(removed_path)
            
            # 移除数据和列表项
            del self.image_paths[current_row]
            self.image_list.takeItem(current_row)
            
            logger.info(f"移除了图片: {removed_name}")
            
            # 清空预览
            self.preview_label.setText("请选择一张图片进行预览")
            
            # 更新按钮状态
            self.update_button_states()
    
    def clear_images(self):
        """清空所有图片"""
        logger.info(f"清空了所有 {len(self.image_paths)} 张图片")
        self.image_paths.clear()
        self.image_list.clear()
        self.preview_label.setText("请选择一张图片进行预览")
        self.update_button_states()
    
    def convert_to_gif(self):
        """转换为GIF"""
        if not self.image_paths:
            QMessageBox.warning(self, "警告", "请先添加图片文件")
            logger.warning("尝试转换，但未添加任何图片")
            return
        
        logger.info(f"开始转换GIF，共 {len(self.image_paths)} 张图片")
        
        # 禁用相关控件
        self.set_controls_enabled(False)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 获取设置参数
        duration = self.duration_spinbox.value()
        scale_factor = self.size_slider.value() / 100.0
        logger.info(f"转换参数 - 每帧持续时间: {duration}ms, 尺寸比例: {int(scale_factor*100)}%")
        
        # 创建临时文件路径
        import tempfile
        self.temp_gif_path = tempfile.mktemp(suffix='.gif')
        
        # 启动转换线程
        self.converter_thread = GifConverterThread(
            self.image_paths, self.temp_gif_path, duration, scale_factor
        )
        self.converter_thread.progress_updated.connect(self.update_progress)
        self.converter_thread.conversion_finished.connect(self.on_conversion_finished)
        self.converter_thread.error_occurred.connect(self.on_conversion_error)
        self.converter_thread.start()
        
        # 隐藏之前的GIF预览
        self.gif_preview_label.setVisible(False)
        self.save_gif_btn.setVisible(False)
        self.gif_size_label.setVisible(False)
    
    def show_gif_preview(self, gif_path):
        """显示GIF预览"""
        pixmap = QPixmap(gif_path)
        if not pixmap.isNull():
            # 缩放GIF以适应预览区域
            pixmap = pixmap.scaled(
                self.gif_preview_label.width(),
                self.gif_preview_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.gif_preview_label.setPixmap(pixmap)
            self.gif_preview_label.setText("")
        else:
            self.gif_preview_label.setText("无法加载GIF预览")
        
        # 显示GIF预览标签
        self.gif_preview_label.setVisible(True)
        # 隐藏单张图片预览
        self.preview_label.setVisible(False)
    
    def save_gif(self):
        """保存GIF文件"""
        if not hasattr(self, 'temp_gif_path'):
            QMessageBox.warning(self, "警告", "没有可保存的GIF文件")
            logger.warning("尝试保存，但没有可保存的GIF文件")
            return
        
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存GIF文件",
            "output.gif",
            "GIF Files (*.gif)"
        )
        
        if output_path:
            try:
                # 复制临时文件到目标路径
                import shutil
                shutil.copy2(self.temp_gif_path, output_path)
                
                logger.info(f"GIF保存成功，路径: {output_path}, 大小: {self.gif_size} MB")
                
                # 显示保存成功消息
                QMessageBox.information(
                    self,
                    "保存成功",
                    f"GIF已成功保存到:\n{output_path}"
                )
                
                # 清理临时文件
                os.remove(self.temp_gif_path)
                logger.info(f"临时文件已清理: {self.temp_gif_path}")
                
                # 隐藏GIF预览和保存区域
                self.gif_preview_label.setVisible(False)
                self.save_gif_btn.setVisible(False)
                self.gif_size_label.setVisible(False)
                
                # 显示单张图片预览
                self.preview_label.setVisible(True)
                
            except Exception as e:
                logger.error(f"GIF保存失败: {str(e)}")
                QMessageBox.critical(
                    self,
                    "保存失败",
                    f"保存过程中发生错误:\n{str(e)}"
                )
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_conversion_finished(self, output_path):
        """转换完成回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 保存临时文件路径
        self.temp_gif_path = output_path
        
        # 计算GIF大小
        gif_size = os.path.getsize(output_path) / (1024 * 1024)  # 转换为MB
        self.gif_size = round(gif_size, 2)
        
        logger.info(f"GIF转换完成，临时文件: {output_path}, 大小: {self.gif_size} MB")
        
        # 显示GIF预览
        self.show_gif_preview(output_path)
        
        # 显示保存按钮和大小信息
        self.save_gif_btn.setVisible(True)
        self.gif_size_label.setText(f"GIF大小: {self.gif_size} MB")
        self.gif_size_label.setVisible(True)
        
        # 恢复控件状态
        self.set_controls_enabled(True)
    
    def on_conversion_error(self, error_msg):
        """转换错误回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        logger.error(f"GIF转换失败: {error_msg}")
        
        # 恢复控件状态
        self.set_controls_enabled(True)
        
        # 显示错误消息
        QMessageBox.critical(
            self,
            "转换失败",
            f"转换过程中发生错误:\n{error_msg}"
        )
    
    def show_preview(self, item):
        """显示图片预览"""
        row = self.image_list.row(item)
        if 0 <= row < len(self.image_paths):
            image_path = self.image_paths[row]
            pixmap = QPixmap(image_path)
            
            # 缩放图片以适应标签大小
            if not pixmap.isNull():
                # 获取原始图像尺寸
                original_width = pixmap.width()
                original_height = pixmap.height()
                
                # 根据滑块值计算调整后的尺寸
                scale_factor = self.size_slider.value() / 100.0
                scaled_width = int(original_width * scale_factor)
                scaled_height = int(original_height * scale_factor)
                
                # 缩放图片以适应标签大小
                pixmap = pixmap.scaled(
                    self.preview_label.width(),
                    self.preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                self.preview_label.setPixmap(pixmap)
                
                # 更新预览标签文本，显示原始和调整后的尺寸
                self.preview_label.setToolTip(f"原始尺寸: {original_width}x{original_height}, \n调整后尺寸: {scaled_width}x{scaled_height} ({int(scale_factor*100)}%)")
            else:
                self.preview_label.setText("无法加载图片")
            
            # 显示单张图片预览，隐藏GIF预览
            self.preview_label.setVisible(True)
            self.gif_preview_label.setVisible(False)
            self.save_gif_btn.setVisible(False)
            self.gif_size_label.setVisible(False)
    
    def on_size_slider_changed(self, value):
        """处理尺寸滑块变化"""
        self.size_label_display.setText(f"{value}%")
        
        # 如果当前有选中的项目，更新预览以显示调整后的大小
        current_item = self.image_list.currentItem()
        if current_item:
            self.show_preview(current_item)
    
    def on_selection_changed(self):
        """当列表选择改变时"""
        has_selection = bool(self.image_list.selectedItems())
        self.remove_image_btn.setEnabled(has_selection)
    
    def update_button_states(self):
        """更新按钮状态"""
        has_images = bool(self.image_paths)
        self.clear_images_btn.setEnabled(has_images)
        self.convert_btn.setEnabled(has_images)
        self.remove_image_btn.setEnabled(False)  # 默认禁用，除非有选择
    
    def set_controls_enabled(self, enabled):
        """设置控件启用状态"""
        self.add_images_btn.setEnabled(enabled)
        self.remove_image_btn.setEnabled(enabled and bool(self.image_list.selectedItems()))
        self.clear_images_btn.setEnabled(enabled and bool(self.image_paths))
        self.convert_btn.setEnabled(enabled and bool(self.image_paths))
        self.duration_spinbox.setEnabled(enabled)
        self.image_list.setEnabled(enabled)
    
    def resizeEvent(self, event):
        """窗口大小改变事件，重新调整预览图"""
        super().resizeEvent(event)
        # 如果当前有选中的项目，重新加载预览
        current_item = self.image_list.currentItem()
        if current_item:
            self.show_preview(current_item)


def main():
    app = QApplication(sys.argv)
    window = Img2GifApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()