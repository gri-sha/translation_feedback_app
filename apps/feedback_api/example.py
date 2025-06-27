from flask import Flask, jsonify, request
import sqlite3
from pprint import pprint
from util import DBManager, DataLoader

if __name__ == "__main__":
    db = DBManager()
    
    db.initialize_schema()
    db.load_example_data()
    

    data = {}
    
    # Simple connection for read operations
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        data['tables'] = cursor.fetchall()
        
        cursor.execute("SELECT * from Targets")
        data['targets'] = cursor.fetchall()
        
        cursor.execute("SELECT * from Translations")
        data['translations'] = cursor.fetchall()
        
        cursor.execute("SELECT * from Rankings")
        data['rankings'] = cursor.fetchall()
        
    finally:
        conn.close()
    
    for key, value in data.items():
        print(f"\n{key.upper()}:")
        pprint(value)