import pandas as pd
import asyncio
import aiohttp
import aiofiles
import json
import pandas as pd
from tqdm.asyncio import tqdm_asyncio

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步批量获取中国高校 C9 / 985 / 211 / 双一流 / 双非 标签
数据来源：阳光高考（官方公开接口）
"""


# -------------------- 配置 --------------------
NAME_URL   = "https://static-data.gaokao.cn/www/2.0/school/name.json"
INFO_URL   = "https://static-data.gaokao.cn/www/2.0/school/{}/info.json"
CSV_FILE   = "univ_c9_985_211_shuangfei.csv"
CONCURRENCY = 50          # 并发量，可调
TIMEOUT     = 15          # 秒
# --------------------------------------------

semaphore = asyncio.Semaphore(CONCURRENCY)

async def get_json(session, url):
    """通用 GET 并返回 json"""
    async with semaphore:
        async with session.get(url, timeout=TIMEOUT) as resp:
            resp.raise_for_status()
            return await resp.json(content_type=None)

async def get_all_ids(session):
    """拉学校 ID 列表"""
    data = await get_json(session, NAME_URL)
    # 返回格式 {"data":[{school_id,name},...]}
    return [item["school_id"] for item in data["data"][:60]]

async def get_one_detail(session, school_id):
    """拉单个学校详情并解析关键字段"""
    url = INFO_URL.format(school_id)
    try:
        js = await get_json(session, url)
        d = js["data"]
        # 判断标签
        f985 = int(d.get("f985", 0))
        f211 = int(d.get("f211", 0))
        c9   = int(d.get("c9", 0))
        dfs  = int(d.get("doubleFirstClass", 0))
        level = d.get("level", "")

        # 双非逻辑：本科且非 211/985/双一流
        is_shuangfei = (level == "本科" and not (f211 or f985 or dfs))

        return {
            "school_id"    : school_id,
            "code"         : d.get("school_code", ""),
            "name"         : d.get("name", ""),
            "province"     : d.get("province_name", ""),
            "city"         : d.get("city_name", ""),
            "level"        : level,
            "is_c9"        : bool(c9),
            "is_985"       : bool(f985),
            "is_211"       : bool(f211),
            "is_double_first": bool(dfs),
            "is_shuangfei" : is_shuangfei,
            "address"      : d.get("address", ""),
            "website"      : d.get("school_site", ""),
        }
    except Exception as e:
        # 出错时返回空字典，后面统一过滤
        print(f"[WARN] {school_id} 失败: {e}")
        return None

async def main():
    async with aiohttp.ClientSession() as session:
        print("1. 拉取学校 ID 列表...")
        id_list = await get_all_ids(session)
        print(f"共 {len(id_list)} 所高校")

        print("2. 并发拉详情...")
        tasks = [get_one_detail(session, sid) for sid in id_list]
        results = await tqdm_asyncio.gather(*tasks)

    # 过滤 None
    df = pd.DataFrame([r for r in results if r])
    # 排序：985 -> 211 -> 双一流 -> 其他
    df["sort"] = (
        df["is_985"].astype(int) * 100 +
        df["is_211"].astype(int) * 10 +
        df["is_double_first"].astype(int)
    )
    df = df.sort_values(["sort", "name"], ascending=[False, True]).drop(columns="sort")

    print(f"3. 保存 CSV -> {CSV_FILE}")
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    print("完成！示例：")
    print(df.head())

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == '__main__':
    merge_university_location(
        '学科评估结果_第四轮.csv',
        'univ_province_city.csv',
        '学科评估结果_第四轮_带地区信息.csv'
    )
