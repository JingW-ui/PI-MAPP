import sys
import requests
import json
import os
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

# 获取资源路径，适配PyInstaller单文件模式
def resource_path(relative_path):
    """获取资源的绝对路径，支持开发和打包后两种模式"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller单文件模式下的临时目录
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发模式下的相对路径
    return os.path.join(os.path.abspath("."), relative_path)

class AutoSubmitUI:
    def __init__(self, root):
        self.root = root
        self.timer = None
        self.is_scheduled = False
        self.current_submit_count = 0
        self.total_submit_count = 2
        self.init_ui()
    
    def init_ui(self):
        # 设置窗口标题和大小
        self.root.title('表单自动提交工具')
        self.root.geometry('500x450')
        self.root.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding='10')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表单组
        form_group = ttk.LabelFrame(main_frame, text='表单配置', padding='10')
        form_group.pack(fill=tk.X, pady=5)
        
        # 创建表单布局
        form_layout = ttk.Frame(form_group)
        form_layout.pack(fill=tk.X)
        
        # 添加formId输入
        ttk.Label(form_layout, text='Form ID:').grid(row=0, column=0, sticky=tk.W, pady=3)
        self.form_id_edit = ttk.Entry(form_layout, width=30)
        self.form_id_edit.insert(0, 'NZCgUR')
        self.form_id_edit.grid(row=0, column=1, sticky=tk.W, pady=3)
        
        # 添加姓名输入
        ttk.Label(form_layout, text='姓名:').grid(row=1, column=0, sticky=tk.W, pady=3)
        self.name_edit = ttk.Entry(form_layout, width=30)
        self.name_edit.insert(0, '何慧')
        self.name_edit.grid(row=1, column=1, sticky=tk.W, pady=3)
        
        # 添加班级输入
        ttk.Label(form_layout, text='班级:').grid(row=2, column=0, sticky=tk.W, pady=3)
        self.class_edit = ttk.Entry(form_layout, width=30)
        self.class_edit.insert(0, '食研2501')
        self.class_edit.grid(row=2, column=1, sticky=tk.W, pady=3)
        
        # 添加学号输入
        ttk.Label(form_layout, text='学号:').grid(row=3, column=0, sticky=tk.W, pady=3)
        self.student_id_edit = ttk.Entry(form_layout, width=30)
        self.student_id_edit.insert(0, '2025309110003')
        self.student_id_edit.grid(row=3, column=1, sticky=tk.W, pady=3)
        
        # 创建定时设置组
        schedule_group = ttk.LabelFrame(main_frame, text='定时提交设置', padding='10')
        schedule_group.pack(fill=tk.X, pady=5)
        
        # 创建定时布局
        schedule_layout = ttk.Frame(schedule_group)
        schedule_layout.pack(fill=tk.X)
        
        # 添加定时开关
        ttk.Label(schedule_layout, text='启用定时提交:').grid(row=0, column=0, sticky=tk.W, pady=3)
        self.schedule_var = tk.BooleanVar()
        self.schedule_checkbox = ttk.Checkbutton(schedule_layout, variable=self.schedule_var, command=self.toggle_schedule)
        self.schedule_checkbox.grid(row=0, column=1, sticky=tk.W, pady=3)
        
        # 添加时间选择器
        ttk.Label(schedule_layout, text='提交时间:').grid(row=1, column=0, sticky=tk.W, pady=3)
        self.time_var = tk.StringVar()
        self.time_var.set('19:30')
        self.time_edit = ttk.Entry(schedule_layout, textvariable=self.time_var, width=10, state='disabled')
        self.time_edit.grid(row=1, column=1, sticky=tk.W, pady=3)
        
        # 添加提交次数输入
        ttk.Label(schedule_layout, text='尝试次数:').grid(row=2, column=0, sticky=tk.W, pady=3)
        self.submit_count_var = tk.StringVar()
        self.submit_count_var.set('2')
        self.submit_count_edit = ttk.Entry(schedule_layout, textvariable=self.submit_count_var, width=10, state='disabled')
        self.submit_count_edit.grid(row=2, column=1, sticky=tk.W, pady=3)
        
        # 添加状态显示
        ttk.Label(schedule_layout, text='定时状态:').grid(row=3, column=0, sticky=tk.W, pady=3)
        self.schedule_status = ttk.Label(schedule_layout, text='未启用', foreground='red')
        self.schedule_status.grid(row=3, column=1, sticky=tk.W, pady=3)
        
        # 创建提交按钮
        submit_frame = ttk.Frame(main_frame)
        submit_frame.pack(pady=10)
        self.submit_btn = ttk.Button(submit_frame, text='提交表单', command=self.submit_form_thread)
        self.submit_btn.pack()
        
        # 创建结果输出区域
        result_group = ttk.LabelFrame(main_frame, text='提交结果', padding='10')
        result_group.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_group, wrap=tk.WORD, height=10)
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def toggle_schedule(self):
        if self.schedule_var.get():
            self.time_edit.configure(state='normal')
            self.submit_count_edit.configure(state='normal')
            self.setup_schedule()
        else:
            self.time_edit.configure(state='disabled')
            self.submit_count_edit.configure(state='disabled')
            self.cancel_schedule()
    
    def setup_schedule(self):
        # 获取设定的时间
        target_time_str = self.time_var.get()
        
        # 获取并验证提交次数
        try:
            self.total_submit_count = int(self.submit_count_var.get().strip())
            if self.total_submit_count < 1:
                self.total_submit_count = 2
                self.submit_count_var.set('2')
        except ValueError:
            self.total_submit_count = 2
            self.submit_count_var.set('2')
        
        # 重置提交计数器
        self.current_submit_count = 0
        
        # 更新状态
        self.is_scheduled = True
        current_time = datetime.now().strftime("%H:%M:%S")
        self.schedule_status.config(text=f'[{current_time}] 已启用，将在 {target_time_str} 提交，最大 {self.total_submit_count} 次尝试次数', foreground='green')
        
        # 启动定时检查线程
        if not hasattr(self, 'schedule_thread') or not self.schedule_thread.is_alive():
            self.schedule_thread = threading.Thread(target=self.check_time_loop, daemon=True)
            self.schedule_thread.start()
    
    def cancel_schedule(self, custom_message=None):
        # 更新状态
        self.is_scheduled = False
        if custom_message:
            self.schedule_status.config(text=custom_message, foreground='orange')
        else:
            self.schedule_status.config(text='未启用', foreground='red')
    
    def check_time_loop(self):
        while self.is_scheduled:
            # 获取当前时间
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            
            # 获取目标时间
            target_time_str = self.time_var.get()
            try:
                target_time = datetime.strptime(target_time_str, "%H:%M")
                target_time = target_time.replace(year=now.year, month=now.month, day=now.day)
                
                # 检查是否到达目标时间
                if now.hour == target_time.hour and now.minute == target_time.minute and self.current_submit_count == 0:
                    # 执行提交
                    success = self.submit_form()
                    self.current_submit_count += 1
                    
                    # 更新状态显示
                    if success:
                        custom_message = f'[{current_time}] 提交成功，已完成定时任务'
                        self.cancel_schedule(custom_message)
                    else:
                        custom_message = f'[{current_time}] 提交失败，已完成定时任务'
                        self.cancel_schedule(custom_message)
                        
            except ValueError:
                self.cancel_schedule(f'[{current_time}] 时间格式错误')
                break
            
            # 每秒检查一次
            time.sleep(1)
    
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
                self.result_text.insert(tk.END, f"正在安装playwright...\n")
                self.root.update_idletasks()
                subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])
                subprocess.check_call([sys.executable, "-m", "playwright", "install"])
                from playwright.sync_api import sync_playwright
            
            # 构造表单URL
            form_url = f"https://jsj.top/f/{form_id}"  # 确保URL格式正确
            
            # 使用Playwright分析表单结构
            with sync_playwright() as p:
                self.result_text.insert(tk.END, f"正在启动浏览器...\n")
                self.root.update_idletasks()
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                self.result_text.insert(tk.END, f"正在访问表单页面: {form_url}...\n")
                self.root.update_idletasks()
                page.goto(form_url)
                page.wait_for_load_state('networkidle')
                
                self.result_text.insert(tk.END, f"正在获取表单字段...\n")
                self.root.update_idletasks()
                # 获取所有输入字段
                fields = page.eval_on_selector_all(
                    'input[name],select[name],textarea[name]',
                    'els => els.map(e => ({key: e.name, label: e.labels?.[0]?.innerText ?? "", type: e.type}))'
                )
                
                browser.close()
                self.result_text.insert(tk.END, f"获取到的字段: {str(fields)}\n")
                self.root.update_idletasks()
                
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
                            self.result_text.insert(tk.END, f"匹配到用户提供的成功字段映射模式\n")
                            self.root.update_idletasks()
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
            self.result_text.insert(tk.END, f"分析表单结构失败: {str(e)}\n")
            self.root.update_idletasks()
            print(f"分析表单结构失败: {str(e)}")

        return None
    
    def submit_form(self):
        success = False
        try:
            # 获取当前时间用于日志
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 1. 获取表单数据
            form_id = self.form_id_edit.get().strip()
            name = self.name_edit.get().strip()
            class_name = self.class_edit.get().strip()
            student_id = self.student_id_edit.get().strip()
            
            # 验证输入
            if not form_id:
                self.result_text.insert(tk.END, '错误: Form ID不能为空\n')
                self.root.update_idletasks()
                return success
            
            # 2. 分析表单结构
            self.result_text.insert(tk.END, f'[{current_time}] 正在分析表单结构...\n')
            self.root.update_idletasks()
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
                self.result_text.insert(tk.END, f'[{current_time}] 使用分析得到的字段映射: {str(field_mapping)}\n')
                self.root.update_idletasks()
                self.result_text.insert(tk.END, f'[{current_time}] 只提交一次正确的表单\n')
                self.root.update_idletasks()
            else:
                # 如果分析失败，使用用户提供的成功模式
                self.result_text.insert(tk.END, f'[{current_time}] 使用用户提供的成功字段映射模式\n')
                self.root.update_idletasks()
                
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
            self.result_text.insert(tk.END, '正在提交表单...\n')
            self.root.update_idletasks()
            session = requests.Session()
            response = session.post(
                url=submit_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            # 5. 显示结果
            result = f"提交状态码：{response.status_code}\n"
            result += f"服务器返回：{json.dumps(response.json(), ensure_ascii=False, indent=2)}"
            self.result_text.insert(tk.END, result + '\n')
            self.root.update_idletasks()
            
            # 判断提交是否成功（根据状态码和服务器返回内容）
            if response.status_code == 200:
                response_data = response.json()
                # 检查是否包含成功提交的标志
                if 'data' in response_data and 'createPublishedFormEntry' in response_data['data']:
                    success = True
            
        except Exception as e:
            self.result_text.insert(tk.END, f"提交失败：{str(e)}\n")
            self.root.update_idletasks()
        
        return success
    
    def submit_form_thread(self):
        # 清空结果区域
        self.result_text.delete(1.0, tk.END)
        # 在新线程中执行提交操作，避免阻塞UI
        thread = threading.Thread(target=self.submit_form, daemon=True)
        thread.start()

if __name__ == '__main__':
    root = tk.Tk()
    app = AutoSubmitUI(root)
    root.mainloop()
