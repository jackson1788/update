import requests
import os
import json

# 获取Teable配置
TEABLE_TOKEN = "你的TeableToken"
TABLE_ID = "你的TableID"

# 配置Teable API请求头
headers_teable = {
    "Authorization": f"Bearer {TEABLE_TOKEN}",
    "Content-Type": "application/json"
}

# 获取现有记录
teable_query_url = f"https://app.teable.io/api/table/{TABLE_ID}/record"
query_params = {
    "take": 100  # 根据需要调整查询数量
}
response_teable = requests.get(teable_query_url, headers=headers_teable, params=query_params)

if response_teable.status_code != 200:
    print(f"❌ Teable API 查询失败: {response_teable.status_code}, {response_teable.text}")
    exit(1)

# 获取并更新所有记录
teable_data = response_teable.json()
for record in teable_data.get("records", []):
    record_id = record["id"]
    update_url = f"https://app.teable.io/api/table/{TABLE_ID}/record/{record_id}"

    # 更新评论内容为 "111"
    update_data = {
        "record": {
            "fields": {
                "Comment": "111"  # 强制更新评论内容为 "111"
            }
        },
        "fieldKeyType": "id",
        "typecast": True
    }

    print(f"❓ 发送更新请求: {json.dumps(update_data, indent=2)}")  # 打印更新请求的内容
    update_response = requests.patch(update_url, headers=headers_teable, json=update_data)

    print(f"📢 更新响应: {update_response.status_code} - {update_response.text}")  # 打印更新响应

    if update_response.status_code == 200:
        print(f"✅ 记录 {record_id} 评论更新成功")
    else:
        print(f"❌ Teable API 更新失败: {update_response.status_code}, {update_response.text}")
