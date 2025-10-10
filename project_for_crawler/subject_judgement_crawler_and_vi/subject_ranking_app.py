import sys
import pandas as pd
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtCharts import *
import random
from functools import partial


class SubjectRankingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Academic Ranking Visualization System")
        self.setMinimumSize(1600, 850)

        # 欧美简约风格配色
        self.colors = {
            "primary": "#2C3E50",
            "secondary": "#34495E",
            "accent": "#3498DB",
            "background": "#ECF0F1",
            "text": "#2C3E50",
            "success": "#27AE60",
            "warning": "#E67E22",
            "danger": "#E74C3C"
        }

        # 设置样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {self.colors["background"]};
            }}
            QGroupBox {{
                font-size: 14px;
                font-weight: bold;
                border: 2px solid {self.colors["primary"]};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                color: {self.colors["text"]};
                background-color: white;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: {self.colors["primary"]};
            }}
            QPushButton {{
                background-color: {self.colors["primary"]};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.colors["accent"]};
            }}
            QPushButton:pressed {{
                background-color: {self.colors["secondary"]};
            }}
            QLabel {{
                color: {self.colors["text"]};
                font-size: 14px;
            }}
            QComboBox, QLineEdit {{
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 13px;
                background-color: white;
                color: {self.colors["text"]};
            }}
            QComboBox:focus, QLineEdit:focus {{
                border-color: {self.colors["accent"]};
            }}
            QTableWidget {{
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                background-color: white;
                gridline-color: #ECF0F1;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #ECF0F1;
            }}
            QTableWidget::item:hover {{
                background-color: #F8F9FA;
            }}
            QTableWidget::item:selected {{
                background-color: {self.colors["accent"]}20;
                color: {self.colors["text"]};
            }}
            QHeaderView::section {{
                background-color: {self.colors["primary"]};
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
            QProgressBar {{
                border: 2px solid #BDC3C7;
                border-radius: 6px;
                text-align: center;
                color: {self.colors["text"]};
                background-color: white;
            }}
            QProgressBar::chunk {{
                background-color: {self.colors["accent"]};
                border-radius: 4px;
            }}
        """)

        # 创建示例数据
        self.data = self.create_sample_data()
        self.filtered_data = self.data.copy()

        self.c9_universities = {
            "清华大学", "北京大学", "复旦大学", "上海交通大学",
            "浙江大学", "中国科学技术大学", "南京大学", "哈尔滨工业大学", "西安交通大学"
        }

        self._985_universities = {
            "清华大学", "北京大学", "中国人民大学", "北京航空航天大学", "北京理工大学",
            "北京师范大学", "中国农业大学", "中央民族大学", "南开大学", "天津大学",
            "大连理工大学", "东北大学", "吉林大学", "哈尔滨工业大学", "复旦大学",
            "同济大学", "上海交通大学", "华东师范大学", "南京大学", "东南大学",
            "浙江大学", "中国科学技术大学", "厦门大学", "山东大学", "中国海洋大学",
            "武汉大学", "华中科技大学", "湖南大学", "中南大学", "中山大学",
            "华南理工大学", "四川大学", "电子科技大学", "重庆大学", "西安交通大学",
            "西北工业大学", "兰州大学", "西北农林科技大学", "国防科技大学"
        }

        self._211_universities = {
                   # 以下仅列出非 985 的 77 所纯 211（2025 教育部版）
                   "北京科技大学", "北京化工大学", "北京邮电大学", "北京林业大学", "北京中医药大学",
                   "北京外国语大学", "中国传媒大学", "对外经济贸易大学", "中央财经大学", "中国政法大学",
                   "华北电力大学", "中国矿业大学（北京）", "中国石油大学（北京）", "中国地质大学（北京）",
                   "北京体育大学", "中央音乐学院", "北京工业大学", "北京交通大学", "北京联合大学",
                   "天津医科大学", "河北工业大学", "太原理工大学", "内蒙古大学", "辽宁大学",
                   "大连海事大学", "东北师范大学", "延边大学", "东北农业大学", "东北林业大学",
                   "华东理工大学", "东华大学", "上海外国语大学", "上海财经大学", "上海大学",
                   "上海科技大学", "苏州大学", "南京航空航天大学", "南京理工大学", "河海大学",
                   "江南大学", "南京农业大学", "中国药科大学", "南京师范大学", "安徽大学",
                   "合肥工业大学", "福州大学", "南昌大学", "中国石油大学（华东）", "郑州大学",
                   "武汉理工大学", "中国地质大学（武汉）", "华中农业大学", "华中师范大学", "中南财经政法大学",
                   "湖南师范大学", "暨南大学", "华南师范大学", "广西大学", "海南大学",
                   "西南大学", "西南交通大学", "四川农业大学", "西南财经大学", "贵州大学",
                   "云南大学", "西藏大学", "西北大学", "西安电子科技大学", "长安大学",
                   "陕西师范大学", "青海大学", "宁夏大学", "新疆大学", "石河子大学"
               }

        self.init_ui()
        self.init_animations()


    def create_sample_data(self):
        """创建示例数据"""

        # 强力将学科代码和学校代码作为字符串读取
        data = pd.read_csv("学科评估结果_第四轮.csv", encoding="utf-8",
                           dtype={"学科代码": str, "学校代码": str})


        location_data = pd.read_csv("univ_province_city.csv", encoding="utf-8")
        # 合并数据
        data = pd.merge(data, location_data, left_on="学校名称", right_on="name", how="left")
        # 重命名列
        data = data.rename(columns={"province": "省份", "city": "城市"})
        # 删除多余的name列
        data = data.drop(columns=["name"])


        required_columns = ["学科代码", "学科名称", "学科门类", "学校代码", "学校名称", "评估等级", "省份", "城市"]
        if not all(col in data.columns for col in required_columns):
            raise ValueError("CSV文件缺少必要的列")
        return data


    def init_ui(self):
        """初始化UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title_label = QLabel("ACADEMIC RANKING VISUALIZATION")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.colors["primary"]};
            padding: 5px;
            background-color: transparent;  /* 设置背景透明 */
            border: none;  /* 移除边框 */
        """)
        main_layout.addWidget(title_label)

        # 筛选区域
        filter_group = QGroupBox("FILTER CRITERIA")
        filter_layout = QHBoxLayout()

        # 学科门类筛选
        filter_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        self.category_combo.addItems(sorted(self.data["学科门类"].unique()))
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        filter_layout.addWidget(self.category_combo)

        # 学科名称筛选
        filter_layout.addWidget(QLabel("Subject:"))
        self.subject_combo = QComboBox()
        self.subject_combo.addItem("All Subjects")
        self.subject_combo.addItems(sorted(self.data["学科名称"].unique()))
        self.subject_combo.currentTextChanged.connect(self.update_display)
        filter_layout.addWidget(self.subject_combo)


        # 评估等级筛选
        filter_layout.addWidget(QLabel("Grade:"))
        self.grade_combo = QComboBox()
        self.grade_combo.addItem("All Grades")
        self.grade_combo.addItems([
            "A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-",
            "B及以上", "A-及以上"
        ])
        self.grade_combo.currentTextChanged.connect(self.update_display)
        filter_layout.addWidget(self.grade_combo)

        # 省份筛选
        filter_layout.addWidget(QLabel("Province:"))
        self.province_combo = QComboBox()
        self.province_combo.addItem("All Provinces")
        # 获取所有非空的省份数据
        provinces = self.data["省份"].dropna().unique()
        self.province_combo.addItems(sorted(provinces))
        self.province_combo.currentTextChanged.connect(self.on_province_changed)
        filter_layout.addWidget(self.province_combo)

        # 城市筛选
        filter_layout.addWidget(QLabel("City:"))
        self.city_combo = QComboBox()
        self.city_combo.addItem("All Cities")
        self.city_combo.currentTextChanged.connect(self.update_display)
        filter_layout.addWidget(self.city_combo)

        # 搜索框
        filter_layout.addWidget(QLabel("University:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter university name...")
        self.search_input.textChanged.connect(self.update_display)
        filter_layout.addWidget(self.search_input)

        # 省份/城市搜索框
        filter_layout.addWidget(QLabel("Province/City:"))
        self.location_search_input = QLineEdit()
        self.location_search_input.setPlaceholderText("Enter province or city...")
        self.location_search_input.textChanged.connect(self.update_display)
        filter_layout.addWidget(self.location_search_input)

        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        # 数据展示区域
        content_layout = QHBoxLayout()

        # 左侧表格
        left_panel = QVBoxLayout()

        # 统计信息
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            background-color: white;
            border-radius: 8px;
            padding: 5px;
            border: 1px solid #BDC3C7;
        """)
        stats_layout = QHBoxLayout(stats_widget)

        self.stats_label = QLabel("Showing 0 records")
        self.stats_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        stats_layout.addWidget(self.stats_label)

        # 添加快速操作按钮
        reset_btn = QPushButton("Reset Filters")
        reset_btn.clicked.connect(self.reset_filters)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors["warning"]};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #F39C12;
            }}
            QPushButton:pressed {{
                background-color: #E67E22;
            }}
        """)
        stats_layout.addWidget(reset_btn)

        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        export_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors["success"]};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #2ECC71;
            }}
            QPushButton:pressed {{
                background-color: #27AE60;
            }}
        """)
        stats_layout.addWidget(export_btn)

        left_panel.addWidget(stats_widget)

        # 数据表格
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels([
            "Category", "Subject Name", "Subject Code",
            "University Name", "University Code", "Grade", "Province", "City"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.table_widget.setSortingEnabled(True)
        left_panel.addWidget(self.table_widget)
        # 设置表格字体和对齐方式
        self.table_widget.setStyleSheet("""
            QTableWidget {
                font-size: 12px; /* 表格内容文字小一号 */
            }
            QHeaderView::section {
                font-size: 13px; /* 表头文字小一号 */
            }
        """)

        content_layout.addLayout(left_panel, 5)

        # 右侧图表
        right_panel = QVBoxLayout()

        # 图表选择
        chart_group = QGroupBox("VISUALIZATION")
        chart_layout = QVBoxLayout()

        # 图表类型选择
        chart_type_widget = QWidget()
        chart_type_layout = QHBoxLayout(chart_type_widget)

        self.chart_buttons = QButtonGroup()
        chart_types = [
            ("Pie Chart", "pie"),
            ("Bar Chart", "bar"),
            ("Line Chart", "line"),
            ("Radar Chart", "radar")
        ]

        for text, chart_type in chart_types:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("chartType", chart_type)
            # 使用 partial 确保每个按钮绑定正确的参数
            btn.clicked.connect(partial(self.update_chart, chart_type))
            self.chart_buttons.addButton(btn)
            chart_type_layout.addWidget(btn)

        # 默认选中饼图
        if self.chart_buttons.buttons():
            self.chart_buttons.buttons()[0].setChecked(True)

        chart_layout.addWidget(chart_type_widget)

        # 创建图表视图
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setMinimumHeight(400)
        self.chart_view.setStyleSheet("border-radius: 8px; background-color: white;")
        chart_layout.addWidget(self.chart_view)

        chart_group.setLayout(chart_layout)
        right_panel.addWidget(chart_group)

        # 实时数据
        realtime_group = QGroupBox("REAL-TIME DATA")
        realtime_layout = QVBoxLayout()

        self.realtime_label = QLabel("Loading data...")
        self.realtime_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.realtime_label.setAlignment(Qt.AlignCenter)
        realtime_layout.addWidget(self.realtime_label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(8)
        realtime_layout.addWidget(self.progress_bar)

        realtime_group.setLayout(realtime_layout)
        right_panel.addWidget(realtime_group)

        content_layout.addLayout(right_panel, 2)
        main_layout.addLayout(content_layout)

        # 初始显示
        self.update_display()

    # 在 on_category_changed 方法中添加省份和城市的联动更新:

    # 修改 on_category_changed 方法，更新省份和城市下拉框的调用：

    def on_category_changed(self):
        """当学科门类变化时更新学科列表"""
        category = self.category_combo.currentText()

        # 保存当前选中的学科
        current_subject = self.subject_combo.currentText()

        # 更新学科列表
        self.subject_combo.clear()
        self.subject_combo.addItem("All Subjects")

        if category != "All Categories":
            filtered_subjects = self.data[self.data["学科门类"] == category]["学科名称"].unique()
            self.subject_combo.addItems(sorted(filtered_subjects))
        else:
            self.subject_combo.addItems(sorted(self.data["学科名称"].unique()))

        # 尝试恢复之前选中的学科
        index = self.subject_combo.findText(current_subject)
        if index >= 0:
            self.subject_combo.setCurrentIndex(index)

        # 更新省份和城市下拉框选项（根据当前筛选条件）
        self.update_province_city_combos()

        self.update_display()

    # 修改 update_province_city_combos 方法，实现省份城市联动：

    def update_province_city_combos(self):
        """更新省份和城市下拉框选项"""
        # 保存当前选择
        current_province = self.province_combo.currentText()
        current_city = self.city_combo.currentText()

        # 获取当前筛选条件下的数据
        temp_data = self.data.copy()

        # 应用当前筛选条件
        category = self.category_combo.currentText()
        subject = self.subject_combo.currentText()
        grade = self.grade_combo.currentText()
        search_text = self.search_input.text().lower()

        if category != "All Categories":
            temp_data = temp_data[temp_data["学科门类"] == category]
        if subject != "All Subjects":
            temp_data = temp_data[temp_data["学科名称"] == subject]
        if grade != "All Grades":
            temp_data = temp_data[temp_data["评估等级"] == grade]
        if search_text:
            temp_data = temp_data[
                temp_data["学校名称"].str.lower().str.contains(search_text)
            ]

        # 更新省份下拉框
        self.province_combo.blockSignals(True)  # 防止触发更新事件
        self.province_combo.clear()
        self.province_combo.addItem("All Provinces")
        provinces = temp_data["省份"].dropna().unique()
        self.province_combo.addItems(sorted(provinces))

        # 恢复之前的选择
        province_index = self.province_combo.findText(current_province)
        if province_index >= 0:
            self.province_combo.setCurrentIndex(province_index)
        self.province_combo.blockSignals(False)

        # 更新城市下拉框 - 根据选中的省份筛选城市
        self.city_combo.blockSignals(True)  # 防止触发更新事件
        self.city_combo.clear()
        self.city_combo.addItem("All Cities")

        # 如果选择了特定省份，则只显示该省份的城市
        if current_province != "All Provinces":
            city_data = temp_data[temp_data["省份"] == current_province]
            cities = city_data["城市"].dropna().unique()
        else:
            cities = temp_data["城市"].dropna().unique()

        self.city_combo.addItems(sorted(cities))

        # 恢复之前的选择
        city_index = self.city_combo.findText(current_city)
        if city_index >= 0:
            self.city_combo.setCurrentIndex(city_index)
        self.city_combo.blockSignals(False)

    def on_province_changed(self):
        """当省份选择变化时更新城市列表"""
        # 更新城市下拉框
        self.update_cities_for_province()
        # 更新显示
        self.update_display()

    def update_cities_for_province(self):
        """根据选中的省份更新城市下拉框"""
        selected_province = self.province_combo.currentText()

        # 保存当前城市选择
        current_city = self.city_combo.currentText()

        # 获取当前筛选条件下的数据
        temp_data = self.data.copy()

        # 应用当前筛选条件
        category = self.category_combo.currentText()
        subject = self.subject_combo.currentText()
        grade = self.grade_combo.currentText()
        search_text = self.search_input.text().lower()

        if category != "All Categories":
            temp_data = temp_data[temp_data["学科门类"] == category]
        if subject != "All Subjects":
            temp_data = temp_data[temp_data["学科名称"] == subject]
        if grade != "All Grades":
            temp_data = temp_data[temp_data["评估等级"] == grade]
        if search_text:
            temp_data = temp_data[
                temp_data["学校名称"].str.lower().str.contains(search_text)
            ]

        # 更新城市下拉框
        self.city_combo.blockSignals(True)
        self.city_combo.clear()
        self.city_combo.addItem("All Cities")

        # 如果选择了特定省份，则只显示该省份的城市
        if selected_province != "All Provinces":
            city_data = temp_data[temp_data["省份"] == selected_province]
            cities = city_data["城市"].dropna().unique()
        else:
            cities = temp_data["城市"].dropna().unique()

        self.city_combo.addItems(sorted(cities))

        # 恢复之前的选择（如果该城市仍在列表中）
        city_index = self.city_combo.findText(current_city)
        if city_index >= 0:
            self.city_combo.setCurrentIndex(city_index)
        self.city_combo.blockSignals(False)

    def reset_filters(self):
        """重置所有筛选条件"""
        self.category_combo.setCurrentIndex(0)
        self.subject_combo.setCurrentIndex(0)
        self.grade_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.location_search_input.clear()
        # 重置省份和城市筛选
        self.province_combo.setCurrentIndex(0)
        self.city_combo.setCurrentIndex(0)

    def export_data(self):
        """导出数据到CSV文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "academic_ranking_data.csv", "CSV Files (*.csv)"
        )

        if file_path:
            try:
                self.filtered_data.to_csv(file_path, index=False, encoding='utf-8')
                QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting data: {str(e)}")

    def init_animations(self):
        """初始化动画效果"""
        # 进度条动画
        self.progress_animation = QPropertyAnimation(self.progress_bar, b"value")
        self.progress_animation.setDuration(3000)
        self.progress_animation.setStartValue(0)
        self.progress_animation.setEndValue(100)
        self.progress_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # 启动动画
        QTimer.singleShot(1000, self.progress_animation.start)

        # 实时更新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_realtime_data)
        self.timer.start(5000)

    def update_display(self):
        """更新显示内容"""
        # 获取筛选条件
        category = self.category_combo.currentText()
        subject = self.subject_combo.currentText()
        grade = self.grade_combo.currentText()
        search_text = self.search_input.text().lower()
        location_search_text = self.location_search_input.text().lower()
        # 获取省份和城市筛选条件
        province = self.province_combo.currentText()
        city = self.city_combo.currentText()

        # 筛选数据
        self.filtered_data = self.data.copy()

        if category != "All Categories":
            self.filtered_data = self.filtered_data[self.filtered_data["学科门类"] == category]
        if subject != "All Subjects":
            self.filtered_data = self.filtered_data[self.filtered_data["学科名称"] == subject]
        if grade != "All Grades":
            # 处理扩展的等级筛选条件
            if grade == "B及以上":
                # 定义等级顺序，从高到低
                grade_order = ["A+", "A", "A-", "B+", "B"]
                self.filtered_data = self.filtered_data[self.filtered_data["评估等级"].isin(grade_order)]
            elif grade == "A-及以上":
                # 定义等级顺序，从高到低
                grade_order = ["A+", "A", "A-"]
                self.filtered_data = self.filtered_data[self.filtered_data["评估等级"].isin(grade_order)]
            else:
                # 原有的单一等级筛选
                self.filtered_data = self.filtered_data[self.filtered_data["评估等级"] == grade]
        if search_text:
            self.filtered_data = self.filtered_data[
                self.filtered_data["学校名称"].str.lower().str.contains(search_text)
            ]
        if location_search_text:
            # 省份或城市模糊搜索
            province_mask = self.filtered_data["省份"].str.lower().str.contains(location_search_text, na=False)
            city_mask = self.filtered_data["城市"].str.lower().str.contains(location_search_text, na=False)
            self.filtered_data = self.filtered_data[province_mask | city_mask]
        # 添加省份筛选
        if province != "All Provinces":
            self.filtered_data = self.filtered_data[self.filtered_data["省份"] == province]
        # 添加城市筛选
        if city != "All Cities":
            self.filtered_data = self.filtered_data[self.filtered_data["城市"] == city]

        # 在update_display方法中，替换原有的循环部分
        self.table_widget.setRowCount(len(self.filtered_data))
        # 重置索引以确保连续性
        reset_index_data = self.filtered_data.reset_index(drop=True)
        for i, row in reset_index_data.iterrows():
            self.table_widget.setItem(i, 0, QTableWidgetItem(row["学科门类"]))
            self.table_widget.setItem(i, 1, QTableWidgetItem(row["学科名称"]))
            self.table_widget.setItem(i, 2, QTableWidgetItem(str(row["学科代码"])))

            # 学校名称保持默认样式
            university_name = row["学校名称"]
            # 创建标签widget
            university_widget = QWidget()
            university_layout = QHBoxLayout(university_widget)
            university_layout.setContentsMargins(0, 0, 0, 0)
            university_layout.setSpacing(3)

            # 学校名称标签
            name_label = QLabel(university_name)
            name_label.setStyleSheet("color: #2C3E50; font-size: 10px;")
            university_layout.addStretch()
            university_layout.addWidget(name_label)

            # 添加标签
            if row["学校名称"] in self.c9_universities:
                tag_label = QLabel("C9")
                tag_label.setStyleSheet("""
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #32CD32, stop:1 #228B22);
                    color: white;
                    font-size: 7px;
                    font-weight: bold;
                    padding: 2px 4px;
                    border-radius: 3px;
                """)
                university_layout.addWidget(tag_label)
            elif row["学校名称"] in self._985_universities:
                tag_label = QLabel("985")
                tag_label.setStyleSheet("""
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E90FF, stop:1 #4169E1);
                    color: white;
                    font-size: 7px;
                    font-weight: bold;
                    padding: 2px 4px;
                    border-radius: 3px;
                """)
                university_layout.addWidget(tag_label)
            elif row["学校名称"] in self._211_universities:
                tag_label = QLabel("211")
                tag_label.setStyleSheet("""
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #9370DB, stop:1 #8A2BE2);
                    color: white;
                    font-size: 7px;
                    font-weight: bold;
                    padding: 2px 4px;
                    border-radius: 3px;
                """)
                university_layout.addWidget(tag_label)

            university_layout.addStretch()
            self.table_widget.setCellWidget(i, 3, university_widget)

            self.table_widget.setItem(i, 4, QTableWidgetItem(str(row["学校代码"])))

            # 评估等级颜色
            grade_item = QTableWidgetItem(row["评估等级"])
            grade_colors = {
                "A+": QColor(46, 204, 113),  # 绿色
                "A": QColor(52, 152, 219),  # 蓝色
                "A-": QColor(155, 89, 182),  # 紫色
                "B+": QColor(241, 196, 15),  # 黄色
                "B": QColor(230, 126, 34),  # 橙色
                "B-": QColor(231, 76, 60),  # 红色
                "C+": QColor(149, 165, 166),  # 灰色
                "C": QColor(127, 140, 141),  # 深灰
                "C-": QColor(52, 73, 94)  # 深蓝灰
            }
            if row["评估等级"] in grade_colors:
                grade_item.setForeground(grade_colors[row["评估等级"]])
                grade_item.setFont(QFont("Arial", 11, QFont.Bold))
            self.table_widget.setItem(i, 5, grade_item)

            # 添加省份和城市信息
            self.table_widget.setItem(i, 6, QTableWidgetItem(row["省份"] if pd.notna(row["省份"]) else ""))
            self.table_widget.setItem(i, 7, QTableWidgetItem(row["城市"] if pd.notna(row["城市"]) else ""))
            for j in range(8):  # 8列数据
                item = self.table_widget.item(i, j)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

        # 更新统计信息
        total_count = len(self.filtered_data)
        total_percentage = (total_count / len(self.data)) * 100 if len(self.data) > 0 else 0
        self.stats_label.setText(f"Showing {total_count} records ({total_percentage:.3f}% of total)")

        # 更新图表
        active_button = self.chart_buttons.checkedButton()
        if active_button:
            chart_type = active_button.property("chartType")
            self.update_chart(chart_type)

    def update_chart(self, chart_type):
        """更新图表"""
        if len(self.filtered_data) == 0:
            return

        chart = QChart()
        chart.setTheme(QChart.ChartThemeLight)
        chart.setBackgroundBrush(QBrush(QColor("white")))
        chart.setAnimationOptions(QChart.SeriesAnimations)

        if chart_type == "pie":
            # 饼图 - 评估等级分布
            grade_counts = self.filtered_data["评估等级"].value_counts()
            series = QPieSeries()
            series.setHoleSize(0.3)  # 环形图

            for grade, count in grade_counts.items():
                percentage = (count / len(self.filtered_data)) * 100
                slice = series.append(f"{grade}\n{count} ({percentage:.1f}%)", count)

                grade_colors = {
                    "A+": QColor(46, 204, 113),
                    "A": QColor(52, 152, 219),
                    "A-": QColor(155, 89, 182),
                    "B+": QColor(241, 196, 15),
                    "B": QColor(230, 126, 34),
                    "B-": QColor(231, 76, 60),
                    "C+": QColor(149, 165, 166),
                    "C": QColor(127, 140, 141),
                    "C-": QColor(52, 73, 94)
                }
                if grade in grade_colors:
                    slice.setBrush(grade_colors[grade])
                slice.setLabelVisible(True)

            chart.addSeries(series)
            chart.setTitle("Grade Distribution")


        elif chart_type == "bar":

            # 柱状图 - 各学科数量

            subject_counts = self.filtered_data["学科名称"].value_counts().head(8)

            series = QBarSeries()

            bar_set = QBarSet("Subject Count")

            bar_set.setColor(QColor(self.colors["accent"]))

            for subject, count in subject_counts.items():
                bar_set.append(count)

            series.append(bar_set)

            chart.addSeries(series)

            # 设置坐标轴

            axis_x = QBarCategoryAxis()

            axis_x.append([s[:10] + "..." if len(s) > 10 else s for s in subject_counts.index])

            axis_x.setLabelsAngle(-45)

            # 设置横坐标字体更小

            axis_x.setLabelsFont(QFont("Arial", 5))  # 将字体大小从默认值减小到8

            chart.addAxis(axis_x, Qt.AlignBottom)

            series.attachAxis(axis_x)

            axis_y = QValueAxis()

            chart.addAxis(axis_y, Qt.AlignLeft)

            series.attachAxis(axis_y)

            chart.setTitle("Top Subjects by Count")


        elif chart_type == "line":
            # 折线图 - 评估等级趋势
            grade_order = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-"]
            grade_counts = self.filtered_data["评估等级"].value_counts()

            series = QLineSeries()
            series.setColor(QColor(self.colors["accent"]))
            series.setPointsVisible(True)

            for i, grade in enumerate(grade_order):
                count = grade_counts.get(grade, 0)
                series.append(i, count)

            chart.addSeries(series)

            # 设置坐标轴
            axis_x = QCategoryAxis()
            for i, grade in enumerate(grade_order):
                axis_x.append(grade, i)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            chart.setTitle("Grade Trend Analysis")

        elif chart_type == "radar":
            # 雷达图 - 学科门类分布
            category_counts = self.filtered_data["学科门类"].value_counts()
            series = QPieSeries()

            for category, count in category_counts.items():
                slice = series.append(f"{category}\n{count}", count)
                slice.setLabelVisible(True)

            chart.addSeries(series)
            chart.setTitle("Category Distribution")

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        # 设置标题样式
        chart.setTitleBrush(QBrush(QColor(self.colors["text"])))
        chart.setTitleFont(QFont("Arial", 14, QFont.Bold))

        self.chart_view.setChart(chart)

    def update_realtime_data(self):
        """更新实时数据"""
        current_time = QTime.currentTime().toString("hh:mm:ss")
        total_records = len(self.data)
        current_display = len(self.filtered_data)
        percentage = (current_display / total_records * 100) if total_records > 0 else 0

        self.realtime_label.setText(
            f"🕐 Update Time: {current_time}\n"
            f"📊 Total Records: {total_records:,}\n"
            f"👁️ Current Display: {current_display:,}\n"
            f"🎯 Filter Ratio: {percentage:.1f}%"
        )

        # 随机更新进度条
        self.progress_bar.setValue(random.randint(70, 95))

    def show_statistics(self):
        """显示统计信息"""
        msg = QMessageBox()
        msg.setWindowTitle("Statistical Information")
        msg.setIcon(QMessageBox.Information)

        # 计算统计数据
        total_subjects = len(self.data["学科名称"].unique())
        total_universities = len(self.data["学校名称"].unique())
        total_categories = len(self.data["学科门类"].unique())

        stats_text = f"""
        📈 STATISTICAL OVERVIEW

        Total Subjects: {total_subjects:,}
        Total Universities: {total_universities:,}
        Total Categories: {total_categories:,}
        Total Records: {len(self.data):,}

        Grade Distribution:
        """

        grade_counts = self.data["评估等级"].value_counts()
        for grade, count in grade_counts.items():
            percentage = count / len(self.data) * 100
            stats_text += f"\n{grade}: {count:,} ({percentage:.1f}%)"

        msg.setText(stats_text)
        msg.exec()


def main():
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle('Fusion')

    # 设置应用程序字体
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    app.setWindowIcon(QIcon("app.ico"))

    # 创建并显示主窗口
    window = SubjectRankingApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()