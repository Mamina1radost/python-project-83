import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException

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
        url_data = cur.fetchone()
        return url_data
    

def get_name(conn=conn):
     with conn.cursor() as cur:
        cur.execute('''
            SELECT urls.id, urls.name, MAX(url_checks.created_at), MAX(url_checks.status_code) 
            FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id GROUP BY urls.id ORDER BY urls.created_at DESC;''')
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
    

def create_check(url_id, conn=conn):
    data = get_url(url_id)
    url = data[1]
    try:
        code = requests.get(url)
    except ConnectionError as e:
        return 'error'
    with conn.cursor() as cur:
        cur.execute('''
        INSERT INTO url_checks (url_id, status_code, created_at) VALUES (%s, %s, %s) RETURNING id;''', (url_id, code.status_code, datetime.now()))
        check_url_id = cur.fetchone()
        conn.commit()
        return check_url_id[0]


def read_all_check(url_id, conn=conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT * FROM url_checks WHERE url_id = (%s) ORDER BY created_at DESC;''', (url_id, ))
        all_check_url = cur.fetchall()
        return all_check_url
    

def get_last_check(url_id, conn=conn):
    with conn.cursor() as cur:
        cur.execute('''
        SELECT status_code, created_at FROM url_checks
        WHERE url_id = (%s) 
        ORDER BY created_at DESC LIMIT 1;''', (url_id, ))
        status_code, created_at = cur.fetchone()
        return status_code, created_at