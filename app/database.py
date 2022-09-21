from . import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

username = config.settings.DATABASE_USERNAME
password = config.settings.DATABASE_PASSWORD
host = config.settings.DATABASE_HOSTNAME
port = config.settings.DATABASE_PORT
database = config.settings.DATABASE_NAME

SQLALCHEMY_DATABASE_URL = f'postgresql://{username}:{password}@{host}:{port}/{database}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
