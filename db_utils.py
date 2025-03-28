# db_utils.py
import sqlite3
import pandas as pd

def init_db(db_path, table_name, schema: dict, primary_key: str):
    """
    Initialize the student table if it doesn't exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    col_defs = ', '.join([f"{col} TEXT" for col in schema])
    create_stmt = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {col_defs},
            PRIMARY KEY ({primary_key})
        );
    """
    cursor.execute(create_stmt)
    conn.commit()
    conn.close()


def insert_or_update(db_path, table_name, data: dict, primary_key: str):
    """
    Insert a new row or update existing based on the primary key.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?'] * len(data))
    updates = ', '.join([f"{k}=excluded.{k}" for k in data])

    query = f"""
        INSERT INTO {table_name} ({columns})
        VALUES ({placeholders})
        ON CONFLICT({primary_key}) DO UPDATE SET {updates};
    """
    cursor.execute(query, tuple(data.values()))
    conn.commit()
    conn.close()


def fetch_all_records(db_path, table_name):
    """
    Retrieve all records from the student table.
    """
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()
    return df


def delete_by_id(db_path, table_name, student_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
