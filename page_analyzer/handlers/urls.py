from flask import Blueprint, render_template, flash, redirect, request, url_for
from page_analyzer.db import (get_all_urls, add_last_check, get_url_by_name,
                              get_url_by_id, add_url, get_checks_by_id)
from urllib.parse import urlparse
import validators


get_url = Blueprint('get_url', __name__, template_folder='templates')
get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')


@get_url.get('/urls/<id>')
def get_url_(id):
    url = get_url_by_id(id)
    checks = get_checks_by_id(id)
    return render_template(
        'url.html',
        url=url,
        checks=checks
    )


@get_urls.get('/urls')
def get_urls_():
    urls = get_all_urls()
    urls_with_last_check = add_last_check(urls)
    return render_template(
        'urls.html',
        urls=urls_with_last_check
    )


@post_urls.post('/urls')
def post_urls_():
    url_name = request.form.get('url', '')
    error = validate(url_name)
    if error:
        flash(error, 'error')
        return render_template(
            'index.html'
        ), 422
    normalized_url_name = normalize(url_name)
    url = get_url_by_name(normalized_url_name)
    if not url:
        url = add_url(normalized_url_name)
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'warning')
    return redirect(url_for('get_url.get_url_', id=url['id']), code=302)


def normalize(url_name):
    parsed_url_name = urlparse(url_name)
    normalized_url = parsed_url_name.scheme + r'://' + parsed_url_name.hostname
    return normalized_url


def validate(url_name):
    if validators.url(url_name) is not True:
        return 'Некорректный URL'
    if len(url_name) > 255:
        return 'URL превышает 255 символов'
    return False
