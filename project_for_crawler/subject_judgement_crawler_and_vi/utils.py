import pandas as pd


def merge_university_location(eval_file, location_file, output_file):
    """
    将大学的省份和城市信息追加到学科评估结果CSV文件中

    参数:
    eval_file: 学科评估结果CSV文件路径
    location_file: 大学省份城市CSV文件路径
    output_file: 输出文件路径
    """

    # 读取学科评估结果文件
    eval_df = pd.read_csv(eval_file, encoding='utf-8')

    # 读取大学位置信息文件
    location_df = pd.read_csv(location_file, encoding='utf-8')

    # 重命名location_df中的列以便合并
    location_df = location_df.rename(columns={
        'name': '学校名称',
        'province': '省份',
        'city': '城市'
    })

    # 将大学位置信息合并到评估结果中
    result_df = pd.merge(
        eval_df,
        location_df,
        on='学校名称',
        how='left'
    )

    # 保存结果到新文件
    result_df.to_csv(output_file, index=False, encoding='utf-8')

    return result_df



if __name__ == '__main__':
    merge_university_location(
        '学科评估结果_第四轮.csv',
        'univ_province_city.csv',
        '学科评估结果_第四轮_带地区信息.csv'
    )
