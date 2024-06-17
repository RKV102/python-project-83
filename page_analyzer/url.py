from flask import Blueprint, render_template, get_flashed_messages
import psycopg2
import os
from dotenv import load_dotenv


get_url = Blueprint('get_url', __name__, template_folder='templates')
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@get_url.get('/urls/<id>')
def get_url_(id):
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
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        message=message,
        checks=checks
    )
