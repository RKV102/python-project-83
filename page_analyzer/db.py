import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from requests import HTTPError
from flask import flash, request
import validators
from urllib.parse import urlparse


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def get_url_with_checks(id):
    url = select_data(
        ['id', 'name', 'created_at'],
        'urls',
        1,
        f'id = {id}'
    )
    check_count = select_data(
        ['COUNT(*)'],
        'url_checks',
        1,
        f'url_id = {id}'
    )[0]
    checks = select_data(
        ['id', 'created_at', 'status_code', 'h1', 'title', 'description'],
        'url_checks',
        check_count,
        f'url_id = {id}'
    )
    if check_count == 1:
        checks = [checks]
    return url, checks


def check_url(id):
    timestamp = datetime.now()
    url = select_data(
        ['name'],
        'urls',
        1,
        f'id = {id}'
    )[0]
    response = requests.get(url)
    try:
        response.raise_for_status()
    except HTTPError:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        status_code = response.status_code
        soup = BeautifulSoup(response.content, 'html.parser')
        h1 = soup.h1
        h1_string = h1.string if h1 else None
        title = soup.title
        title_string = title.string if title else None
        description = soup.find('meta', attrs={'name': 'description'})
        description_string = description.get('content') if description \
            else None
        insert_data(
            'url_checks',
            [
                'url_id', 'created_at', 'status_code', 'h1', 'title',
                'description'
            ],
            [
                id, timestamp, status_code, h1_string, title_string,
                description_string
            ]
        )


def get_urls():
    urls_count = select_data(
        ['COUNT(*)'],
        'urls',
        1
    )[0]
    urls = select_data(
        ['id', 'name'],
        'urls',
        urls_count
    )
    if urls_count == 1:
        urls = [urls]
    edited_urls = []
    for url in urls:
        check = select_data(
            ['created_at', 'status_code'],
            'url_checks',
            1,
            f'url_id = {url[0]}',
            'created_at DESC',
            1
        )
        if check:
            edited_urls.append([*url, check[0], check[1]])
        else:
            edited_urls.append([*url, None, None])
    return edited_urls


def add_url():
    url = request.form.get('url', '')
    error = None
    if validators.url(url) is not True:
        error = 'Некорректный URL'
    elif len(url) > 255:
        error = 'URL превышает 255 символов'
    if error:
        return None, url, error
    parsed_search = urlparse(url)
    normalized_search = parsed_search[0] + r'://' + parsed_search[1]
    id = select_data(
        ['id'],
        'urls',
        1,
        f"name = '{normalized_search}'"
    )
    if not id:
        timestamp = datetime.now()
        insert_data(
            'urls',
            ['name', 'created_at'],
            [normalized_search, timestamp]
        )
        id = select_data(
            ['MAX(id)'],
            'urls',
            1
        )[0]
        flash('Страница успешно добавлена', 'success')
    else:
        id = id[0]
        flash('Страница уже существует', 'warning')
    return id, url, error


def select_data(columns_, from_, count_, where_=None, order_by_=None,
                limit_=None):
    joined_columns = ', '.join(columns_)
    query = f'SELECT {joined_columns} FROM {from_}'
    if where_:
        query = f'{query} WHERE {where_}'
    if order_by_:
        query = f'{query} ORDER BY {order_by_}'
    if limit_:
        query = f'{query} LIMIT {limit_}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query)
            if count_ == 1:
                return cursor.fetchone()
            return cursor.fetchmany(count_)


def insert_data(into_, columns_, values_):
    joined_columns = f"({', '.join(columns_)})"
    shortcuts = ['%s'] * len(values_)
    joined_shortcuts = f"({', '.join(shortcuts)})"
    query = f'INSERT INTO {into_} {joined_columns} VALUES {joined_shortcuts}'
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(query, values_)
