from flask import Blueprint, render_template, redirect, url_for, jsonify
from sqlalchemy.sql.expression import func

from flaskr.db import init_db
from flaskr.models import Wordle

bp = Blueprint('app', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/random')
def random():
    wordle = Wordle.query.order_by(func.random()).limit(1)[0]
    return redirect(wordle.url)


@bp.route('/about')
def about():
    return 'About'


@bp.route('/api/wordles', methods=['GET'])
def get_wordles():
    wordles = []
    for wordle in Wordle.query.all():
        wordles.append({'id': wordle.id, 'url': wordle.url, 'data': wordle.data, 'date': wordle.date})
    return jsonify(wordles)


@bp.route('/tools/init')
def init():
    init_db()
    return redirect(url_for('app.index'))
