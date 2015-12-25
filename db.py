from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base

import os

Session = sessionmaker()


def _configure_database(engine):
    Base.metadata.create_all(engine)


def _is_configured(path):
    if os.path.isfile(path):
        return True


def configure_session(path='fuel.db'):
    engine = create_engine('sqlite:///{}'.format(path), echo=False)
    Session = sessionmaker(engine)
    Session.configure(bind=engine)
    if not _is_configured(path):
        _configure_database(engine)

    Base.metadata.bind = engine
