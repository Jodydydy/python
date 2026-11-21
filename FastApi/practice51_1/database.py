import sqlite3

DB_NAME = "database.sqlite"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row #для получения данных в виде словаря
    return conn