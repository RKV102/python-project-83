from flask import Blueprint, render_template, get_flashed_messages
from page_analyzer.db import get_url_by_id, get_checks_by_id


get_url = Blueprint('get_url', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
    url = get_url_by_id(id, 'id', 'name', 'created_at')
    checks = get_checks_by_id(id)
    return render_template(
        'url.html',
        url=url,
        checks=checks
    )
