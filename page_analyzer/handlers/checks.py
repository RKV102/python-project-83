from flask import Blueprint, flash, redirect
from page_analyzer.db import get_url_by_id, get_url_name, add_check
from bs4 import BeautifulSoup
import requests


post_checks = Blueprint('post_checks', __name__, template_folder='templates')


@post_checks.post('/urls/<id>/checks')
def post_checks_(id):
    url = get_url_by_id(id, 'name')
    url_name = get_url_name(url)
    response = requests.get(url_name)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        flash('Произошла ошибка при проверке', 'error')
    else:
        flash('Страница успешно проверена', 'success')
        status_code = response.status_code
        h1, title, description = parse_response_content(response.content)
        add_check(id, status_code, h1, title, description)
    return redirect(f'/urls/{id}', code=302)


def parse_response_content(response_content, parser='html.parser'):
    soup = BeautifulSoup(response_content, parser)
    h1 = soup.h1
    h1_string = h1.string if h1 else None
    title = soup.title
    title_string = title.string if title else None
    description = soup.find('meta', attrs={'name': 'description'})
    description_string = description.get('content') if description \
        else None
    return h1_string, title_string, description_string
