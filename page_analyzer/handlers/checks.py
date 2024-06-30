from flask import Blueprint, flash, redirect, url_for
from page_analyzer.db import get_url_by_id, add_check
from bs4 import BeautifulSoup
import requests


post_checks = Blueprint('post_checks', __name__, template_folder='templates')


@post_checks.post('/urls/<id>/checks')
def post_checks_(id):
    url = get_url_by_id(id)
    url_name = url['name']
    try:
        response = requests.get(url_name, timeout=(3, 5))
        response.raise_for_status()
    except (requests.HTTPError, requests.exceptions.Timeout):
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        status_code = response.status_code
        h1, title, description = parse(response.content)
        add_check(id, status_code, h1, title, description)
    return redirect(url_for('get_url.get_url_', id=id), code=302)


def parse(content):
    soup = BeautifulSoup(content, 'html.parser')
    h1 = soup.h1
    h1_string = h1.string if h1 else None
    title = soup.title
    title_string = title.string if title else None
    description = soup.find('meta', attrs={'name': 'description'})
    description_string = description.get('content') if description \
        else None
    return h1_string, title_string, description_string
