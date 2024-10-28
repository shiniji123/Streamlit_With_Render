import psycopg2
from dotenv import load_dotenv
import os

# โหลด Environment Variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    # เชื่อมต่อกับฐานข้อมูล
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("Connected to the database successfully!")
    conn.close()
except Exception as e:
    print(f"Error connecting to database: {e}")
