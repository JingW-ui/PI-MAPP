import re

def find_chinese_characters(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找中文字符
    chinese_pattern = r'[\u4e00-\u9fff]+'
    chinese_matches = re.findall(chinese_pattern, content)
    
    # 查找包含中文的行
    lines = content.split('\n')
    chinese_lines = []
    for i, line in enumerate(lines, 1):
        if re.search(chinese_pattern, line):
            chinese_lines.append((i, line.strip()))
    
    # 获取不重复的中文词语
    unique_chinese = list(set(chinese_matches))
    
    print(f"Found {len(unique_chinese)} unique Chinese words/phrases:")
    for word in sorted(unique_chinese):
        print(repr(word))
    
    print(f"\nFound {len(chinese_lines)} lines containing Chinese characters:")
    for line_num, line_content in chinese_lines[:30]:  # 仅显示前30行以避免输出过多
        print(f"Line {line_num}: {line_content}")
    
    if len(chinese_lines) > 30:
        print(f"... and {len(chinese_lines) - 30} more lines")

if __name__ == "__main__":
    file_path = r"H:\pycharm_project\github_projects\PI-MAPP\project\Brain_Tumor_dection_ui\Brain_Tumor_detection_ui.py"
    find_chinese_characters(file_path)