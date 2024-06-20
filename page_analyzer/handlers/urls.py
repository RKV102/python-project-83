from flask import Blueprint, render_template, flash, redirect, request
from page_analyzer.db import select_data, insert_data
from urllib.parse import urlparse
from datetime import datetime
import validators


get_urls = Blueprint('get_urls', __name__, template_folder='templates')
post_urls = Blueprint('post_urls', __name__, template_folder='templates')


@get_urls.get('/urls')
def get_urls_():
    urls_count = select_data(
        ['COUNT(*)'],
        'urls',
        1
    )[0]
    urls = select_data(
        ['id', 'name'],
        'urls',
        urls_count,
        None,
        'id'
    )
    if urls_count == 1:
        urls = [urls]
    edited_urls = []
    for url in urls:
        check = select_data(
            ['created_at', 'status_code'],
            'url_checks',
            1,
            f'url_id = {url[0]}',
            'created_at DESC',
            1
        )
        if check:
            edited_urls.append([*url, check[0], check[1]])
        else:
            edited_urls.append([*url, None, None])
    return render_template(
        'urls.html',
        urls=edited_urls
    )


@post_urls.post('/urls')
def post_urls_():
    # id, url, error = add_url__()
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
    parsed_search = urlparse(url)
    normalized_search = parsed_search[0] + r'://' + parsed_search[1]
    id = select_data(
        ['id'],
        'urls',
        1,
        f"name = '{normalized_search}'"
    )
    if not id:
        timestamp = datetime.now()
        insert_data(
            'urls',
            ['name', 'created_at'],
            [normalized_search, timestamp]
        )
        id = select_data(
            ['MAX(id)'],
            'urls',
            1
        )[0]
        flash('Страница успешно добавлена', 'success')
    else:
        id = id[0]
        flash('Страница уже существует', 'warning')
    return redirect(f'/urls/{id}', code=302)
