from flask import Blueprint, render_template, get_flashed_messages
from page_analyzer.db import get_url_with_checks


get_url = Blueprint('get_url', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
    url, checks = get_url_with_checks(id)
    message = get_flashed_messages(with_categories=True)
    return render_template(
        'url.html',
        url=url,
        message=message,
        checks=checks
    )
