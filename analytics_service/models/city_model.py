from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from analytics_service.database_postgres import Base


class City(Base):
    __tablename__ = 'cities'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    country_id = Column(Integer, ForeignKey('countries.id'), nullable=False)

    country = relationship('Country', back_populates='cities')
    events = relationship('Event', back_populates='city')