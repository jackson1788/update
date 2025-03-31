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

# 通过工作流参数传递触发的 Issue ID
trigger_issue_id = os.getenv("TRIGGER_ISSUE_ID")  # 通过环境变量获取 Issue ID

if not trigger_issue_id:
    raise ValueError("❌ TRIGGER_ISSUE_ID 未找到，请检查工作流配置")
print(f"📢 触发的 Issue ID: {trigger_issue_id}")

# 1️⃣ 获取 GitHub Issue 详细信息
issue_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{trigger_issue_id}"
response = requests.get(issue_url, headers=headers_github)

if response.status_code != 200:
    print(f"❌ GitHub API 请求失败: {response.status_code}, {response.text}")
    exit(1)

issue = response.json()

# 获取评论
comments_url = issue["comments_url"]
comments_response = requests.get(comments_url, headers=headers_github)

if comments_response.status_code == 200:
    comments = comments_response.json()
    if comments:
        last_comment = comments[-1]
        latest_comment = last_comment["body"]
        commenter = last_comment["user"]["login"]
    else:
        latest_comment = ""
        commenter = ""
else:
    print(f"❌ 获取评论失败: {comments_response.status_code}, {comments_response.text}")
    exit(1)

print(f"📢 最新评论: {latest_comment}, 评论者: {commenter}")

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

# 3️⃣ 更新触发 Issue 的评论与负责人到 Teable
if trigger_issue_id in all_records:
    record_id = all_records[trigger_issue_id]
    print(f"📢 触发的 Issue ID: {trigger_issue_id}, 对应的 Teable 记录 ID: {record_id}")

    update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{record_id}"
    update_data = {
        "record": {
            "fields": {
                "Comment": latest_comment,
                "Commenter": latest_commenter
            }
        },
        "fieldKeyType": "name",
        "typecast": True
    }

    update_response = requests.patch(update_url, headers=headers_teable, json=update_data)
    print(f"📢 更新记录 {record_id} 响应: {update_response.status_code} - {update_response.text}")
else:
    print(f"❌ 未找到 Issue ID {trigger_issue_id} 对应的 Teable 记录，无法更新。")

print("✅ 完成同步触发 Issue 的评论和负责人到 Teable。")
