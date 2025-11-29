import os
import sqlite3
from pymongo import MongoClient
import app as app

SQLITE_DB_PATH = "instance/users.db"
LOG_FILE_PATH = "app_log.txt"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "hospital_db"

def reset_sqlite():
    if os.path.exists(SQLITE_DB_PATH):
        os.remove(SQLITE_DB_PATH)
        print(f"Deleted SQLite database: {SQLITE_DB_PATH}")
    # Recreate empty SQLite database with User table
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("SQLite database recreated with User table.")

def reset_mongo():
    client = MongoClient(MONGO_URI)
    if MONGO_DB_NAME in client.list_database_names():
        client.drop_database(MONGO_DB_NAME)
        print(f"Dropped MongoDB database: {MONGO_DB_NAME}")
    db = client[MONGO_DB_NAME]
    # Recreate patients collection (empty)
    db.create_collection("patients")
    print("MongoDB database recreated with empty 'patients' collection.")

def reset_log():
    with open(LOG_FILE_PATH, "w") as f:
        f.write("")  # Clear the log
    print(f"Cleared log file: {LOG_FILE_PATH}")

if __name__ == "__main__":
    reset_sqlite()
    reset_mongo()
    reset_log()
    app.import_patients_from_csv(r"dataset\healthcare-dataset-stroke-data.csv")
    print("All reset successfully!")