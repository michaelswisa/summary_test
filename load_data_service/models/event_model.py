from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from load_data_service.database_postgres import Base


class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    summary = Column(String, nullable=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=True)
    attack_type_id = Column(Integer, ForeignKey('attack_types.id'), nullable=True)
    target_type_id = Column(Integer, ForeignKey('target_types.id'), nullable=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=True)

    casualties = relationship('Casualties', back_populates='event', uselist=False)
    group = relationship('Group', back_populates='events')
    attack_type = relationship('AttackType', back_populates='events')
    target_type = relationship('TargetType', back_populates='events')
    city = relationship('City', back_populates='events')