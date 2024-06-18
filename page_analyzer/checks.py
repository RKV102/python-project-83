from flask import redirect, Blueprint
from page_analyzer.db import check_url


post_checks = Blueprint('post_checks', __name__, template_folder='templates')


@post_checks.post('/urls/<id>/checks')
def post_checks_(id):
    check_url(id)
    return redirect(f'/urls/{id}', code=302)
