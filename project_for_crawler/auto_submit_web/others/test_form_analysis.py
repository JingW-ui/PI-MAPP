#!/usr/bin/env python3
"""
测试表单结构分析功能
"""

from playwright.sync_api import sync_playwright

def analyze_form_test():
    """测试表单分析功能"""
    test_form_id = "Thvy0K"  # 使用用户提供的示例表单ID
    form_url = f"https://tjlvnuc7.jsjform.com/f/{test_form_id}"
    
    try:
        with sync_playwright() as p:
            print(f"正在启动浏览器...")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print(f"正在访问表单页面: {form_url}...")
            page.goto(form_url)
            page.wait_for_load_state('networkidle')
            
            print(f"正在获取表单字段...")
            # 获取所有输入字段
            fields = page.eval_on_selector_all(
                'input[name],select[name],textarea[name]',
                'els => els.map(e => ({key: e.name, label: e.labels?.[0]?.innerText ?? "", type: e.type}))'
            )
            
            browser.close()
            print(f"获取到的字段: {fields}")
            
            # 分析字段映射
            field_mapping = {}
            text_fields = [f for f in fields if f['type'] == 'text']
            
            if len(text_fields) >= 1:
                field_mapping['name'] = text_fields[0]['key']  # 第一个文本字段是姓名
            if len(text_fields) >= 2:
                field_mapping['class'] = text_fields[1]['key']  # 第二个文本字段可能是班级
            if len(text_fields) >= 3:
                field_mapping['student_id'] = text_fields[2]['key']  # 第三个文本字段可能是学号
            
            print(f"分析得到的字段映射: {field_mapping}")
            return field_mapping
            
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_form_test()