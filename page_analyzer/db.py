import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_url_by_id(id, *columns):
    joined_columns = ', '.join(columns)
    query = f'SELECT {joined_columns} FROM urls WHERE id = {id}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()


def get_all_urls():
    query = 'SELECT id, name FROM urls ORDER BY id'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_last_check_by_id(id):
    query = 'SELECT created_at, status_code FROM url_checks '\
            f'WHERE url_id = {id} ORDER BY created_at DESC LIMIT 1'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()


def get_checks_by_id(id):
    query = 'SELECT id, created_at, status_code, h1, title, description '\
            f'FROM url_checks WHERE url_id = {id}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def select_url_id(url):
    query = f"SELECT id FROM urls WHERE name = '{url}'"
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            url_id = cursor.fetchone()
            if url_id:
                return url_id[0]
            return url_id


def get_last_url_id():
    query = 'SELECT MAX(id) FROM urls'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]


def add_url(url, created_at):
    query = 'INSERT INTO urls (name, created_at) VALUES (%s, %s)'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, (url, created_at))


def get_url_name(url):
    return url[0]


def add_check(id, created_at, status_code, h1, title, description):
    query = 'INSERT INTO url_checks (url_id, created_at, status_code, h1, '\
            'title, description) VALUES (%s, %s, %s, %s, %s, %s)'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, (id, created_at, status_code, h1, title,
                                   description))


def map_urls(urls):
    mapped_urls = []
    for url in urls:
        check = get_last_check_by_id(url[0])
        if check:
            mapped_urls.append([*url, *check])
        else:
            mapped_urls.append([*url, None, None])
    return mapped_urls
