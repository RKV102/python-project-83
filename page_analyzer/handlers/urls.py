from flask import Blueprint, render_template, flash, redirect, request
from page_analyzer.db import (get_all_urls, map_urls, select_url_id,
                              get_last_url_id, add_url)
from urllib.parse import urlparse
from datetime import datetime
import validators


get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')


@get_urls.get('/urls')
def get_urls_():
    urls = get_all_urls()
    urls_with_last_check = map_urls(urls)
    return render_template(
        'urls.html',
        urls=urls_with_last_check
    )


@post_urls.post('/urls')
def post_urls_():
    url = request.form.get('url', '')
    error = None
    if validators.url(url) is not True:
        error = 'Некорректный URL'
    elif len(url) > 255:
        error = 'URL превышает 255 символов'
    if error:
        return render_template(
            'index.html',
            url=url,
            error=error
        ), 422
    parsed_url = urlparse(url)
    normalized_url = parsed_url[0] + r'://' + parsed_url[1]
    id = select_url_id(normalized_url)
    if not id:
        timestamp = datetime.now()
        add_url(normalized_url, timestamp)
        id = get_last_url_id()
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'warning')
    return redirect(f'/urls/{id}', code=302)
