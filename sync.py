import requests
import os

# GitHub 配置
GH_TOKEN = os.getenv("GH_TOKEN")
REPO_OWNER = "jackson1788"
REPO_NAME = "update"

# Teable 配置
TEABLE_TOKEN = "teable_acc3TYd8sn8wEYyyTNa_8p3MrgouOEhI82GBPjirUGyF+xPvSWoJKmTHcNTmu7o="
TABLE_ID = "tblsGQOJRAKhizNBYGN"

headers_github = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

# 1️⃣ 获取 GitHub Issues
issues_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues?state=open"
response = requests.get(issues_url, headers=headers_github)
if response.status_code != 200:
    print(f"❌ GitHub API 请求失败: {response.status_code}, {response.text}")
    exit(1)

issues = response.json()
for issue in issues:
    print(f"Issue Title: {issue['title']}, Issue ID: {issue['id']}")

# 2️⃣ 获取所有 Teable 记录
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
query_params = {"fieldKeyType": "name", "take": 100, "skip": 0}

existing_records = {}

while True:
    response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)
    if response_teable.status_code != 200:
        print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
        exit(1)

    teable_data = response_teable.json()
    records = teable_data.get("records", [])
    if not records:
        break

    for record in records:
        issue_id = record["fields"].get("Issue ID")
        if issue_id:
            existing_records[issue_id] = record["id"]

    query_params["skip"] += 100

# 3️⃣ 强制更新所有评论为 "111"
update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"

for record_id in existing_records.values():
    update_data = {
        "record": {"fields": {"Comment": "111"}},
        "fieldKeyType": "id",
        "typecast": True
    }

    update_response = requests.patch(f"{update_url}/{record_id}", headers=headers_teable, json=update_data)
    print(f"📢 更新响应: {update_response.status_code} - {update_response.text}")

print("✅ 完成强制更新所有记录的评论内容为 '111'。")
