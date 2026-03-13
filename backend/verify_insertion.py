import sqlite3
import os

db_path = 'c:/Users/sukuna/Downloads/KhudyakovINC/backend/data.db'

def verify_data():
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, position FROM team_members ORDER BY id DESC LIMIT 5")
    rows = cursor.fetchall()
    
    print("--- Last 5 entries in team_members table ---")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Position: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    verify_data()
