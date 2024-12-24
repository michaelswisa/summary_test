from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from analytics_service.database_postgres import Base


class TargetType(Base):
    __tablename__ = 'target_types'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    events = relationship('Event', back_populates='target_type')
