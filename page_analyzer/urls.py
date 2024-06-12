from flask import render_template, request, flash, redirect, Blueprint
from dotenv import load_dotenv
import os
import psycopg2
import validators
from urllib.parse import urlparse
from datetime import datetime


get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@get_urls.get('/urls')
def get_urls_():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute("SELECT COUNT(*) FROM urls")
    urls_count = conn_cursor.fetchone()[0]
    conn_cursor.execute(
        "SELECT urls.id, urls.name, url_checks.created_at AS check_created_at, "
        "url_checks.status_code FROM urls LEFT JOIN "
        "url_checks ON urls.id = url_checks.url_id"
    )
    urls = conn_cursor.fetchmany(urls_count)
    conn_cursor.close()
    conn.close()
    return render_template(
        'urls.html',
        urls=urls
    )


@post_urls.post('/urls')
def post_urls_():
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
