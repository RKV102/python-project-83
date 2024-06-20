from flask import Flask, render_template
from dotenv import load_dotenv
from page_analyzer.handlers.urls import get_urls, post_urls
from page_analyzer.handlers.url import get_url
from page_analyzer.handlers.checks import post_checks
import os


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.register_blueprint(get_url)
app.register_blueprint(get_urls)
app.register_blueprint(post_urls)
app.register_blueprint(post_checks)


@app.get('/')
def index():
    return render_template('index.html')
