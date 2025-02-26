import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bs4 import BeautifulSoup


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def add_url(url):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
        INSERT INTO urls (name, created_at) 
                    VALUES (%s, %s) RETURNING id;""",
            (url, datetime.now()),
        )
        id = cur.fetchone()
        conn.commit()
        return id[0]


def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT * FROM urls WHERE id = %s;""",
            (id,),
        )
        url_data = cur.fetchone()
        return url_data


def get_checks():
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT urls.id, urls.name, MAX(url_checks.created_at),
            MAX(url_checks.status_code)
            FROM urls LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id ORDER BY urls.created_at DESC;"""
        )
        data = cur.fetchall()
        return data


def get_url_by_name(name):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT * FROM urls WHERE name = %s;""",
            (name,),
        )
        url = cur.fetchone()
        if url is not None:
            url = url[0]
        return url


def create_check(url_id):
    conn = psycopg2.connect(DATABASE_URL)
    data = get_url(url_id)
    url = data[1]

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return "error"

    soup = BeautifulSoup(response.text, "html.parser")
    h1 = soup.find("h1")
    h1_text = h1.get_text() if h1 else ""

    title = soup.find("title")
    title_text = title.get_text() if title else ""

    meta_description = soup.find("meta", attrs={"name": "description"})
    description = (
        meta_description["content"]
        if (meta_description and "content" in meta_description.attrs)
        else ""
    )

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO url_checks (url_id, status_code,
            created_at, description, h1, title)
            VALUES (%s, %s, %s, %s, %s, %s);
        """,
            (
                url_id,
                response.status_code,
                datetime.now().date(),
                description,
                h1_text,
                title_text,
            ),
        )
        conn.commit()

    return "ok"


def read_all_check(url_id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT * FROM url_checks WHERE url_id = (%s)
        ORDER BY created_at DESC;""",
            (url_id,),
        )
        all_check_url = cur.fetchall()
        return all_check_url


def get_last_check(url_id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cur:
        cur.execute(
            """
        SELECT status_code, created_at FROM url_checks
        WHERE url_id = (%s) 
        ORDER BY created_at DESC LIMIT 1;""",
            (url_id,),
        )
        status_code, created_at = cur.fetchone()
        return status_code, created_at
