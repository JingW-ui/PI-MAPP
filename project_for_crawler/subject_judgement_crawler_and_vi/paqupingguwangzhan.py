import pypinyin
from DrissionPage import ChromiumPage
import pandas as pd
import time
import re
from pypinyin import lazy_pinyin
# 基础URL
BASE_URL = "https://www.cdgdc.edu.cn"
START_URL = f"{BASE_URL}/dslxkpgjggb/"
# -------------------- 1. 门类→缩写/代码段 映射表 --------------------
CATEGORY_MAP = {
    "人文社科类": {"abbr": "rwskl", "code_range": range(  1,   7)},   # 01xx
    "理学":       {"abbr": "lx",    "code_range": range(  7,  10)},   # 07xx
    "工学":       {"abbr": "gx",    "code_range": range( 10,  14)},   # 08xx
    "农学":       {"abbr": "nx",    "code_range": range( 14,  18)},   # 09xx
    "医学":       {"abbr": "yx",    "code_range": range( 18,  22)},   # 10xx
    "管理学":     {"abbr": "glx",   "code_range": range( 22,  26)},   # 12xx
    "艺术学":     {"abbr": "ysx",   "code_range": range( 26,  30)},   # 13xx
}
# ---------- 拼音缩写 -> 中文 ----------
PIN2CN = {
    'rwskl': '人文社科类',
    'lx':    '理学',
    'gx':    '工学',
    'nx':    '农学',
    'yx':    '医学',
    'glx':   '管理学',
    'ysx':   '艺术学',
}

# 中文 -> 拼音缩写
CN2PIN = {v: k for k, v in PIN2CN.items()}

# 两个工具函数
def get_cn(pinyin_abbr: str) -> str:
    """输入 'rwskl'  -> 输出 '人文社科类'"""
    return PIN2CN.get(pinyin_abbr.strip().lower(), '未知门类')

def get_pinyin(cn_name: str) -> str:
    """输入 '人文社科类' -> 输出 'rwskl'"""
    return CN2PIN.get(cn_name.strip(), 'unknown')
# -------------- 2. 从文本中提取学科代码+名称 --------------
SUBJ_RE = re.compile(r"^\s*(\d{4})\s+([^\s].+)$", re.M)

def extract_subjects_from_text(text: str):
    """
    从 print_all_subjects 打印出的原始文本里，
    提取所有 4 位学科代码及名称
    返回 list[ (code, name) ]
    """
    return SUBJ_RE.findall(text)


# -------------- 4. 构造单个学科 URL --------------
def build_subject_url(code: str, name: str,abbr: str) -> str:
    """
    构造规则：
    https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/{门类缩写}/a{代码}_{首字母小写拼音}.htm
    """
    chars = re.findall(r'[\u4e00-\u9fff]', name)
    # 首字母小写
    py_part = ''.join(lazy_pinyin(chars, style=pypinyin.FIRST_LETTER)).lower()

    return f"https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/{abbr}/a{code}_{py_part}.htm"
# -------------- 5. 一键生成所有学科 URL --------------
def build_all_subject_urls(text: str,abbr: str):
    """
    输入：print_all_subjects 得到的原始文本
    """
    subs = extract_subjects_from_text(text)
    url_list = []
    for code, name in subs:
        url = build_subject_url(code, name, abbr)
        url_list.append({
                'category': get_cn(abbr),
                'code': code,
                'name': name,
                'url': url
            })
    return url_list

def setup_browser():
    """设置浏览器配置"""
    page = ChromiumPage()
    page.set.window.size(1200, 800)
    return page


def find_fourth_round_link(page):
    """在主页找到第四轮学科评估的链接"""
    print("正在访问主页面...")
    page.get(START_URL)
    time.sleep(2)

    # 查找包含"第四轮"和"学科评估"的链接
    links = page.eles('tag:a')
    for link in links:
        link_text = link.text.strip()
        if 'a0' in link_text :
            fourth_round_url = link.attr('href')
            if fourth_round_url.startswith('/'):
                fourth_round_url = BASE_URL + fourth_round_url
            print(f"找到第四轮评估链接: {fourth_round_url}")
            return fourth_round_url

    print("未找到第四轮评估链接")
    return None


def get_all_subject_links(page, fourth_round_url):
    """获取所有学科的链接"""
    print("正在访问第四轮评估主页，获取所有学科链接...")
    page.get(fourth_round_url)
    time.sleep(3)

    # 获取页面所有文本内容
    table = page.ele('tag:table')
    page_text = table.text

    # 解析学科门类和学科代码
    subjects = []

    # 定义学科门类
    categories = ['人文社科类', '理学', '工学', '农学', '医学', '管理学', '艺术学']
    current_category = None

    lines = page_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检查是否是学科门类
        if any(category in line for category in categories):
            current_category = line
            print(f"找到学科门类: {current_category}")
            continue

        # 检查是否是学科行（包含4位数字代码）
        subject_match = re.match(r'(\d{4})\s+(.+)', line)
        if subject_match and current_category:
            subject_code = subject_match.group(1)
            subject_name = subject_match.group(2).strip()

            # 构建学科链接（根据您提供的模式）
            # 例如：a0819_kygc.htm
            subject_url = f"https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/gx/a{subject_code}_{get_pinyin_abbr(subject_name)}.htm"

            subjects.append({
                'category': current_category,
                'code': subject_code,
                'name': subject_name,
                'url': subject_url
            })
            print(f"  找到学科: {subject_code} {subject_name}")

    print(f"总共找到 {len(subjects)} 个学科")
    return subjects


def get_pinyin_abbr(chinese_name):
    """生成学科名称的拼音缩写（简化版，实际可能需要更复杂的处理）"""
    # 这里是一个简化的映射，实际应该使用完整的拼音转换库
    pinyin_map = {
        '力学': 'lx',
        '机械工程': 'jxgc',
        '光学工程': 'gxgc',
        '仪器科学与技术': 'yqkx',
        '材料科学与工程': 'clkx',
        '冶金工程': 'yjgc',
        '动力工程及工程热物理': 'dlgc',
        '电气工程': 'dqgc',
        '电子科学与技术': 'dzkx',
        '信息与通信工程': 'xxtx',
        '控制科学与工程': 'kzkx',
        '计算机科学与技术': 'jsjkx',
        '建筑学': 'jzx',
        '土木工程': 'tmgc',
        '水利工程': 'slgc',
        '测绘科学与技术': 'chkx',
        '化学工程与技术': 'hxgc',
        '地质资源与地质工程': 'dzzy',
        '矿业工程': 'kygc',
        '石油与天然气工程': 'sytrq',
        '纺织科学与工程': 'fzkx',
        '轻工技术与工程': 'qgjs',
        '交通运输工程': 'jtys',
        '船舶与海洋工程': 'cbhy',
        '航空宇航科学与技术': 'hkyh',
        '兵器科学与技术': 'bqkx',
        '核科学与技术': 'hkx',
        '农业工程': 'nygc',
        '林业工程': 'lygc',
        '环境科学与工程': 'hjkx',
        '生物医学工程': 'swyx',
        '食品科学与工程': 'spkx',
        '城乡规划学': 'cxgh',
        '风景园林学': 'fjyl',
        '软件工程': 'rjgc',
        '安全科学与工程': 'aqkx'
    }

    return pinyin_map.get(chinese_name, chinese_name[:4].lower())


def parse_subject_table(page, subject_url, category_name, subject_name, subject_code):
    """解析具体学科的评估结果表格"""
    print(f"正在解析: {subject_code} {subject_name}")

    try:
        page.get(subject_url)
        time.sleep(2)

        # 获取页面所有文本
        table = page.ele('tag:table')
        page_text = table.text

        # 解析评估结果
        results = []
        lines = page_text.split('\n')

        current_grade = None
        for line in lines:
            line = line.strip()

            # 检测等级行（A+, A, A-, B+, B, B-, C+, C, C-）
            grade_match = re.match(r'([ABC][+-]?)', line)
            if grade_match:
                current_grade = grade_match.group(1)
                # continue

            # 检测包含等级和学校信息的行
            # 匹配格式: "A+    10290      中国矿业大学"
            # print(line)
            combined_match = re.match(r'^([ABC][+-]?)\s+(\d{5})\s+([\u4e00-\u9fff]+大学|[\u4e00-\u9fff]+学院)', line)
            if combined_match:
                grade = combined_match.group(1)
                school_code = combined_match.group(2)
                school_name = combined_match.group(3)

                results.append({
                    '学科代码': subject_code,
                    '学科名称': subject_name,
                    '学科门类': category_name,
                    '学校代码': school_code,
                    '学校名称': school_name,
                    '评估等级': grade
                })
                continue
            # 检测学校行（学校代码 + 学校名称）
            school_match = re.match(r'(\d{5})\s+([\u4e00-\u9fff]+大学|[\u4e00-\u9fff]+学院)', line)
            if school_match and current_grade:
                school_code = school_match.group(1)
                school_name = school_match.group(2)

                results.append({
                    '学科代码': subject_code,
                    '学科名称': subject_name,
                    '学科门类': category_name,
                    '学校代码': school_code,
                    '学校名称': school_name,
                    '评估等级': current_grade
                })

        if results:
            df = pd.DataFrame(results)
            print(f"  成功提取 {len(df)} 条评估结果")
            return df
        else:
            print(f"  未找到评估结果: {subject_name}")
            return None

    except Exception as e:
        print(f"  解析失败 {subject_name}: {e}")
        return None





def debug_single_page():
    """调试函数：只爬取单个页面进行测试"""
    page = setup_browser()

    # 测试单个学科
    test_url = "https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/gx/a0819_kygc.htm"
    category_name = "工学"
    subject_name = "矿业工程"
    subject_code = "0819"

    try:
        result_df = parse_subject_table(page, test_url, category_name, subject_name, subject_code)
        if result_df is not None:
            print("测试成功！数据预览:")
            print(result_df)
            result_df.to_csv("debug_test.csv", index=False, encoding='utf-8-sig')

            # 显示这个学科的统计
            print(f"\n{subject_name} 评估结果统计:")
            print(result_df['评估等级'].value_counts().sort_index())
        else:
            print("测试失败")
    finally:
        page.quit()


def get_text(page, url):

    try:
        page.get(url)
        time.sleep(2)

        # 获取页面所有文本
        table = page.ele('tag:table')
        page_text = table.text
        return page_text


    except Exception as e:
        print(f"  解析失败 {url}: {e}")
        return None


def get_all_subjects():
    url_list = []
    url_list_subjects = []
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/rwskl/a0101_zx.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/lx/a0701_sx.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/gx/a0801_lx.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/nx/a0901_zwx.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/yx/a1001_jcyx.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/glx/a1201_glkxygc.htm')
    url_list.append('https://www.cdgdc.edu.cn/dslxkpgjggb/xkpm/ysx/a1301_ysxll.htm')
    for url in url_list:
        page = setup_browser()
        text = get_text(page, url)
        # print(text)
        abbr = url.split('/')[-2]
        df_url = build_all_subject_urls(text,abbr)
        for furl in df_url:
            url_list_subjects.append(furl)
    return  url_list_subjects
def main():
    """主函数"""
    print("初始化浏览器...")
    page = setup_browser()
    all_results = []

    try:

        # 2. 获取所有学科链接
        subjects = get_all_subjects()
        print(f"\n开始爬取 {len(subjects)} 个学科的数据...")

        # 3. 遍历每个学科
        for i, subject in enumerate(subjects, 1):
            print(f"\n[{i}/{len(subjects)}] ", end="")

            # 解析学科页面
            result_df = parse_subject_table(
                page,
                subject['url'],
                subject['category'],
                subject['name'],
                subject['code']
            )

            if result_df is not None:
                all_results.append(result_df)

            # 友好延迟
            time.sleep(1)

        # 4. 保存结果
        if all_results:
            final_df = pd.concat(all_results, ignore_index=True)

            # 保存为CSV文件
            output_file = "学科评估结果_第四轮.csv"
            final_df.to_csv(output_file, index=False, encoding='utf-8-sig')

            print(f"\n🎉 爬取完成！")
            print(f"📊 共获取 {len(all_results)} 个学科的数据")
            print(f"🏫 共 {len(final_df)} 条评估记录")
            print(f"💾 结果已保存到: {output_file}")

            # 显示数据预览
            print("\n数据预览:")
            print(final_df.head(10))

            # 显示统计信息
            print("\n评估等级统计:")
            print(final_df['评估等级'].value_counts().sort_index())

        else:
            print("未获取到任何数据")

    except Exception as e:
        print(f"爬取过程中出现错误: {e}")
    finally:
        print("\n关闭浏览器...")
        page.quit()
if __name__ == "__main__":
    # 运行调试模式（测试单个页面）
    # print("=== 调试模式 ===")
    # debug_single_page()

    # 运行完整爬取（取消注释下面这行）
    print("=== 完整爬取模式 ===")
    main()
