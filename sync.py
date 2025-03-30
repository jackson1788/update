import requests
import os

# 获取 GitHub Token
GH_TOKEN = os.getenv("GH_TOKEN")
if not GH_TOKEN:
    raise ValueError("❌ GH_TOKEN 未找到，请检查 GitHub Secrets")

headers_github = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# GitHub 配置
REPO_OWNER = "jackson1788"
REPO_NAME = "update"

# Teable 配置
TEABLE_TOKEN = "teable_acc3TYd8sn8wEYyyTNa_8p3MrgouOEhI82GBPjirUGyF+xPvSWoJKmTHcNTmu7o="
TABLE_ID = "tblsGQOJRAKhizNBYGN"

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

# 打印所有 issue 的 ID
for issue in issues:
    print(f"Issue Title: {issue['title']}, Issue ID: {issue['id']}")

# 2️⃣ 查询 Teable，获取所有已存在的 Issue ID 和 Record ID
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
query_params = {
    "fieldKeyType": "name",
    "take": 100,
    "page": 1
}

existing_records = {}

while True:
    response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)
    if response_teable.status_code != 200:
        print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
        exit(1)

    teable_data = response_teable.json()
    records = teable_data.get("records", [])

    print(f"📢 获取的 Teable 数据（页面 {query_params['page']}）：{len(records)} 条")

    for record in records:
        issue_id = record["fields"].get("Issue ID")
        record_id = record["id"]
        if issue_id:
            existing_records[issue_id] = record_id

    if len(records) < query_params["take"]:
        break

    query_params["page"] += 1  # 获取下一页

# 3️⃣ 强制更新所有评论为 "111"
update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"

for issue_id, record_id in existing_records.items():
    update_data = {
        "record": {
            "fields": {
                "Comment": "111"
            }
        },
        "fieldKeyType": "id",
        "typecast": True
    }

    update_response = requests.patch(f"{update_url}/{record_id}", headers=headers_teable, json=update_data)

    print(f"📢 更新记录 {record_id} (Issue ID: {issue_id}) 响应: {update_response.status_code} - {update_response.text}")

    if update_response.status_code == 200:
        print(f"✅ 记录 {record_id} 更新成功")
    else:
        print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")

print("✅ 完成强制更新所有记录的评论内容为 '111'。")
