from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from load_data_service.database_postgres import Base


class Casualties(Base):
    __tablename__ = 'casualties'
    id = Column(Integer, primary_key=True, autoincrement=True)
    killed = Column(Integer, default=0)
    wounded = Column(Integer, default=0)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False)

    event = relationship('Event', back_populates='casualties')
