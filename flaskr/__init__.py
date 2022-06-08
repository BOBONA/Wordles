import os

import click
from flask import Flask, current_app
from flask.cli import with_appcontext

from flaskr.models import Source, Wordle
from flaskr.reddit_scraper import normalize_url, is_wordle_url
from . import app as main_app, api, db, sources

STATIC_PATH = './static/'
BLACKLIST = STATIC_PATH + 'config/site_blacklist.txt'


def create_app():
    app = Flask(__name__, template_folder='.' + STATIC_PATH + 'templates')
    app.config.from_prefixed_env('WDL')
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.static_folder = '.' + STATIC_PATH
    app.register_blueprint(main_app.bp)
    app.register_blueprint(api.bp)
    db.init_app(app)
    app.cli.add_command(verify_wordles)
    app.cli.add_command(fetch_wordles)
    app.cli.add_command(init_db)
    return app


def attempt_multiple(func, times, exception):
    success = False
    i = 0
    while i < times and not success:
        try:
            func()
            success = True
        except exception as e:
            print(f'Attempt {i + 1}/10 failed, trying again')
            print(e)
            i += 1
    if success:
        print('SUCCESS')
    else:
        print('FAILED')


@click.command()
@with_appcontext
def verify_wordles():
    def update():
        session = db.db_session
        with open(BLACKLIST, 'r') as b:
            lines = b.read().splitlines()
            for wordle in Wordle.query.all():
                new = normalize_url(wordle.url)
                if new != wordle.url:
                    exists = Wordle.query.filter_by(url=new).first()
                    if exists:
                        session.delete(wordle)
                        session.commit()
                    else:
                        wordle.url = new
                if not is_wordle_url(wordle.url, lines):
                    session.delete(wordle)
        session.commit()
    print('Verifying wordles...')
    attempt_multiple(update, 10, Exception)


@click.command()
@with_appcontext
def fetch_wordles():
    def fetch():
        source_list = current_app.config['SOURCES']
        session = db.db_session
        with open(BLACKLIST, 'r') as b:
            blacklist = b.read().splitlines()
        lines = source_list.splitlines()
        for line in lines:
            source_data = line.split(' ')
            if len(source_data) >= 2 and source_data[0] and source_data[1]:
                source_type, name = source_data
                source = Source.query.filter_by(source_type=source_type, name=name).first()
                if source is None:
                    source = Source(name, source_type, 0)
                    session.add(source)
                    session.commit()
                sources.get(source_type)(source, session, current_app.config, blacklist)
            session.commit()
    print('Fetching wordles...')
    attempt_multiple(fetch, 10, Exception)


@click.command()
@with_appcontext
def init_db():
    print('Initializing database...')
    db.init_db()
    print('SUCCESS')
