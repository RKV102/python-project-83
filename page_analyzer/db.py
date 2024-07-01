import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_url_by_id(id):
    query = f'SELECT * FROM urls WHERE id = {id}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            return cursor.fetchone()


def get_all_urls():
    query = 'SELECT id, name FROM urls ORDER BY id'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_last_check_by_id(id):
    query = 'SELECT created_at, status_code FROM url_checks '\
            f'WHERE url_id = {id} ORDER BY created_at DESC LIMIT 1'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            return cursor.fetchone()


def get_checks_by_id(id):
    query = 'SELECT id, created_at, status_code, h1, title, description '\
            f'FROM url_checks WHERE url_id = {id}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def get_url_id(url):
    query = f"SELECT id FROM urls WHERE name = '{url}'"
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            url_id = cursor.fetchone()
            if url_id:
                return url_id['id']
            return url_id


def get_last_url_id():
    query = 'SELECT MAX(id) FROM urls'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query)
            return cursor.fetchone()['max']


def add_url(url):
    query = 'INSERT INTO urls (name) VALUES (%s) RETURNING id'
    with (psycopg2.connect(DATABASE_URL) as connection):
        connection.autocommit = True
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor)\
                as cursor:
            cursor.execute(query, [url])
            return cursor.fetchone()['id']


def add_check(id, status_code, h1, title, description):
    query = 'INSERT INTO url_checks (url_id, status_code, h1, '\
            'title, description) VALUES (%s, %s, %s, %s, %s)'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, (id, status_code, h1, title, description))


def add_last_check(urls):
    urls_with_last_check = []
    for url in urls:
        url_with_last_check = {
            'id': url['id'],
            'name': url['name']
        }
        check = get_last_check_by_id(url['id'])
        if check:
            url_with_last_check['last_check_created_at'] = check['created_at']
            url_with_last_check['last_check_status_code'] = check['status_code']
        else:
            url_with_last_check['last_check_created_at'] = None
            url_with_last_check['last_check_status_code'] = None
        urls_with_last_check.append(url_with_last_check)
    return urls_with_last_check
