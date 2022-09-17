from venv import create
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import dotenv_values


config = dotenv_values(".env")
username = config["USER"]
password = config["PASSWORD"]
host = config["HOST"]
database = config["DATABASE"]

SQLALCHEMY_DATABASE_URL = f'postgresql://{username}:{password}@{host}/{database}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()