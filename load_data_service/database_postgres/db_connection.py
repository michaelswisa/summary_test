from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from load_data_service.config import POSTGRES_URL
from load_data_service.database_postgres import Base

engine = create_engine(POSTGRES_URL)
session_maker = sessionmaker(bind=engine)
db_session = scoped_session(session_maker)


def init_db():
    Base.metadata.create_all(engine)


def get_session():
    return db_session
