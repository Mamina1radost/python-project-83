import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)


def add_url(url, conn=conn):
    with conn.cursor() as cur:
        cur.execute('''
        INSERT INTO urls (name, created_at) 
                    VALUES (%s, %s) RETURNING id;''', (url, datetime.now()))
        id = cur.fetchone()
        conn.commit()
        return id[0]
    
def get_url(id, conn=conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT * FROM urls WHERE id = %s;''', (id, ))
        id, name, created_at = cur.fetchone()
        return id, name, created_at
    

def get_name(conn=conn):
     with conn.cursor() as cur:
        cur.execute('''
            SELECT * FROM urls ORDER BY created_at DESC;''')
        data = cur.fetchall()
        return data
     
    
def get_url_by_name(name, conn=conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT * FROM urls WHERE name = %s;''', (name, ))
        url = cur.fetchone()
        if url is not None:
           url = url[0] 
        return url