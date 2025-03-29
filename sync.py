import requests
import os
import json

# 配置 GitHub 访问信息
GH_TOKEN = os.getenv("GH_TOKEN")  # GitHub 个人访问令牌
REPO_OWNER = "jackson1788"  # GitHub 用户名
REPO_NAME = "update"  # 仓库名称

# 配置 Teable 访问信息
TEABLE_TOKEN = "teable_acc3TYd8sn8wEYyyTNa_8p3MrgouOEhI82GBPjirUGyF+xPvSWoJKmTHcNTmu7o="  # Teable 访问令牌
TABLE_ID = "tblsGQOJRAKhizNBYGN"  # 替换为你的 Teable 表 ID

# 1️⃣ 获取 GitHub Issues
issues_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=open"
headers_github = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
response = requests.get(issues_url, headers=headers_github)

if response.status_code != 200:
    print(f"GitHub API 请求失败: {response.status_code}, {response.text}")
    exit(1)

issues = response.json()

# 2️⃣ 构造 Teable API 需要的记录格式
records = []
for issue in issues:
    records.append({
        "fields": {
            "What is it?": issue["title"],  # 标题
            "github link": issue["html_url"]  # GitHub Issue 链接
        }
    })

# 3️⃣ 调用 Teable API 创建记录
teable_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}
data = {"records": records}

response_teable = requests.post(teable_url, headers=headers_teable, json=data)

if response_teable.status_code == 201:
    print("✅ Issues 成功同步到 Teable")
else:
    print(f"❌ Teable API 请求失败: {response_teable.status_code}, {response_teable.text}")
