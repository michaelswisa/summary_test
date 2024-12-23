from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from loading_additional_data_source_service.database_postgres import Base


class Region(Base):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String, nullable=False, unique=True)

    countries = relationship('Country', back_populates='region')
