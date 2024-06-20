from flask import Blueprint, render_template, get_flashed_messages
from page_analyzer.db import select_data


get_url = Blueprint('get_url', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
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
        f'url_id = {id}',
        'id'
    )
    if check_count == 1:
        checks = [checks]
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        message=message,
        checks=checks
    )
