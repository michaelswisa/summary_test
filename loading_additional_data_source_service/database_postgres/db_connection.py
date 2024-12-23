from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from analytics_service.config import POSTGRES_URL

engine = create_engine(POSTGRES_URL)
session_maker = sessionmaker(bind=engine)
db_session = scoped_session(session_maker)

def get_session():
    return db_session