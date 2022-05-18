import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.environ.get('DATABASE_URL').replace("://", "ql://", 1))  # to fix url thing
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_app(app):
    app.teardown_appcontext(close_db)


def close_db(e=None):
    db_session.remove()


def init_db():
    from . import models
    if not inspect(engine).has_table(models.Wordle):
        Base.metadata.create_all(bind=engine)
