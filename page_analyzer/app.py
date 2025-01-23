from flask import Flask, render_template, request, redirect, url_for, flash
import validators
from .db import add_url, get_url, get_name, get_url_by_name
from urllib.parse import urlparse
from dotenv import load_dotenv
import os



load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def create_url():
    url = request.form['url']
    if validators.url(url):
        normalize_url = urlparse(url)
        base_url = f"{normalize_url.scheme}://{normalize_url.netloc}"
        check_url = get_url_by_name(base_url)
        if not check_url:
            id = add_url(base_url)
            flash("Страница успешно добавлена", category='alert-success')
            return redirect(url_for('url_id', id=id))
        else:
            flash("Страница уже существует", category='alert-info')
            return redirect(url_for('url_id', id=check_url))
    else:
        flash('Некорректный URL', category='alert-danger')
        return redirect(url_for('index'))

@app.route('/urls/<int:id>')
def url_id(id):
    id, name, created_at = get_url(id)
    return render_template('urls.html', id=id, name=name, created_at=created_at)


@app.route('/urls')
def all_url():
    data = get_name()
    return render_template('urls_list.html', all_urls=data)


