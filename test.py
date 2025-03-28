import psycopg2

# 数据库连接信息
conn = psycopg2.connect(
    host="viaduct.proxy.rlwy.net",
    port="31408",
    dbname="railway",
    user="read_only_role_bseCwbXP2oUV7xTsdKl",
    password="********",
    options="-c search_path=bseCwbXP2oUV7xTsdKl"
)

# 验证连接是否成功
try:
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    print("Connection successful")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
    
try:
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'bseCwbXP2oUV7xTsdKl';
    """)
    tables = cur.fetchall()
    print(f"Tables in schema 'bseCwbXP2oUV7xTsdKl': {tables}")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
