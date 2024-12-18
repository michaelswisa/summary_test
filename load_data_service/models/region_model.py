from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship


class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)

    countries = relationship('Country', back_populates='region')
