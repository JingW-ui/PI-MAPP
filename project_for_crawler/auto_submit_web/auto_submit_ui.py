import sys
import requests
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, QGridLayout,
    QTimeEdit, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtCore import QTime
from PyQt6.QtGui import QIcon

# 获取资源路径，适配PyInstaller单文件模式
def resource_path(relative_path):
    """获取资源的绝对路径，支持开发和打包后两种模式"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller单文件模式下的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发模式下的相对路径
    return os.path.join(os.path.abspath("."), relative_path)

class AutoSubmitUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.is_scheduled = False
        self.current_submit_count = 0
        self.total_submit_count = 2
        self.init_ui()
    
    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle('表单自动提交工具')
        self.setGeometry(300, 300, 500, 450)

        # 创建中央控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建表单组
        form_group = QGroupBox('表单配置')
        form_layout = QGridLayout()
        
        # 添加formId输入
        form_layout.addWidget(QLabel('Form ID:'), 0, 0)
        self.form_id_edit = QLineEdit('NZCgUR')
        form_layout.addWidget(self.form_id_edit, 0, 1)
        
        # 添加姓名输入
        form_layout.addWidget(QLabel('姓名:'), 1, 0)
        self.name_edit = QLineEdit('何慧')
        form_layout.addWidget(self.name_edit, 1, 1)
        
        # 添加班级输入
        form_layout.addWidget(QLabel('班级:'), 2, 0)
        self.class_edit = QLineEdit('食研2501')
        form_layout.addWidget(self.class_edit, 2, 1)
        
        # 添加学号输入
        form_layout.addWidget(QLabel('学号:'), 3, 0)
        self.student_id_edit = QLineEdit('2025309110003')
        form_layout.addWidget(self.student_id_edit, 3, 1)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 创建定时设置组
        schedule_group = QGroupBox('定时提交设置')
        schedule_layout = QGridLayout()
        
        # 添加定时开关
        schedule_layout.addWidget(QLabel('启用定时提交:'), 0, 0)
        self.schedule_checkbox = QCheckBox()
        self.schedule_checkbox.stateChanged.connect(self.toggle_schedule)
        schedule_layout.addWidget(self.schedule_checkbox, 0, 1)
        
        # 添加时间选择器
        schedule_layout.addWidget(QLabel('提交时间:'), 1, 0)
        self.time_edit = QTimeEdit(QTime(19, 30))  # 默认19:30
        self.time_edit.setDisplayFormat('HH:mm')
        self.time_edit.setEnabled(False)
        # 添加时间选择器的用户提示
        self.time_edit.setToolTip('选择每天自动提交的时间')
        schedule_layout.addWidget(self.time_edit, 1, 1)
        
        # 添加提交次数输入
        schedule_layout.addWidget(QLabel('尝试次数:'), 2, 0)
        self.submit_count_edit = QLineEdit('2')
        self.submit_count_edit.setEnabled(False)
        # 添加提交次数输入框的用户提示
        self.submit_count_edit.setToolTip('设置每天自动提交的次数，默认2次')
        schedule_layout.addWidget(self.submit_count_edit, 2, 1)
        
        # 添加状态显示
        schedule_layout.addWidget(QLabel('定时状态:'), 3, 0)
        self.schedule_status = QLabel('未启用')
        self.schedule_status.setStyleSheet('color: red')
        schedule_layout.addWidget(self.schedule_status, 3, 1)
        
        schedule_group.setLayout(schedule_layout)
        main_layout.addWidget(schedule_group)
        
        # 创建提交按钮
        submit_layout = QHBoxLayout()
        self.submit_btn = QPushButton('提交表单')
        self.submit_btn.clicked.connect(self.submit_form)
        submit_layout.addWidget(self.submit_btn)
        main_layout.addLayout(submit_layout)
        
        # 创建结果输出区域
        result_group = QGroupBox('提交结果')
        result_layout = QVBoxLayout()
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
    
    def toggle_schedule(self, state):
        if state == Qt.CheckState.Checked.value:
            self.time_edit.setEnabled(True)
            self.submit_count_edit.setEnabled(True)
            self.setup_schedule()
        else:
            self.time_edit.setEnabled(False)
            self.submit_count_edit.setEnabled(False)
            self.cancel_schedule()
    
    def setup_schedule(self):
        # 获取设定的时间
        target_time = self.time_edit.time()
        
        # 获取并验证提交次数
        try:
            self.total_submit_count = int(self.submit_count_edit.text().strip())
            if self.total_submit_count < 1:
                self.total_submit_count = 2
                self.submit_count_edit.setText('2')
        except ValueError:
            self.total_submit_count = 2
            self.submit_count_edit.setText('2')
        
        # 重置提交计数器
        self.current_submit_count = 0
        
        # 创建定时器
        if self.timer is None:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.check_time)
            
        # 每秒检查一次时间
        self.timer.start(1000)
        
        # 更新状态
        self.is_scheduled = True
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.schedule_status.setText(f'[{current_time}] 已启用，将在 {target_time.toString("HH:mm")} 提交，最大 {self.total_submit_count} 次尝试次数')
        self.schedule_status.setStyleSheet('color: green')
    
    def cancel_schedule(self, custom_message=None):
        # 停止定时器
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
        
        # 更新状态
        self.is_scheduled = False
        if custom_message:
            self.schedule_status.setText(custom_message)
            self.schedule_status.setStyleSheet('color: orange')
        else:
            self.schedule_status.setText('未启用')
            self.schedule_status.setStyleSheet('color: red')
    
    def check_time(self):
        # 获取当前时间
        current_time = QTime.currentTime()
        target_time = self.time_edit.time()
        current_time_str = current_time.toString("HH:mm:ss")
        
        # 检查是否到达目标时间
        if current_time.hour() == target_time.hour() and current_time.minute() == target_time.minute():
            # 只提交一次，避免产生多个提交记录
            if self.current_submit_count == 0:
                # 执行提交
                success = self.submit_form()
                self.current_submit_count += 1
                
                # 更新状态显示
                if success:
                    custom_message = f'[{current_time_str}] 提交成功，已完成定时任务'
                    self.cancel_schedule(custom_message)
                else:
                    custom_message = f'[{current_time_str}] 提交失败，已完成定时任务'
                    self.cancel_schedule(custom_message)
    
    def analyze_form_structure(self, form_id):
        """
        分析表单结构，获取字段映射信息
        :param form_id: 表单ID
        :return: 字段映射字典
        """
        try:
            # 安装playwright依赖
            import subprocess
            import sys
            try:
                from playwright.sync_api import sync_playwright
            except ImportError:
                self.result_text.append(f"正在安装playwright...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install"])
                from playwright.sync_api import sync_playwright
            
            # 构造表单URL
            form_url = f"https://jsj.top/f/{form_id}"  # 确保URL格式正确
            
            # 使用Playwright分析表单结构
            with sync_playwright() as p:
                self.result_text.append(f"正在启动浏览器...")
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                self.result_text.append(f"正在访问表单页面: {form_url}...")
                page.goto(form_url)
                page.wait_for_load_state('networkidle')
                
                self.result_text.append(f"正在获取表单字段...")
                # 获取所有输入字段
                fields = page.eval_on_selector_all(
                    'input[name],select[name],textarea[name]',
                    'els => els.map(e => ({key: e.name, label: e.labels?.[0]?.innerText ?? "", type: e.type}))'
                )
                
                browser.close()
                self.result_text.append(f"获取到的字段: {str(fields)}")
                
                # 分析字段映射
                field_mapping = {}
                text_fields = [f for f in fields if f['type'] == 'text']
                
                # 按照用户提供的成功测试结果处理
                # 当字段没有标签时，根据字段名称和位置判断
                if text_fields:
                    # 处理用户提供的示例情况：field_1, field_4, field_5
                    if len(text_fields) == 3:
                        # 检查是否匹配用户提供的示例模式
                        field_keys = [f['key'] for f in text_fields]
                        if 'field_1' in field_keys and 'field_4' in field_keys and 'field_5' in field_keys:
                            # 匹配用户提供的成功模式
                            field_mapping['name'] = 'field_1'
                            field_mapping['class'] = 'field_4'
                            field_mapping['student_id'] = 'field_5'
                            self.result_text.append(f"匹配到用户提供的成功字段映射模式")
                        else:
                            # 通用位置匹配
                            field_mapping['name'] = text_fields[0]['key']  # 第一个文本字段是姓名
                            field_mapping['class'] = text_fields[1]['key']  # 第二个文本字段可能是班级
                            field_mapping['student_id'] = text_fields[2]['key']  # 第三个文本字段可能是学号
                    elif len(text_fields) == 2:
                        # 只有两个字段时的处理
                        field_mapping['name'] = text_fields[0]['key']
                        field_mapping['class'] = text_fields[1]['key']
                        field_mapping['student_id'] = text_fields[1]['key']  # 可能学号和班级是同一个字段
                    elif len(text_fields) >= 1:
                        # 只有一个字段时的处理
                        field_mapping['name'] = text_fields[0]['key']
                        field_mapping['class'] = text_fields[0]['key']
                        field_mapping['student_id'] = text_fields[0]['key']
                
                # 如果有标签信息，优先使用标签判断
                for field in fields:
                    label = field['label'].strip().lower()
                    key = field['key']
                    
                    if '姓名' in label or 'name' in label:
                        field_mapping['name'] = key
                    elif '班级' in label or 'class' in label:
                        field_mapping['class'] = key
                    elif '学号' in label or 'student' in label or 'id' in label:
                        field_mapping['student_id'] = key
                
                return field_mapping
            
        except Exception as e:
            self.result_text.append(f"分析表单结构失败: {str(e)}")
            print(f"分析表单结构失败: {str(e)}")

        return None
    
    def submit_form(self):
        success = False
        try:
            # 获取当前时间用于日志
            current_time = QTime.currentTime().toString("HH:mm:ss")
            
            # 1. 获取表单数据
            form_id = self.form_id_edit.text().strip()
            name = self.name_edit.text().strip()
            class_name = self.class_edit.text().strip()
            student_id = self.student_id_edit.text().strip()
            
            # 验证输入
            if not form_id:
                self.result_text.setText('错误: Form ID不能为空')
                return success
            
            # 2. 分析表单结构
            self.result_text.append(f'[{current_time}] 正在分析表单结构...')
            field_mapping = self.analyze_form_structure(form_id)
            print(field_mapping)
            
            # 3. 构造请求体
            submit_url = f"https://jsj.top/graphql/f/{form_id}"
            
            # 构建entryAttributes
            entry_attributes = {}
            entry_attributes['field_1'] = name  # 姓名字段通常是field_1
            
            # 使用获取到的字段映射
            if field_mapping and 'class' in field_mapping and 'student_id' in field_mapping:
                # 如果分析成功，只使用正确的字段映射提交一次
                entry_attributes[field_mapping['name']] = name
                entry_attributes[field_mapping['class']] = class_name
                entry_attributes[field_mapping['student_id']] = student_id
                self.result_text.append(f'[{current_time}] 使用分析得到的字段映射: {str(field_mapping)}')
                self.result_text.append(f'[{current_time}] 只提交一次正确的表单')
            else:
                # 如果分析失败，使用用户提供的成功模式
                self.result_text.append(f'[{current_time}] 使用用户提供的成功字段映射模式')
                
                # 用户提供的成功模式
                entry_attributes['field_1'] = name
                entry_attributes['field_4'] = class_name
                entry_attributes['field_5'] = student_id
                
                # 同时包含其他可能的组合
                entry_attributes['field_2'] = class_name  # 标准位置
                entry_attributes['field_3'] = student_id  # 标准位置
                entry_attributes['field_6'] = class_name  # 班级可能在field_6
                entry_attributes['field_7'] = student_id  # 学号可能在field_7
            
            payload = {
                "operationName": "CreatePublishedFormEntry",
                "variables": {
                    "input": {
                        "formId": form_id,
                        "geetest4Data": None,
                        "captchaData": None,
                        "prefilledParams": "",
                        "hasPreferential": False,
                        "forceSubmit": False,
                        "entryAttributes": entry_attributes,
                        "fillingDuration": 30,
                        "embedded": False,
                        "backgroundImage": False,
                        "formMargin": False,
                        "internal": False,
                        "code": None
                    }
                },
                "extensions": {
                    "persistedQuery": {
                        "version": 1,
                        "sha256Hash": "5bf5d5ff1235ad9e9bc24bbb8c8d20b52efaa7b9ef72b848f2b1ace05611dcee"
                    }
                }
            }
            
            # 3. 构造请求头
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
                "Content-Type": "application/json",
                "Referer": f"https://jinshuju.cool/f/{form_id}",
                "Origin": "https://jinshuju.cool"
            }
            
            # 4. 发送POST请求
            self.result_text.setText('正在提交表单...')
            session = requests.Session()
            response = session.post(
                url=submit_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            # 5. 显示结果
            result = f"提交状态码：{response.status_code}\n"
            result += f"服务器返回：{json.dumps(response.json(), ensure_ascii=False, indent=2)}"
            self.result_text.setText(result)
            
            # 判断提交是否成功（根据状态码和服务器返回内容）
            if response.status_code == 200:
                response_data = response.json()
                # 检查是否包含成功提交的标志
                if 'data' in response_data and 'createPublishedFormEntry' in response_data['data']:
                    success = True
            
        except Exception as e:
            self.result_text.setText(f"提交失败：{str(e)}")
        
        return success

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoSubmitUI()
    window.setWindowIcon(QIcon(resource_path("b.ico")))
    window.show()
    sys.exit(app.exec())