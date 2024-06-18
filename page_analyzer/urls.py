from flask import render_template, redirect, Blueprint
from page_analyzer.db import get_urls as get_urls__, add_url as add_url__


get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')


@get_urls.get('/urls')
def get_urls_():
    urls = get_urls__()
    return render_template(
        'urls.html',
        urls=urls
    )


@post_urls.post('/urls')
def post_urls_():
    id, url, error = add_url__()
    if error:
        return render_template(
            'index.html',
            url=url,
            error=error
        ), 422
    return redirect(f'/urls/{id}', code=302)
