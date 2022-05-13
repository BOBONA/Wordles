from flask import Blueprint, render_template

from flaskr.db import init_db
from flaskr.models import Wordle

bp = Blueprint('app', __name__)


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/about')
def about():
    return 'About'


@bp.route('/test')
def testdb():
    init_db()
    wordles = Wordle.query.all()
    return {'result': str(wordles)}
