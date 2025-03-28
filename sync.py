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
repo_owner = 'your-github-username'
repo_name = 'your-repository-name'
issue_number = 1  # 这里是你要同步的 Issue 编号

# GitHub API 请求头部
headers = {
    'Authorization': f'token {gh_token}',
    'Accept': 'application/vnd.github.v3+json',
}

# 获取 GitHub Issue 数据
issue_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}'
response = requests.get(issue_url, headers=headers)

# 打印返回的响应内容
print(response.status_code)
print(response.json())  # 打印响应数据，查看是否包含 title 字段

# 检查响应内容是否正确
issue_data = response.json()

if 'title' in issue_data:
    issue_title = issue_data['title']
    issue_url = issue_data['html_url']
else:
    print(f"Error: 'title' not found in issue data. Response: {issue_data}")
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
