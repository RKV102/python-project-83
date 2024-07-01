import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def select_items(returned_items_num='one'):
    def wrapper(func):
        def inner(*args, **kwargs):
            with psycopg2.connect(DATABASE_URL) as connection:
                connection.autocommit = True
                with connection.cursor(
                        cursor_factory=psycopg2.extras.DictCursor)\
                        as cursor:
                    query = func(*args, **kwargs)
                    cursor.execute(query)
                    if returned_items_num == 'one':
                        return cursor.fetchone()
                    return cursor.fetchall()
        return inner
    return wrapper


def insert_items(func):
    def wrapper(*args, **kwargs):
        with psycopg2.connect(DATABASE_URL) as connection:
            connection.autocommit = True
            with connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor)\
                    as cursor:
                query, inserted_items = func(*args, **kwargs)
                query = f'{query} RETURNING *'
                cursor.execute(query, inserted_items)
                return cursor.fetchone()
    return wrapper


@select_items()
def get_url_by_id(id):
    query = f'SELECT * FROM urls WHERE id = {id}'
    return query


@select_items(returned_items_num='many')
def get_all_urls():
    query = 'SELECT id, name FROM urls ORDER BY id'
    return query


@select_items()
def get_last_check_by_id(id):
    query = 'SELECT created_at, status_code FROM url_checks '\
            f'WHERE url_id = {id} ORDER BY created_at DESC LIMIT 1'
    return query


@select_items(returned_items_num='many')
def get_checks_by_id(id):
    query = 'SELECT id, created_at, status_code, h1, title, description '\
            f'FROM url_checks WHERE url_id = {id}'
    return query


@select_items()
def get_url_by_name(url):
    query = f"SELECT * FROM urls WHERE name = '{url}'"
    return query


@insert_items
def add_url(url):
    query = 'INSERT INTO urls (name) VALUES (%s)'
    returned_items = [url]
    return query, returned_items


@insert_items
def add_check(id, status_code, h1, title, description):
    query = 'INSERT INTO url_checks (url_id, status_code, h1, '\
            'title, description) VALUES (%s, %s, %s, %s, %s)'
    returned_items = [id, status_code, h1, title, description]
    return query, returned_items


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
