import requests
import os
import json

# 配置 GitHub 访问信息
GH_TOKEN = os.getenv("GH_TOKEN")  # GitHub 个人访问令牌
REPO_OWNER = "jackson1788"  # GitHub 用户名
REPO_NAME = "update"  # 仓库名称

# 配置 Teable 访问信息
TEABLE_TOKEN = "teable_acc3TYd8sn8wEYyyTNa_8p3MrgouOEhI82GBPjirUGyF+xPvSWoJKmTHcNTmu7o="  # Teable 访问令牌
TABLE_ID = "tblsGQOJRAKhizNBYGN"  # Teable 表 ID

# 1️⃣ **获取 GitHub Issues**
issues_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=open"
headers_github = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
response = requests.get(issues_url, headers=headers_github)

if response.status_code != 200:
    print(f"❌ GitHub API 请求失败: {response.status_code}, {response.text}")
    exit(1)

issues = response.json()

# 2️⃣ **查询 Teable，获取已存在的 github link**
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
query_params = {
    "projection": ["github link"]  # ✅ 修正：使用数组
}
headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

response_teable = requests.get(teable_query_url, headers=headers_teable, json=query_params)  # ✅ 传递 JSON 参数

if response_teable.status_code != 200:
    print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
    exit(1)

# 获取 Teable 已存在的 Issue 链接
existing_links = set()
teable_data = response_teable.json()
for record in teable_data.get("records", []):
    existing_links.add(record["fields"].get("github link"))

# 3️⃣ **去重，筛选出 Teable 中没有的 Issues**
new_records = []
for issue in issues:
    if issue["html_url"] not in existing_links:  # 只添加 Teable 没有的 Issue
        new_records.append({
            "fields": {
                "What is it?": issue["title"],
                "github link": issue["html_url"]
            }
        })

# 4️⃣ **同步到 Teable**
if new_records:
    teable_insert_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
    data = {"records": new_records}
    
    response_insert = requests.post(teable_insert_url, headers=headers_teable, json=data)
    
    if response_insert.status_code == 201:
        print(f"✅ {len(new_records)} 条新 Issue 成功同步到 Teable")
    else:
        print(f"❌ Teable API 插入失败: {response_insert.status_code}, {response_insert.text}")
else:
    print("⚠️ 无新 Issue 需要同步，所有数据已存在。")
