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
    "fieldKeyType": "name",
    "take": 100
}

headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

# 打印 query_params 查看 projection 是否正确
print(f"Query Params: {query_params}")

response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)

if response_teable.status_code != 200:
    print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
    exit(1)

# 获取 Teable 已存在的 Issue 链接
existing_links = {}
teable_data = response_teable.json()
for record in teable_data.get("records", []):
    existing_links[record["fields"].get("github link")] = record["id"]

# 3️⃣ **去重，筛选出 Teable 中没有的 Issues**
new_records = []
updated_records = []
for issue in issues:
    issue_url = issue["html_url"]
    issue_id = issue["id"]  # 使用 GitHub issue 的 ID 作为唯一标识符
    
    assignees = ", ".join([assignee["login"] for assignee in issue["assignees"]])  # 获取所有 Assignees
    comments_url = issue["comments_url"]
    
    # 获取 issue 的最新评论
    response_comments = requests.get(comments_url, headers=headers_github)
    if response_comments.status_code == 200:
        comments = response_comments.json()
        comment_text = " ".join([comment["body"] for comment in comments])  # 合并评论
    else:
        print(f"❌ 获取评论失败: {response_comments.status_code}, {response_comments.text}")
        comment_text = "无评论"
    
    if issue_url not in existing_links:
        # 新的 issue 需要添加到 Teable
        new_records.append({
            "fields": {
                "What is it?": issue["title"],
                "github link": issue_url,
                "Assignees": assignees,
                "Comment": comment_text
            }
        })
    else:
        # 如果记录已经存在，则更新
        record_id = existing_links[issue_url]
        update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{record_id}"
        update_data = {
            "record": {
                "fields": {
                    "What is it?": issue["title"],
                    "github link": issue_url,
                    "Assignees": assignees,
                    "Comment": comment_text
                }
            },
            "fieldKeyType": "id"  # 使用 ID 作为字段键
        }
        
        update_response = requests.put(update_url, headers=headers_teable, json=update_data)
        
        if update_response.status_code == 200:
            print(f"✅ Issue {issue_url} 更新成功")
            updated_records.append(issue_url)
        else:
            print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")

# 4️⃣ **同步到 Teable**
if new_records:
    teable_insert_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
    data = {"records": new_records}
    
    response_insert = requests.post(teable_insert_url, headers=headers_teable, json=data)
    
    if response_insert.status_code == 201:
        print(f"✅ {len(new_records)} 条新 Issue 成功同步到 Teable")
    else:
        print(f"❌ Teable API 插入失败: {response_insert.status_code}, {response_insert.text}")

# 最后打印哪些 issue 被更新或者新增
if not new_records and not updated_records:
    print("⚠️ 没有新 Issue 需要同步，所有数据已存在。")
else:
    if new_records:
        print(f"✅ {len(new_records)} 条新记录已同步到 Teable。")
    if updated_records:
        print(f"✅ {len(updated_records)} 条记录已更新。")
