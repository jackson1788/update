import subprocess
import os

# 从环境变量中获取 GitHub Token
github_token = os.getenv('GH_TOKEN')

# 检查 token 是否为空，如果为空，抛出异常
if not github_token:
    raise ValueError("GitHub Token (GH_TOKEN) is not set or is empty.")

# 创建带认证的 GitHub 仓库 URL
repo_url = f"https://{github_token}@github.com/jackson1788/update.git"

# 克隆 GitHub 仓库
subprocess.run(["git", "clone", repo_url], check=True)
