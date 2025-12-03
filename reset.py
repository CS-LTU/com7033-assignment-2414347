import os
import sqlite3
from pymongo import MongoClient
import app as app

# Paths and configuration settings for resetting databases and logs
SQLITE_DB_PATH = "instance/users.db"
LOG_FILE_PATH = "app_log.txt"
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "hospital_db"

# ------------------------------------------------------------
# RESET SQLITE DATABASE (User Authentication Database)
# ------------------------------------------------------------
def reset_sqlite():
    """
    Deletes and recreates the SQLite database used for storing user accounts.
    This supports secure testing and allows resetting the environment safely.
    """

    # Remove existing DB if present
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
    """
    Drops and recreates the MongoDB database used for storing patient medical records.
    Ensures clean testing environment for CRUD operations.
    """
    client = MongoClient(MONGO_URI)
    if MONGO_DB_NAME in client.list_database_names():
        client.drop_database(MONGO_DB_NAME)
        print(f"Dropped MongoDB database: {MONGO_DB_NAME}")
    db = client[MONGO_DB_NAME]

    # Recreate patients collection (empty)
    db.create_collection("patients")
    print("MongoDB database recreated with empty 'patients' collection.")

# ------------------------------------------------------------
# RESET LOG FILE
# ------------------------------------------------------------
def reset_log():
    """
    Clears the application log file. Ensures clean logging for testing cycles.
    """
    with open(LOG_FILE_PATH, "w") as f:
        f.write("")  # Clear the log
    print(f"Cleared log file: {LOG_FILE_PATH}")

# ------------------------------------------------------------
# MAIN RESET EXECUTION — Used before demos/tests
# ------------------------------------------------------------
if __name__ == "__main__":
    reset_sqlite()
    reset_mongo()
    reset_log()
    # Reimport dataset into MongoDB after reset.
    app.import_patients_from_csv(r"dataset\healthcare-dataset-stroke-data.csv")
    print("All reset successfully!")
