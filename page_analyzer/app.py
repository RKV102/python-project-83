from flask import (Flask, render_template, request, flash, redirect,
                   get_flashed_messages)
from dotenv import load_dotenv
import os
import psycopg2
import validators
import requests
from requests import HTTPError
from urllib.parse import urlparse
from datetime import datetime
from bs4 import BeautifulSoup


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/urls/<id>')
def get_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute(
        f"SELECT id, name, created_at FROM urls WHERE id = {id}"
    )
    url = conn_cursor.fetchone()
    conn_cursor.execute(
        f"SELECT COUNT(*) FROM url_checks WHERE url_id = {id}"
    )
    check_count = conn_cursor.fetchone()[0]
    conn_cursor.execute(
        "SELECT id, created_at, status_code, h1, title, description "
        + f"FROM url_checks WHERE url_id = {id}"
    )
    checks = conn_cursor.fetchmany(check_count)
    conn_cursor.close()
    conn.close()
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        message=message,
        checks=checks
    )


@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute("SELECT COUNT(*) FROM urls")
    urls_count = conn_cursor.fetchone()[0]
    conn_cursor.execute(
        "SELECT urls.id, urls.name, urls.created_at AS url_created_at, "
        + "url_checks.created_at AS check_created_at FROM urls LEFT JOIN "
        + "url_checks ON urls.id = url_checks.url_id"
    )
    urls = conn_cursor.fetchmany(urls_count)
    conn_cursor.close()
    conn.close()
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def post_urls():
    url = request.form.get('url', '')
    error = None
    if validators.url(url) is not True:
        error = 'Некорректный URL'
    elif len(url) > 255:
        error = 'URL превышает 255 символов'
    if error:
        return render_template(
            'index.html',
            url=url,
            error=error
        ), 422
    parsed_search = urlparse(url)
    normalized_search = parsed_search[0] + r'://' + parsed_search[1]
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute(
        f"SELECT id FROM urls WHERE name = '{normalized_search}';"
    )
    id = conn_cursor.fetchone()
    if not id:
        timestamp = datetime.now()
        conn_cursor.execute(
            "INSERT INTO urls (name, created_at) "
            "VALUES (%s, %s)",
            (normalized_search, timestamp)
        )
        conn_cursor.execute("SELECT MAX(id) FROM urls")
        id = conn_cursor.fetchone()[0]
        flash('Страница успешно добавлена', 'success')
    else:
        id = id[0]
        flash('Страница уже существует', 'warning')
    conn_cursor.close()
    conn.close()
    return redirect(f'/urls/{id}', code=302)


@app.post('/urls/<id>/checks')
def post_checks(id):
    timestamp = datetime.now()
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute(
        f"SELECT name FROM urls WHERE id = {id}"
    )
    url = conn_cursor.fetchone()[0]
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
        conn_cursor.execute(
            "INSERT INTO url_checks (url_id, created_at, status_code, h1, "
            "title, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (id, timestamp, status_code, h1_string, title_string,
             description_string)
        )
    conn_cursor.close()
    conn.close()
    return redirect(f'/urls/{id}', code=302)
