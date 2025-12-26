# 表单自动提交工具

这是一个基于PyQt6开发的表单自动提交工具，用于通过GraphQL接口批量提交表单数据。

## 功能特点

- 可视化界面，操作简单
- 支持自定义Form ID、姓名、班级、学号等字段
- 实时显示提交结果
- 基于原脚本的请求逻辑，确保兼容性

## 项目结构

```
auto_submit_web/
├── auto_main.py        # 原始命令行脚本
├── auto_submit_ui.py   # PyQt6 GUI版本
└── README.md           # 项目说明文档
```

## 依赖安装

```bash
pip install PyQt6 requests
```

## 使用方法

### 1. GUI版本

运行PyQt6界面版本：

```bash
python auto_submit_ui.py
```

在界面中填写以下信息：
- **Form ID**：表单标识符（默认：NZCgUR）
- **姓名**：提交的姓名（默认：何慧）
- **班级**：提交的班级（默认：食研2501）
- **学号**：提交的学号（默认：2025309110003）

点击"提交表单"按钮，在结果区域查看提交状态和服务器响应。

### 2. 命令行版本

运行原始命令行脚本：

```bash
python auto_main.py
```

## 打包成可执行文件

使用PyInstaller将GUI版本打包为Windows可执行文件：

### 安装PyInstaller

```bash
pip install pyinstaller
```

### 打包命令

```bash
pyinstaller --onefile --windowed --name="表单自动提交工具1.0.1" auto_submit_ui.py
pyinstaller -F -w -i b.ico --add-data "b.ico;." --name="auto_Submit_1.1.5" auto_submit_ui.py
```

打包选项说明：
- `--onefile`：生成单个可执行文件
- `--windowed`：不显示命令行窗口（仅适用于GUI程序）
- `--name`：指定可执行文件名称

打包完成后，可执行文件将生成在`dist`目录中。

## 注意事项

1. 确保网络连接正常
2. 请勿频繁提交，避免给服务器造成压力
3. 提交的数据将直接发送到指定的GraphQL接口
4. 如遇到"Variables mismatch"错误，请检查Form ID是否正确

## 更新日志

- 2025-12-16：修复URL硬编码问题，支持动态Form ID
- 2025-12-16：创建PyQt6 GUI版本
- 2025-12-16：初始版本发布

## 许可证

本项目采用MIT许可证。