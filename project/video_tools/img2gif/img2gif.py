import sys
import os
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, QFileDialog, QMessageBox, 
                             QSpinBox, QGroupBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon


class GifConverterThread(QThread):
    """后台线程用于处理GIF转换"""
    progress_updated = pyqtSignal(int)
    conversion_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, image_paths, output_path, duration):
        super().__init__()
        self.image_paths = image_paths
        self.output_path = output_path
        self.duration = duration
    
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
                images.append(img)
            
            # 保存为GIF
            if images:
                images[0].save(
                    self.output_path,
                    save_all=True,
                    append_images=images[1:],
                    duration=self.duration,
                    loop=0
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
    
    def init_ui(self):
        self.setWindowTitle('图片转GIF工具')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部按钮区域
        button_layout = QHBoxLayout()
        
        self.add_images_btn = QPushButton('添加图片')
        self.add_images_btn.clicked.connect(self.add_images)
        
        self.remove_image_btn = QPushButton('移除选中图片')
        self.remove_image_btn.clicked.connect(self.remove_selected_image)
        self.remove_image_btn.setEnabled(False)
        
        self.clear_images_btn = QPushButton('清空所有图片')
        self.clear_images_btn.clicked.connect(self.clear_images)
        self.clear_images_btn.setEnabled(False)
        
        self.convert_btn = QPushButton('转换为GIF')
        self.convert_btn.clicked.connect(self.convert_to_gif)
        self.convert_btn.setEnabled(False)
        
        button_layout.addWidget(self.add_images_btn)
        button_layout.addWidget(self.remove_image_btn)
        button_layout.addWidget(self.clear_images_btn)
        button_layout.addWidget(self.convert_btn)
        
        # 创建图片列表区域
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.SingleSelection)
        self.image_list.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 创建预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        self.preview_label = QLabel("请选择一张图片进行预览")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        preview_layout.addWidget(self.preview_label)
        
        # 创建设置区域
        settings_group = QGroupBox("转换设置")
        settings_layout = QHBoxLayout(settings_group)
        
        duration_label = QLabel("每帧持续时间(ms):")
        self.duration_spinbox = QSpinBox()
        self.duration_spinbox.setRange(10, 5000)
        self.duration_spinbox.setValue(500)
        self.duration_spinbox.setSingleStep(100)
        
        settings_layout.addWidget(duration_label)
        settings_layout.addWidget(self.duration_spinbox)
        settings_layout.addStretch()
        
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
            for path in file_paths:
                if path not in self.image_paths:
                    self.image_paths.append(path)
                    # 只显示文件名
                    file_name = os.path.basename(path)
                    self.image_list.addItem(file_name)
            
            # 更新按钮状态
            self.update_button_states()
    
    def remove_selected_image(self):
        """移除选中的图片"""
        current_row = self.image_list.currentRow()
        if current_row >= 0:
            # 移除数据和列表项
            del self.image_paths[current_row]
            self.image_list.takeItem(current_row)
            
            # 清空预览
            self.preview_label.setText("请选择一张图片进行预览")
            
            # 更新按钮状态
            self.update_button_states()
    
    def clear_images(self):
        """清空所有图片"""
        self.image_paths.clear()
        self.image_list.clear()
        self.preview_label.setText("请选择一张图片进行预览")
        self.update_button_states()
    
    def convert_to_gif(self):
        """转换为GIF"""
        if not self.image_paths:
            QMessageBox.warning(self, "警告", "请先添加图片文件")
            return
        
        # 选择输出文件路径
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存GIF文件",
            "output.gif",
            "GIF Files (*.gif)"
        )
        
        if output_path:
            # 禁用相关控件
            self.set_controls_enabled(False)
            
            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            # 获取设置参数
            duration = self.duration_spinbox.value()
            
            # 启动转换线程
            self.converter_thread = GifConverterThread(
                self.image_paths, output_path, duration
            )
            self.converter_thread.progress_updated.connect(self.update_progress)
            self.converter_thread.conversion_finished.connect(self.on_conversion_finished)
            self.converter_thread.error_occurred.connect(self.on_conversion_error)
            self.converter_thread.start()
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_conversion_finished(self, output_path):
        """转换完成回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 恢复控件状态
        self.set_controls_enabled(True)
        
        # 显示成功消息
        QMessageBox.information(
            self,
            "转换完成",
            f"GIF已成功保存到:\n{output_path}"
        )
    
    def on_conversion_error(self, error_msg):
        """转换错误回调"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
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
                pixmap = pixmap.scaled(
                    self.preview_label.width(),
                    self.preview_label.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(pixmap)
            else:
                self.preview_label.setText("无法加载图片")
    
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