from flask import Blueprint, render_template, get_flashed_messages
import psycopg2
import os
from dotenv import load_dotenv


get_url = Blueprint('get_url', __name__, template_folder='templates')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@get_url.get('/urls/<id>')
def get_url_(id):
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
