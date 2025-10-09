import requests, pandas as pd

url = 'https://api.hcfpz.cn/un/schools'
data = requests.get(url, timeout=60).json()          # list[dict]
df = pd.DataFrame(data['data'])[['name', 'province', 'city']]
df.to_csv('univ_province_city.csv', index=False)
print(df.head())