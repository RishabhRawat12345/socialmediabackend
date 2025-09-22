import psycopg

# Replace with your actual credentials
DB_URL = "postgresql://postgres:dean@db.rwocivhozcmfswyilrwy.supabase.co:5432/postgres?sslmode=require"

try:
    # Connect to the database
    with psycopg.connect(DB_URL) as conn:
        # Create a cursor to execute queries
        with conn.cursor() as cur:
            cur.execute("SELECT version();")  # Test query
            version = cur.fetchone()
            print("✅ Connected! Database version:", version[0])

except Exception as e:
    print("❌ Connection failed:", e)
