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
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id, name, created_at FROM urls WHERE id = {id}"
            )
            url = cursor.fetchone()
            cursor.execute(
                f"SELECT COUNT(*) FROM url_checks WHERE url_id = {id}"
            )
            check_count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id, created_at, status_code, h1, title, description "
                + f"FROM url_checks WHERE url_id = {id}"
            )
            checks = cursor.fetchmany(check_count)
    return url, checks


def check_url(id):
    timestamp = datetime.now()
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT name FROM urls WHERE id = {id}"
            )
            url = cursor.fetchone()[0]
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
                description = soup.find(
                    'meta',
                    attrs={'name': 'description'}
                )
                description_string = description.get('content') if description \
                    else None
                cursor.execute(
                    "INSERT INTO url_checks (url_id, created_at, status_code, "
                    "h1, title, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id, timestamp, status_code, h1_string, title_string,
                     description_string)
                )


def get_urls():
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM urls")
            urls_count = cursor.fetchone()[0]
            cursor.execute(
                "SELECT urls.id, urls.name, url_checks.created_at AS "
                "check_created_at, url_checks.status_code FROM urls LEFT JOIN "
                "url_checks ON urls.id = url_checks.url_id"
            )
            urls = cursor.fetchmany(urls_count)
    return urls


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
    with psycopg2.connect(DATABASE_URL) as connection:
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id FROM urls WHERE name = '{normalized_search}';"
            )
            id = cursor.fetchone()
            if not id:
                timestamp = datetime.now()
                cursor.execute(
                    "INSERT INTO urls (name, created_at) "
                    "VALUES (%s, %s)",
                    (normalized_search, timestamp)
                )
                cursor.execute("SELECT MAX(id) FROM urls")
                id = cursor.fetchone()[0]
                flash('Страница успешно добавлена', 'success')
            else:
                id = id[0]
                flash('Страница уже существует', 'warning')
    return id, url, error
