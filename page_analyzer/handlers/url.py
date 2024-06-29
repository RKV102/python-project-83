from flask import Blueprint, render_template
from page_analyzer.db import get_url_by_id, get_checks_by_id


get_url = Blueprint('get_url', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
    url = get_url_by_id(id, column_id=True, column_created_at=True)
    checks = get_checks_by_id(id)
    return render_template(
        'url.html',
        url=url,
        checks=checks
    )
