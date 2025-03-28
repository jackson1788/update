import os
import psycopg2
import requests

# 获取环境变量
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_schema = os.getenv('DB_SCHEMA')
gh_token = os.getenv('GH_TOKEN')

# GitHub API URL 和 Headers
repo_owner = 'jackson1788'  # 替换为你的 GitHub 用户名
repo_name = 'update'  # 替换为你的仓库名称

# GitHub API 请求头部
headers = {
    'Authorization': f'token {gh_token}',
    'Accept': 'application/vnd.github.v3+json',
}

# 获取所有 GitHub Issues 数据（按创建时间排序）
issues_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=open'
response = requests.get(issues_url, headers=headers)

# 打印响应状态码和返回的数据
print("Response Status Code:", response.status_code)
print("Response JSON:", response.json())

# 检查响应内容并获取最新的 Issue 数据
issues_data = response.json()

if response.status_code == 200 and len(issues_data) > 0:
    latest_issue = issues_data[0]  # 获取创建的第一个 Issue
    issue_title = latest_issue['title']
    issue_url = latest_issue['html_url']
else:
    print(f"Error: Unable to retrieve issues. Response: {issues_data}")
    exit(1)

# 建立数据库连接
try:
    connection = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )

    cursor = connection.cursor()

    # 切换到指定的 Schema
    cursor.execute(f"SET search_path TO {db_schema};")

    # 假设你要将 GitHub Issue 数据同步到 New_tableYvvR0COMWm 表
    cursor.execute("""
        INSERT INTO New_tableYvvR0COMWm ("What is it?", "github link")
        VALUES (%s, %s)
    """, (issue_title, issue_url))

    # 提交并关闭连接
    connection.commit()
    cursor.close()

except Exception as e:
    print(f"Error: {e}")
finally:
    if connection:
        connection.close()
# 打印数据库连接配置
print(f"DB Host: {db_host}")
print(f"DB Port: {db_port}")
print(f"DB Name: {db_name}")
print(f"DB User: {db_user}")
