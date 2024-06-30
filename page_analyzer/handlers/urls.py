from flask import Blueprint, render_template, flash, redirect, request, url_for
from page_analyzer.db import (get_all_urls, map_urls, get_url_id, get_url_by_id,
                              get_last_url_id, add_url, get_checks_by_id)
from urllib.parse import urlparse
import validators


get_url = Blueprint('get_url', __name__, template_folder='templates')
get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
    url = get_url_by_id(id, column_id=True, column_created_at=True)
    checks = get_checks_by_id(id)
    return render_template(
        'url.html',
        url=url,
        checks=checks
    )


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
    error = validiate(url)
    if error:
        flash(error, 'error')
        return render_template(
            'index.html'
        ), 422
    normalized_url = normalize_url(url)
    id = get_url_id(normalized_url)
    if not id:
        add_url(normalized_url)
        id = get_last_url_id()
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'warning')
    return redirect(url_for('get_url.get_url_', id=id), code=302)


def normalize_url(url):
    parsed_url = urlparse(url)
    normalized_url = parsed_url.scheme + r'://' + parsed_url.hostname
    return normalized_url


def validiate(url):
    if validators.url(url) is not True:
        return 'Некорректный URL'
    if len(url) > 255:
        return 'URL превышает 255 символов'
    return False
