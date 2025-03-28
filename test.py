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
