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
issue_map = {str(issue["id"]): issue["title"] for issue in issues}

print("📢 GitHub Issues 获取成功")
for issue_id, title in issue_map.items():
    print(f"Issue Title: {title}, Issue ID: {issue_id}")

# 2️⃣ 获取 GitHub Issues 的最新评论
latest_comments = {}
for issue in issues:
    comments_url = issue["comments_url"]
    comments_response = requests.get(comments_url, headers=headers_github)

    if comments_response.status_code == 200:
        comments = comments_response.json()
        if comments:
            last_comment = comments[-1]
            latest_comments[str(issue["id"])] = {
                "comment": last_comment["body"],
                "commenter": last_comment["user"]["login"]
            }

print("📢 获取最新评论成功:", latest_comments)

# 3️⃣ 查询 Teable，获取所有数据
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

# 4️⃣ 更新有新评论的 Issue 到 Teable
update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
for issue_id, comment_data in latest_comments.items():
    if issue_id in all_records:
        record_id = all_records[issue_id]
        update_data = {
            "record": {
                "fields": {
                    "Comment": comment_data["comment"],
                    "Commenter": comment_data["commenter"]
                }
            },
            "fieldKeyType": "name",  # 必须使用 "name" 否则 404
            "typecast": True
        }

        update_response = requests.patch(f"{update_url}/{record_id}", headers=headers_teable, json=update_data)

        print(f"📢 更新记录 {record_id} (Issue ID: {issue_id}) 响应: {update_response.status_code} - {update_response.text}")

        if update_response.status_code == 200:
            print(f"✅ 记录 {record_id} (Issue ID: {issue_id}) 更新成功")
        else:
            print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")

# ❌ 强制更新部分（已注释，可手动启用）
# for issue_id, record_id in all_records.items():
#     update_data = {
#         "record": {
#             "fields": {
#                 "Comment": "111"
#             }
#         },
#         "fieldKeyType": "name",
#         "typecast": True
#     }
#     update_response = requests.patch(f"{update_url}/{record_id}", headers=headers_teable, json=update_data)
#     print(f"📢 强制更新 {record_id} (Issue ID: {issue_id}) 响应: {update_response.status_code} - {update_response.text}")

print("✅ 完成同步最新的评论到 Teable。")
