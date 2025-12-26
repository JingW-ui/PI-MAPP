import requests
import json

# 1. 表单提交的GraphQL接口（你抓包到的）
submit_url = "https://jsj.top/graphql/f/NZCgUR"

# 2. 构造请求体（完全匹配抓包的JSON，仅替换字段值）
payload = {
  "operationName": "CreatePublishedFormEntry",
  "variables": {
    "input": {
      "formId": "NZCgUR",
      "geetest4Data": None,  # 无验证码填null/None
      "captchaData": None,
      "prefilledParams": "",
      "hasPreferential": False,
      "forceSubmit": False,
      "entryAttributes": {  # 这里替换成你要提交的真实数据
        "field_1": "何慧",  #姓名
        "field_2": "食研2501",    #班级
        "field_3": "2025309110003",   #学号
        "field_4": "食研2501",  # 班级
        "field_5": "2025309110003",  # 学号
        "field_6": "食研2501",  # 班级
        "field_7": "2025309110003"  # 学号

      },
      "fillingDuration": 30,  # 填写时长，随便填个数值即可
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

# 3. 构造请求头（必须带，否则会被拦截）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",  # GraphQL接口必须是JSON格式
    "Referer": "https://jinshuju.cool/f/VPp2uO",  # 来源页，必填
    "Origin": "https://jinshuju.cool"  # 跨域校验，必填
}

# 4. 发送POST请求（GraphQL需用json参数传体）
session = requests.Session()  # 保持会话，避免Cookie失效
response = session.post(
    url=submit_url,
    data=json.dumps(payload),  # 把字典转成JSON字符串
    headers=headers
)

# 5. 打印结果
print("提交状态码：", response.status_code)
print("服务器返回：", json.dumps(response.json(), ensure_ascii=False, indent=2))