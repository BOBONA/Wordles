from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func

from flaskr.db import Base


class Wordle(Base):
    __tablename__ = 'wordles'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), unique=True, nullable=False)
    likes = Column(Integer, default=0)
    data = Column(String(200), nullable=False)
    date = Column(Integer, nullable=False)
    source = Column(Integer, ForeignKey('sources.id'))

    def __init__(self, url, data, date, source_id):
        self.url = url
        self.data = data
        self.date = date
        self.source = source_id

    def __repr__(self):
        return f'<Wordle {self.url!r}>'


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    source_type = Column(String(30), nullable=False)
    last_fetched = Column(Integer, nullable=False)

    def __init__(self, name, source_type, last_fetched):
        self.name = name
        self.source_type = source_type
        self.last_fetched = last_fetched

    def __repr__(self):
        return f'<Source {self.name!r}>'


class IpAddress(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    address = Column(String(15), unique=True, nullable=False)
    likes = Column(ARRAY(Integer, ForeignKey('wordles.id')))
    date = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, address):
        self.address = address
        self.likes = []

    def __repr__(self):
        return f'<Address {self.address!r}>'
