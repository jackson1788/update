import requests
import os
import json

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

# 2️⃣ 查询 Teable，获取所有数据
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

all_records = {}
page = 1
while True:
    query_params = {"fieldKeyType": "name", "take": 100, "skip": (page - 1) * 100}
    response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)
    
    if response_teable.status_code != 200:
        print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
        exit(1)

    teable_data = response_teable.json()
    records = teable_data.get("records", [])
    
    # 解析数据
    for record in records:
        fields = record["fields"]
        issue_id = fields.get("Issue ID")
        record_id = record.get("id")
        if issue_id and record_id:
            all_records[issue_id] = record_id
    
    print(f"📢 获取的 Teable 数据（页面 {page}）：{len(records)} 条")
    
    if len(records) < 100:
        break  # 没有更多数据了，停止分页查询
    page += 1

# 3️⃣ 仅更新 rec86OdkTsI4Pr9dAAx (Issue ID: 2958436443) 的 Comment 为 "222"
target_record_id = "rec86OdkTsI4Pr9dAAx"
target_issue_id = "2958436443"

if target_issue_id in all_records:
    update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{target_record_id}"
    update_data = {
        "record": {
            "fields": {
                "Comment": "222"
            }
        },
        "fieldKeyType": "name",
        "typecast": True
    }

    response = requests.patch(update_url, headers=headers_teable, json=update_data)

    # 打印更新结果
    print(f"📢 更新记录 {target_record_id} (Issue ID: {target_issue_id}) 响应: {response.status_code} - {response.text}")

    if response.status_code == 200:
        print(f"✅ 记录 {target_record_id} (Issue ID: {target_issue_id}) 更新成功")
    else:
        print(f"❌ Teable API 更新失败: {response.status_code}, {response.text}")
else:
    print(f"❌ 目标 Issue ID: {target_issue_id} 未在 Teable 中找到")

# 输出同步结果
print("✅ 完成特定记录的评论更新")
