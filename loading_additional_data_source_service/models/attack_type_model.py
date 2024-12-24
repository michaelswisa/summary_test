from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from loading_additional_data_source_service.database_postgres import Base


class AttackType(Base):
    __tablename__ = 'attack_types'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=True, unique=True)

    events = relationship('Event', back_populates='attack_type')