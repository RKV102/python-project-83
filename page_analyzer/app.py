from flask import Flask, render_template
from dotenv import load_dotenv
import os
from page_analyzer.url import get_url
from page_analyzer.urls import get_urls, post_urls
from page_analyzer.checks import post_checks


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(get_url, url_prefix='/urls')
app.register_blueprint(get_urls, url_prefix='/urls')
app.register_blueprint(post_urls, url_prefix='/urls')
app.register_blueprint(post_checks, url_prefix='/urls')


@app.get('/')
def index():
    return render_template('index.html')
