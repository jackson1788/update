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

# 3️⃣ 强制更新评论内容为 000
issue_id_to_update = "2958436443"  # 用你实际需要更新的 Issue ID
new_comment = "000"

# 尝试直接更新评论
update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{issue_id_to_update}"

update_data = {
    "record": {
        "fields": {
            "Comment": new_comment  # 强制更新评论内容为 "000"
        }
    },
    "fieldKeyType": "name",
    "typecast": True
}

print(f"❓ 发送更新请求: {json.dumps(update_data, indent=2)}")  # 打印更新请求的内容

update_response = requests.patch(update_url, headers={"Authorization": f"Bearer {TEABLE_TOKEN}", "Content-Type": "application/json"}, json=update_data)

# 打印更新响应
print(f"📢 更新响应: {update_response.status_code} - {update_response.text}")  # 打印更新响应

if update_response.status_code == 200:
    print(f"✅ Issue {issue_id_to_update} 更新成功")
else:
    print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")

# 4️⃣ 同步新数据到 Teable
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

# 输出同步结果
if new_records:
    teable_insert_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
    data = {"records": new_records}
    
    response_insert = requests.post(teable_insert_url, headers={"Authorization": f"Bearer {TEABLE_TOKEN}", "Content-Type": "application/json"}, json=data)
    
    if response_insert.status_code == 201:
        print(f"✅ {len(new_records)} 条新 Issue 成功同步到 Teable")
    else:
        print(f"❌ Teable API 插入失败: {response_insert.status_code}, {response_insert.text}")
else:
    print("⚠️ 没有新 Issue 需要同步，所有数据已存在。")
