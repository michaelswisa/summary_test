from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)

    region = relationship('Region', back_populates='countries')
    cities = relationship('City', back_populates='country')