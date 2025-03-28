import subprocess
import os

# 从环境变量中获取 GitHub Token
github_token = os.getenv('GH_TOKEN')

# 创建带认证的 GitHub 仓库 URL
repo_url = f"https://{github_token}@github.com/jackson1788/github-issue-sync.git"

# 克隆 GitHub 仓库
subprocess.run(["git", "clone", repo_url], check=True)
