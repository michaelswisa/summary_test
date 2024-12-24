from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from analytics_service.database_postgres import Base


class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    events = relationship('Event', back_populates='group')
