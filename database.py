import sqlite3
import os

DATABASE_PATH = os.path.join('DATABASE', 'enova_gpt.db')

def create_connection():
    os.makedirs('DATABASE', exist_ok=True) 
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generation_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        contract_type TEXT,
        salaire TEXT,
        duree_stage TEXT,
        recruitment_post TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyze_cvs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        cv_score INTEGER,
        cv_path TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS linkedin_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        profile_link TEXT,
        profile_name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def insert_generation_post(job_title, contract_type, salaire, duree_stage, recruitment_post):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO generation_posts (job_title, contract_type, salaire, duree_stage, recruitment_post)
    VALUES (?, ?, ?, ?, ?)
    ''', (job_title, contract_type, salaire, duree_stage, recruitment_post))
    conn.commit()
    conn.close()

def insert_analyze_cv(job_title, cv_score, cv_path):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO analyze_cvs (job_title, cv_score, cv_path)
    VALUES (?, ?, ?)
    ''', (job_title, cv_score, cv_path))
    conn.commit()
    conn.close()

def insert_linkedin_profile(job_title, profile_link, profile_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO linkedin_profiles (job_title, profile_link, profile_name)
    VALUES (?, ?, ?)
    ''', (job_title, profile_link, profile_name))
    conn.commit()
    conn.close()



