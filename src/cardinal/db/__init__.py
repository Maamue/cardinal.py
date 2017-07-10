import contextlib
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from __main__ import config

engine = create_engine(config['db_connectstring'], pool_size=20, max_overflow=100)
Base = declarative_base()
_Session = sessionmaker()
_Session.configure(bind=engine)


@contextlib.contextmanager
def session_scope():
    session = _Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()