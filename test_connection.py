# test_connection.py
import os
from dotenv import load_dotenv
from app.models import get_db_connection

# Load environment variables from .env file
load_dotenv()

def test_connection():
    print("Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("✅ Database connection successful!")
        conn.close()
    else:
        print("❌ Database connection failed.")

if __name__ == '__main__':
    test_connection()