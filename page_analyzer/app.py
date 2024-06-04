from flask import (Flask, render_template, request, flash, redirect,
                   get_flashed_messages)
from dotenv import load_dotenv
import os
import psycopg2
import validators
from urllib.parse import urlparse
from datetime import datetime


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
    id, name, date_and_time = conn_cursor.fetchone()
    conn_cursor.close()
    conn.close()
    message = get_flashed_messages(with_categories=True)[0]
    return render_template(
        'url.html',
        id=id,
        name=name,
        date=date_and_time.date(),
        message=message
    )


@app.get('/urls')
def get_urls():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    conn_cursor = conn.cursor()
    conn_cursor.execute("SELECT COUNT(*) FROM urls")
    urls_count = conn_cursor.fetchone()[0]
    conn_cursor.execute("SELECT id, name, created_at FROM urls")
    urls = conn_cursor.fetchmany(urls_count)
    return render_template(
        'urls.html',
        urls=urls
    )


@app.post('/urls')
def post_urls():
    url = request.form.get('url', '')
    if validators.url(url) is not True:
        return render_template(
            'index.html',
            url=url,
            errors=True
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
            + f"VALUES ('{normalized_search}', '{timestamp}')"
        )
        conn_cursor.execute("SELECT MAX(id) FROM urls")
        id = conn_cursor.fetchone()
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'warning')
    conn_cursor.close()
    conn.close()
    return redirect(f'/urls/{id[0]}', code=302)
