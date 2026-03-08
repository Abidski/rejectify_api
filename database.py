import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

URL = os.getenv("DATABASE_URL")

if URL is None:
    raise RuntimeError("Cannot get dtabase url")

engine = create_engine(URL)

Session = sessionmaker(engine)


def get_db():
    with Session() as session:
        yield session
