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

# 2️⃣ 查询 Teable，获取已存在的 Issue ID
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
query_params = {
    "fieldKeyType": "name",
    "take": 100
}

headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)
if response_teable.status_code != 200:
    print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
    exit(1)

# 处理 Teable 返回的数据
existing_records = {}
teable_data = response_teable.json()
for record in teable_data.get("records", []):
    issue_id = record["fields"].get("Issue ID")
    if issue_id:
        existing_records[issue_id] = record["id"]

# 3️⃣ 处理新数据和更新数据
new_records = []
updated_records = []

for issue in issues:
    issue_id = str(issue["id"])  # GitHub Issue ID
    issue_url = issue["html_url"]
    assignees = ", ".join([assignee["login"] for assignee in issue["assignees"]])
    comments_url = issue["comments_url"]

    # 获取 issue 的最新评论
    response_comments = requests.get(comments_url, headers=headers_github)
    if response_comments.status_code == 200:
        comments = response_comments.json()
        comment_text = comments[-1]["body"] if comments else "无评论"
        commenter = comments[-1]["user"]["login"] if comments else "无评论人"
        print(f"评论内容: {comment_text}, 评论人: {commenter}")  # 打印评论
    else:
        print(f"❌ 获取评论失败: {response_comments.status_code}, {response_comments.text}")
        comment_text = "无评论"
        commenter = "无评论人"

    if issue_id not in existing_records:
        # 新 issue 需要添加
        new_records.append({
            "fields": {
                "Issue ID": issue_id,
                "Title": issue["title"],
                "Link": issue_url,
                "Assignees": assignees,
                "Comment": comment_text,
                "Commenter": commenter
            }
        })
    else:
        # 需要更新的记录
        record_id = existing_records[issue_id]
        update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{record_id}"
        update_data = {
            "fieldKeyType": "id",  # 这里改为 id
            "typecast": True,
            "record": {
                "fields": {
                    "Title": issue["title"],
                    "Link": issue_url,
                    "Assignees": assignees,
                    "Comment": "000",  # 强制更新评论内容为 "000"
                    "Commenter": commenter
                }
            },
            "order": {
                "viewId": "string",  # 根据需求提供具体的 viewId
                "anchorId": "string",  # 根据需求提供具体的 anchorId
                "position": "before"  # 可以是 before 或者 other
            }
        }

        print(f"❓ 发送更新请求: {json.dumps(update_data, indent=2)}")  # 打印更新请求的内容

        update_response = requests.patch(update_url, headers=headers_teable, json=update_data)
        
        # 打印更新响应
        print(f"📢 更新响应: {update_response.status_code} - {update_response.text}")  # 打印更新响应

        if update_response.status_code == 200:
            print(f"✅ Issue {issue_url} 更新成功")
            updated_records.append(issue_url)
        else:
            print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")

# 4️⃣ 同步新数据到 Teable
if new_records:
    teable_insert_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
    data = {"records": new_records}
    
    response_insert = requests.post(teable_insert_url, headers=headers_teable, json=data)
    
    if response_insert.status_code == 201:
        print(f"✅ {len(new_records)} 条新 Issue 成功同步到 Teable")
    else:
        print(f"❌ Teable API 插入失败: {response_insert.status_code}, {response_insert.text}")

# 输出同步结果
if not new_records and not updated_records:
    print("⚠️ 没有新 Issue 需要同步，所有数据已存在。")
else:
    if new_records:
        print(f"✅ {len(new_records)} 条新记录已同步到 Teable。")
    if updated_records:
        print(f"✅ {len(updated_records)} 条记录已更新。")
