from flask import Blueprint, render_template, redirect
from sqlalchemy.sql.expression import func

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
    return render_template('about.html')
