import os

import click
from flask import Flask, current_app
from flask.cli import with_appcontext

from flaskr.models import Blacklist, Source, Wordle
from . import app as main_app, db, sources

STATIC_PATH = './static/'
BLACKLIST = STATIC_PATH + 'site_blacklist.txt'
SOURCES = STATIC_PATH + 'sources.txt'


def create_app():
    app = Flask(__name__, template_folder='.' + STATIC_PATH + 'templates')
    app.config.from_prefixed_env('WDL')
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.static_folder = '.' + STATIC_PATH
    app.register_blueprint(main_app.bp)
    db.init_app(app)
    app.cli.add_command(update_blacklist)
    app.cli.add_command(fetch_wordles)
    return app


@click.command()
@with_appcontext
def update_blacklist():
    session = db.db_session
    with open(BLACKLIST, 'r') as b:
        lines = b.read().splitlines()
        for line in lines:
            url = Blacklist.query.filter(Blacklist.site == line).first()
            if not url:
                for wordle in Wordle.query.all():
                    if wordle.url.split('/')[2] == line:
                        session.delete(wordle)
                session.add(Blacklist(line))
    session.commit()


@click.command()
@with_appcontext
def fetch_wordles():
    with open(SOURCES, 'r') as s:
        session = db.db_session
        config = current_app.config
        with open(BLACKLIST, 'r') as b:
            blacklist = b.read().splitlines()
        lines = s.read().splitlines()
        for line in lines:
            source_data = line.split(' ')
            if len(source_data) >= 2 and source_data[0] and source_data[1]:
                source_type, name = source_data
                source = Source.query.filter_by(source_type=source_type, name=name).first()
                if source is None:
                    source = Source(name, source_type, 0)
                    session.add(source)
                    session.commit()
                sources.get(source_type)(source, session, config, blacklist)
            session.commit()
