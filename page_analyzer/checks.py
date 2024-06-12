from flask import flash, redirect, Blueprint
from dotenv import load_dotenv
import os
import psycopg2
import requests
from requests import HTTPError
from datetime import datetime
from bs4 import BeautifulSoup


post_checks = Blueprint('post_checks', __name__, template_folder='templates')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@post_checks.post('/<id>/checks')
def post_checks_(id):
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
